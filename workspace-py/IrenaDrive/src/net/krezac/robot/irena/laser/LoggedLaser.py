#!/usr/bin/python
# based on:
# XV-11 Lidar Test
# Copyright 2010 Nicolas "Xevel" Saugnier
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
#
"""
neato X11 lidar
"""
import serial
from threading import Thread,Event,Lock
import csv
import time
import sys
import traceback

class LoggedLaser( Thread ):
    def __init__( self, port, baudrate, logFile ):
        Thread.__init__(self) 
        self.laserSerial = serial.Serial(port, baudrate)
        self.setDaemon(True)
        self.lock = Lock()
        self.shouldIRun = Event()
        self.shouldIRun.set()
        self._speedRPM = 0
        self._distData = [10.0 for i in range(181)] 
        self._qualityData = [0 for i in range(181)] 
        self.stopOnExit = False        
        self.logFile = logFile   
        self._init_level = 0
        self._index = 0
        self._nb_errors = 0     

    # THREAD code
    def run(self):
        while self.shouldIRun.isSet():
            try:
                time.sleep(0.00001) # do not hog the processor power
    
                if self._init_level == 0 :
                    b = ord(self.laserSerial.read(1))
                    # start byte
                    if b == 0xFA : 
                        self._init_level = 1
                    else:
                        self._init_level = 0
                elif self._init_level == 1:
                    # position index 
                    b = ord(self.laserSerial.read(1))
                    if b >= 0xA0 and b <= 0xF9  : 
                        self._index = b - 0xA0
                        self._init_level = 2
                    elif b != 0xFA:
                        self._init_level = 0
                elif self._init_level == 2 :
                    # speed
                    b_speed = [ ord(b) for b in self.laserSerial.read(2)]
                    
                    # data
                    b_data0 = [ ord(b) for b in self.laserSerial.read(4)]
                    b_data1 = [ ord(b) for b in self.laserSerial.read(4)]
                    b_data2 = [ ord(b) for b in self.laserSerial.read(4)]
                    b_data3 = [ ord(b) for b in self.laserSerial.read(4)]
    
                    # for the checksum, we need all the data of the packet...
                    # this could be collected in a more elegent fashion... 
                    all_data = [ 0xFA, self._index+0xA0 ] + b_speed + b_data0 + b_data1 + b_data2 + b_data3 
    
                    # checksum  
                    b_checksum = [ ord(b) for b in self.laserSerial.read(2) ]
                    incoming_checksum = int(b_checksum[0]) + (int(b_checksum[1]) << 8)
    
                    # verify that the received checksum is equal to the one computed from the data
                    if self.checksum(all_data) == incoming_checksum:
                        self._speedRPM = float( b_speed[0] | (b_speed[1] << 8) ) / 64.0
    
                        self.updateAngle(self._index * 4 + 0, b_data0)
                        self.updateAngle(self._index * 4 + 1, b_data1)
                        self.updateAngle(self._index * 4 + 2, b_data2)
                        self.updateAngle(self._index * 4 + 3, b_data3)
                    else:
                        # the checksum does not match, something went wrong...
                        self._nb_errors +=1
                        print "lidar errors: "+str(self._nb_errors)
                        
                        # display the samples in an error state
                        #self.updateAngle(self._index * 4 + 0, [0, 0x80, 0, 0])
                        #self.updateAngle(self._index * 4 + 1, [0, 0x80, 0, 0])
                        #self.updateAngle(self._index * 4 + 2, [0, 0x80, 0, 0])
                        #elf.updateAngle(self._index * 4 + 3, [0, 0x80, 0, 0])
                        
                    self._init_level = 0 # reset and wait for the next packet
                    
                else: # default, should never happen...
                    self._init_level = 0
            except :
                pass
                #traceback.print_exc(file=sys.stdout)

 
    def requestStop(self):
        self.shouldIRun.clear()
    
    def getData(self):
        return self._lastData
    
    def checksum(self, data):
        """Compute and return the checksum as an int.
    
        data -- list of 20 bytes (as ints), in the order they arrived in.
        """
        # group the data by word, little-endian
        data_list = []
        for t in range(10):
            data_list.append( data[2*t] + (data[2*t+1]<<8) )
        
        # compute the checksum on 32 bits
        chk32 = 0
        for d in data_list:
            chk32 = (chk32 << 1) + d
    
        # return a value wrapped around on 15bits, and truncated to still fit into 15 bits
        checksum = (chk32 & 0x7FFF) + ( chk32 >> 15 ) # wrap around to fit into 15 bits
        checksum = checksum & 0x7FFF # truncate to 15 bits
        return int( checksum )
    
    def updateAngle( self, angle, data ):
        """Updates the view of a sample.
        Takes the angle (an int, from 0 to 359) and the list of four bytes of data in the order they arrived.
        """
        if angle <= 90:
            index = 90 - angle
        elif angle >= 270:
            index = 450 - angle
        else:
            return # data from rear hemisphere are ignored
        
        invalidData =  data[1] & 0x80 # note [1] & 0x40 means suspicious data (strength and distance don't match)
            
        #unpack data using the denomination used during the discussions
        self._distData[index] = 10.0 if invalidData else 0.001 * (data[0] | (( data[1] & 0x3f) << 8)) # distance is coded on 13 bits ? 14 bits ?, convert from mm to m
        self._qualityData[index] = 0 if invalidData else data[2] | (data[3] << 8) # quality is on 16 bits
        self.logFile.write(str(index) + "," + str(self._distData[index]) + "," + str(self._qualityData[index]) + "\n")

    def getDistanceData(self):
        return self._distData

    def getQualityData(self):
        return self._qualityData
