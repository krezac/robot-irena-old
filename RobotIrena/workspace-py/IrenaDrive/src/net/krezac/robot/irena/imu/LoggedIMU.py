#!/usr/bin/python
"""
  Laser SICK LMS100-10000
    autodetection: 192.168.1.1, ports 2111 (aux) and 2112 (host)
  usage:
      laser.py <number of scans>
"""

import socket
import serial
from threading import Thread,Event,Lock
import csv

HOST = '192.168.2.1'    # The remote host
PORT = 2111             # The same port as used by the server

STX = chr(2)
ETX = chr(3)

class LoggedIMU( Thread ):
    def __init__( self, port, baudrate, logFile ):
        Thread.__init__(self) 
        self.imuSerial = serial.Serial(port, baudrate, timeout=0.25)
        self.setDaemon(True)
        self.lock = Lock()
        self.shouldIRun = Event()
        self.shouldIRun.set()
        self._lastData = "0,0,0,0,0,0,0,0,0" 
        self.stopOnExit = False        
        self.logFile = logFile        

    # THREAD code
    def run(self):
        while self.shouldIRun.isSet():
            serdata = self.imuSerial.readline()
            if serdata.startswith("$VNYMR,"):
                s = 0
                for i in serdata[1:-5]: # payload - no $, no *xy
                    s ^= ord(i)
                if s == int(serdata[-4:], 16):
                    self._lastData = serdata[7:-5]
                    self.logFile.write(serdata)
 
    def requestStop(self):
        self.shouldIRun.clear()
    
    def getData(self):
        return self._lastData
