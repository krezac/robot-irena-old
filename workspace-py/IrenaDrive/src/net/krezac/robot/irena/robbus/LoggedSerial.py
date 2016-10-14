'''
Created on 27.2.2010

@author: Kamil.Rezac
'''
import serial

class LoggedSerial():
    def __init__(self, port, baudrate, consumeEcho, logFile):
        self.robbusSerial = serial.Serial(port, baudrate, timeout=0.25)
        # open log file
        self.logFile = logFile
        self.consumeEcho = consumeEcho
        
    def close(self):
        self.robbusSerial.close()
        
    def writeByte(self, b):
        # write to serial
        self.robbusSerial.write(b)
        # and log
        self.logFile.write("\x00")
        self.logFile.write(b)
        
        if self.consumeEcho:
            self.robbusSerial.read(1)
        
    def readByte(self):
        b = self.robbusSerial.read(1)
        if b is None or len(b) == 0:
            self.logFile.write("\x02")
            self.logFile.write("\xFF")
            return None
        self.logFile.write("\x01")
        self.logFile.write(b)
        return b
        
 