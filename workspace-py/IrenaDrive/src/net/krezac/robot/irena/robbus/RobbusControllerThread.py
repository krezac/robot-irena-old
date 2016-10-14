'''
Created on 19.2.2010

@author: Kamil.Rezac
'''

import threading

class RobbusControllerThread(threading.Thread):
    '''
    classdocs
    '''


    def __init__(self, dataSource):        
        '''
        Constructor
        '''
        self.dataSource = dataSource
        self.nodeList = []
        self.initialized = True # TODO
        #try:
        #    threading.Thread.__init__(self, None, None, "RobbusControllerThread")
        #    self.terminationRequested = False
        #   
        #    #if logName is not None:
        #    #    self.serial = ReplaySerial(logName)
        #    #else:        
        #    self.serial = LoggedSerial('/dev/robbus', 115200, False, dataSource)
        #    self.initialized = True
        #    print "Serial opened"
        #except serial.SerialException:
        #    self.initialized = False
        #except serial.serialutil.SerialException:
        #    self.initialized = False
            

    def requestTermination(self):
        self.terminationRequested = True
        
    def registerNode(self, node):
        self.nodeList.append(node)
        
    def sendWrapped(self, c, sum):
        if ord(c) < 4:
            self.dataSource.writeRobbusByte("\x00")
            #print ">", x, ord(x)
            d = chr(ord(c)+4)
            self.dataSource.writeRobbusByte(d)
            #print ">", x, ord(x)
        else:
            self.dataSource.writeRobbusByte(c)
            #print ">", x, ord(x)
        return sum+ord(c)
    
    def receiveWrapped(self):
        x = self.dataSource.readRobbusByte()
        #print "<", x, ord(x)
        if ord(x) == 0:
            x = self.dataSource.readRobbusByte()    
            #print "<", x, ord(x)
            return chr(ord(x)-4)
        else:
            return x

    def sendMessage(self,alias,data):
        sum = 0;
        self.dataSource.writeRobbusByte("\x02")     #write regular packet start
        sum = self.sendWrapped(alias,sum) 
        #print sum
        sum = self.sendWrapped(chr(len(data)),sum)
        for c in data:
            sum = self.sendWrapped(c,sum)    
            #print sum
        outSum = (256-(sum % 256)) % 256
        self.sendWrapped(chr(outSum),sum)

    # read reply
    def receiveReply(self):
        # consume outgoing message
        s = ""
        # and read incoming
        #print "Receiving data..."
        x = self.dataSource.readRobbusByte() # head, no need to dewrap
        if x is None:
            return None
        s += x
        #print "<", x, ord(x)
        x = self.dataSource.readRobbusByte() # head, no need to dewrap
        if x is None:
            return None
        s += x
        #print "<", x, ord(x)
        lenstr = self.receiveWrapped()
        if lenstr is None:
            return None
        paylen = ord(lenstr);
        s += lenstr
        while paylen > 0:
            x = self.receiveWrapped();
            if x is None:
                return None
            s += x
            paylen = paylen-1
        s += self.receiveWrapped() #chsum
        return s
    
    def parseReply(self, s):
        if s is None:
            return None
        if len(s) < 3:
            raise Exception("Input too short")
        s = s [1:] # cut head
        chSum = sum([ord(c) for c in s]) 
        if sum([ord(c) for c in s]) % 256 != 0:
            raise Exception("Invalid checksum")
        address = chr(ord(s[0]) - 128)
        #print "Reply from:", address, " hex:", address.encode("hex")
        replySize = ord(s[1])
        #print "      size:", replySize
        if replySize != len (s[2:-1]):
            raise Exception("Data size doesn't match real data length")
        data = s[2:-1]
        #print "      data:", [ord(i) for i in data], " hex:", data.encode("hex")
        return data
    
    
        
    def communicateNode(self, node):
        self.sendMessage(node.getAddress(), node.getRequestData())
        reply = self.receiveReply()
        node.setResponseData(self.parseReply(reply))
        
    def synchronizeBus(self):
        if not self.initialized:
            print "Init failed, no run"
            return
        for node in self.nodeList:
            #print "Processing node", node.getAddress()
            #try:
            self.communicateNode(node)
            #except Exception:
            #    pass            
        
        
    def run(self):
        raise NotImplementedError("Not to be used asynchronously yet ;)")
        if not self.initialized:
            print "Init failed, no run"
            return
        print "Robbus controller started"
        while True:
            if self.terminationRequested:
                break
            for node in self.nodeList:
                #print "Processing node", node.getAddress()
                self.communicateNode(node)            
        print "Robbus thread will terminate"
        self.serial.close()            
        print "Robbus controller terminated"