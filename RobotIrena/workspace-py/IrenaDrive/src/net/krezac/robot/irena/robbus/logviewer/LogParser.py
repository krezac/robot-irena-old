'''
Created on May 22, 2010

@author: krezac
'''
import sys
from net.krezac.robot.irena.robbus.data.TractorData import TractorData
from net.krezac.robot.irena.robbus.data.HeadData import HeadData
from net.krezac.robot.irena.robbus.data.CompassData import CompassData
import csv
import os

class LogParser(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''        
        self.tractorData = TractorData()
        self.headData = HeadData()
        self.compassData = CompassData()
        
        self.nodes = {self.compassData.address:self.compassData, 
                      self.headData.address:self.headData, 
                      self.tractorData.address:self.tractorData}
        self.requests = {}
        self.responses = {}
        self.processedAddress = None
        self.timeoutCount = 0
        self.badLogTagCount = 0
        self.badPacketTagCount = 0
        self.badAddressCount = 0
        self.badSumCount = 0
        self.badStripCount = 0

    def parse(self, logName):
        self.timeoutCount = 0
        inLogFile = open(logName, "rb")
        inData = inLogFile.read()
        inLogFile.close()
        # new code start
        inPos = 0
        currentBlock = 0
        block = []
        
        while inPos < len(inData):
            tag  = ord(inData[inPos])
            dataByte = inData[inPos + 1]
            inPos += 2
            if tag == currentBlock:
                block.append(dataByte)
                continue
            if currentBlock == 0 or currentBlock == 1:
                self.processBlock(currentBlock, self.dewrap(block))
            elif currentBlock == 2: # timeout
                self.timeoutCount += 1
                try: 
                    commandResponses = self.responses[self.processedAddress]
                except KeyError:
                    commandResponses = []
                    self.responses[self.processedAddress] = commandResponses
                commandResponses.append(None)
            else:
                print "bad tag"
                sys.exit()
            currentBlock = tag
            block = []
            block.append(dataByte)
            
        # process what remains in buffer
        #self.processBlock(currentBlock, self.dewrap(block))
        # new code end
        
        
    def processBlock(self, blockTag, data):
        #print blockTag, len(data), ord(data[2]), (len(data) - 4)
        #print data
        if ord(data[2]) != (len(data) - 4): # patch pro stare logy, ktere nemaji timeout
                print "In multiBlock"
                sys.exit()
        self.processPacket(blockTag, data)
    
    def calculateSum(self, data):
        data = data[1:]
        sum=0
        for b in data:
            sum += ord(b)
        return sum

    def processPacket(self, tag, data):
        if ord(data[0]) != 2:
            self.badPacketTagCount += 1
            print "Bad packet head tag"
            return
        address = data[1]
        if ord(address) > 127:
            if tag == 1:
                address = chr(ord(address) - 128) # correct the address for reply
            else:
                self.badAddressCount += 1
                print "Bad tag/address combination", tag, ord(address)
                return
        payloadLength = ord(data[2])
        if ord(data[2]) != (len(data) - 4):
            print "Bad length"
            return
        if self.calculateSum(data)%256 != 0:
            self.badSumCount += 1
            print "Bad sum" 
            return
        #strip payload
        data = data[3:-1]
        if len(data) != payloadLength:
            self.badStripCount += 1
            print "Bad strip (should never happen)", len(data), payloadLength
            return
        
        if tag == 0:
            #request
            try: 
                commandRequests = self.requests[address]
            except KeyError:
                commandRequests = []
                self.requests[address] = commandRequests
            strdata = ""
            for b in data:
                strdata += b
            #print ">", address
            commandRequests.append(self.nodes[address].parseRequest(strdata))
            self.processedAddress = address
        elif tag == 1:
            #response
            try: 
                commandResponses = self.responses[address]
            except KeyError:
                commandResponses = []
                self.responses[address] = commandResponses
            strdata = ""
            for b in data:
                strdata += b
            #print "<", address
            commandResponses.append(self.nodes[address].parseResponse(strdata))
        else:
            self.badLogTagCount += 1
            print "invalid log tag", ord(tag)
            return
            
    
    def dewrap(self, data):
        #for b in data:
        #    print ord(b)
        consume = False
        ret = []
        for b in data:
            if consume:
                consume = False
                ret.append(chr(ord(b) - 4))
            else:
                if ord(b) == 0:
                    consume = True
                else:
                    ret.append(b)
        #print "Dewrapped len", len(ret)
        #for b in ret:
        #    print ord(b)
        return ret

    def describeParsedData(self):
        for reqKey in self.requests.keys():
            # write requests
            data = self.requests[reqKey]
            print "Requests for ", reqKey, len(data)
            # and responses            
        for rspKey in self.responses.keys():
            data = self.responses[rspKey]
            print "Responses for ", rspKey, len(data)
    
    def writeParsedData(self, dirName):
        if not os.path.exists(dirName):
            os.makedirs(dirName)
        for reqKey in self.requests.keys():
            # write requests
            data = self.requests[reqKey]
            csvfile = open(dirName + "/"+reqKey+"_req.csv","wb")
            csvwriter = csv.writer(csvfile)
            header = self.nodes[reqKey].requestDescription
            csvwriter.writerow(header)
            csvwriter.writerows(data)
            csvfile.close()
            # and responses            
        for rspKey in self.responses.keys():
            data = self.responses[rspKey]
            csvfile = open(dirName + "/"+rspKey+"_rsp.csv","wb")
            csvwriter = csv.writer(csvfile)
            header = self.nodes[rspKey].responseDescription
            emptyRow = []
            for i in range(0, len(header)):
                emptyRow.append(None)
            csvwriter.writerow(header)
            for line in data:
                if line is not None:
                    csvwriter.writerow(line)
                else:
                    csvwriter.writerow(emptyRow)
            csvfile.close()            
        pass
    
    def writeParsedDataOneFile(self, csvName):
        csvfile = open(csvName,"wb")
        csvwriter = csv.writer(csvfile)
        bigHeader = []
        commonLength = None
        keys = self.requests.keys()
        requestEmptyRows = {}
        responseEmptyRows = {}
        # generate header and emptyRows
        for reqKey in keys:
            if commonLength is None:
                commonLength = len(self.requests[reqKey])
            if commonLength != len(self.requests[reqKey]):
                print "Request data len differs for key", reqKey,len(self.requests[reqKey]), "insead of", commonLength 
            if commonLength != len(self.responses[reqKey]):
                print "Response data len differs for key", reqKey,len(self.responses[reqKey]), "insead of", commonLength
            header = self.nodes[reqKey].requestDescription
            emptyRow = []
            for item in header:
                bigHeader.append("q"+reqKey+"_"+item)
                emptyRow.append(None)
            requestEmptyRows[reqKey] = emptyRow
            
            header = self.nodes[reqKey].responseDescription
            emptyRow = []
            for item in header:
                bigHeader.append("r"+reqKey+"_"+item)
                emptyRow.append(None)
            responseEmptyRows[reqKey] = emptyRow
            
                
        print bigHeader
        csvwriter.writerow(bigHeader)
        
        print "req count", len(self.requests[keys[0]])
        for i in range(0, len(self.requests[keys[0]])):
            bigLine = []
            for key in keys:
                if self.requests[key][i] is not None:
                    bigLine.extend(self.requests[key][i])
                else:
                    bigLine.extend(requestEmptyRows[key])
                    
                if self.responses[key][i] is not None:
                    bigLine.extend(self.responses[key][i])
                else:
                    bigLine.extend(responseEmptyRows[key])
            csvwriter.writerow(bigLine)
        
        csvfile.close()
        

if __name__ == '__main__':
    #logDirName = sys.argv[1]
    #for fileName in os.listdir(logDirName):
        #logName = os.path.join(logDirName, fileName)
        #logName = "logs/2012-03-27_21-29-19_irena_outwait/robbus.rbl" #sys.argv[1]
        #logName = "logs/2012-03-27_21-51-08_irena_azinor/robbus.rbl" #done
        #logName = "logs/2012-03-27_21-52-45_irena_azisou/robbus.rbl"
        #logName = "logs/2012-03-27_21-54-00_irena_joyhome/robbus.rbl"
        #logName = "logs/2012-03-27_21-50-22_irena/robbus.rbl"
        #logName = "logs/2012-03-27_21-49-07_irena/robbus.rbl"
        #logName = "logs/2012-03-27_21-46-55_irena/robbus.rbl"
        #logName = "logs/2012-03-27_21-45-31_irena/robbus.rbl"
        #logName = "logs/2012-03-27_21-42-26_irena_joyaround/robbus.rbl"
        #logName = "logs/2012-03-27_21-41-18_irena_joynor/robbus.rbl"
        #logName = "logs/2012-03-27_21-39-33_irena_joysou/robbus.rbl"
        logName = "logs/2012-03-27_21-29-19_irena_outwait/robbus.rbl"
        
        if os.path.isfile(logName):
            print "Parsing", logName
            x = LogParser()
            x.parse(logName)
            x.describeParsedData()
            #csvName = logName.replace(".rbl", ".csv", -1)
            csvName = logName.rsplit(".rbl", 1)[0] + ".csv"
            print csvName
            #x.writeParsedData(dirName)
            x.writeParsedDataOneFile(csvName)
            print "Timeouts:", x.timeoutCount
            print "Bad log tags:", x.badLogTagCount
            print "Bad packet tags:", x.badPacketTagCount
            print "Bad addresses:", x.badAddressCount
            print "Bad sums:", x.badSumCount
            print "Bad strips:", x.badStripCount
