'''
Created on 27.2.2010

@author: Kamil.Rezac
'''
import sys
class ReplaySerial():
    def __init__(self, logName):
        print "Opening log file for write:", logName
        log = open(logName, "rb")
        self.data = log.read()
        self.dataPosition = 0
        log.close()
        
    def close(self):
        pass
        
    def writeByte(self, b):
        if len(self.data) <= self.dataPosition:
            return
        if self.data[self.dataPosition] != "\x00":
            print "bad control byte in write, position", self.dataPosition
            sys.exit()
        self.dataPosition += 1
        if self.data[self.dataPosition] != b:
            print "bad data byte in write, position", self.dataPosition, "logged", ord(self.data[self.dataPosition]), "written", ord(b)
            sys.exit()
        self.dataPosition +=1
        
    def readByte(self):
        if len(self.data) <= self.dataPosition:
            return None
        if self.data[self.dataPosition] == "\x01":
            ret = self.data[self.dataPosition + 1]
            self.dataPosition += 2
            return ret
        elif self.data[self.dataPosition] == "\x02":
            self.dataPosition += 2
            return None
        else:
            print "bad control byte in read, position", self.dataPosition
            sys.exit()
 