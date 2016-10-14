'''
Created on 8.9.2010

@author: kamil.rezac
'''
from net.krezac.robot.irena.datasource.DataInterface import DataInterface
import csv
import sys

# 2010-09-04_12-18-16_irena
# 2010-09-04_12-34-40_irena 

class LogDataSource(DataInterface):
    '''
    classdocs
    '''    
    def __init__(self, logRoot):
        '''
        Constructor
        '''
        self.logRoot = logRoot
        # robbus stuff
        robbusLogName = logRoot + "/robbus.rbl"
        print "Opening log file for read:", robbusLogName
        log = open(robbusLogName, "rb")
        self.robbusLogData = log.read()
        self.robbusLogDataPosition = 0
        log.close()
        
        # laser stuff
        laserLogName = logRoot + "/laser.csv"
        laserFile = open(laserLogName, "rb")
        laserReader = csv.reader(laserFile)
        self.laserData = []
        for csvRow in laserReader:
            dataRow = []
            for item in csvRow:
                if item != "":
                    dataRow.append(float(item))
            print len(dataRow)
            assert len(dataRow) == 181
            self.laserData.append(dataRow)
        laserFile.close()
        self.laserIndex = 0
        
        # imu stuff
        imuLogName = logRoot + "/imu.txt"
        imuFile = open(imuLogName, "rt")
        imuRows = imuFile.readlines()
        self.imuData = []
        for row in imuRows:
            self.imuData.append([float(i) for i in row.split(",")])
        imuFile.close()
        self.imuIndex = 0

        
        # camera stuff (note negative start indices - to have 0 as first index
        self.lastVisiblePictureIndex = -1
        self.lastIrPictureIndex = -1        
        self.lastVisiblePicturePath = None
        self.lastIrPicturePath = None
        
        self.laserCalled = True
        self.imuCalled = True
        
    def writeRobbusByte(self, b):
        self.laserCalled = False
        self.imuCalled = False
        if len(self.robbusLogData) <= self.robbusLogDataPosition:
            return
        if self.robbusLogData[self.robbusLogDataPosition] != "\x00":
            print "bad control byte in write, position", self.robbusLogDataPosition
            sys.exit()
        self.robbusLogDataPosition += 1
        if self.robbusLogData[self.robbusLogDataPosition] != b:
            print "bad data byte in write, position", self.robbusLogDataPosition, "logged", ord(self.robbusLogData[self.robbusLogDataPosition]), "written", ord(b)
            sys.exit()
        self.robbusLogDataPosition +=1
        
    def readRobbusByte(self):
        if len(self.robbusLogData) <= self.robbusLogDataPosition:
            return None
        if self.robbusLogData[self.robbusLogDataPosition] == "\x01":
            ret = self.robbusLogData[self.robbusLogDataPosition + 1]
            self.robbusLogDataPosition += 2
            return ret
        elif self.robbusLogData[self.robbusLogDataPosition] == "\x02":
            self.robbusLogDataPosition += 2
            return None
        else:
            print "bad control byte in read, position", self.robbusLogDataPosition
            sys.exit()        
        
    def getVisiblePicture(self):
        self.lastVisiblePictureIndex += 1
        # slow down vith sleep
        #time.sleep(0.1)
    
    def getIrPicture(self):
        self.lastIrPictureIndex += 1
    
    def getLastVisiblePicturePath(self):
        return self.logRoot + "/cam_vis/" + "%06d.jpg" % (self.lastVisiblePictureIndex)

    def getLastIrPicturePath(self):
        return self.logRoot + "/cam_ir/" + "%06d.jpg" % (self.lastIrPictureIndex)
        
    def getLaserData(self):
        if self.laserCalled:
            assert(False) # laser called twice, data will be shifted
        
        self.laserCalled = True
        if self.laserIndex >= len (self.laserData):
            return None
        data = self.laserData[self.laserIndex]
        self.laserIndex += 1
        return data

    def getIMUData(self):
        if self.imuCalled:
            assert(False) # imu called twice, data will be shifted
        
        self.imuCalled = True
        if self.imuIndex >= len (self.imuData):
            return None
        data = self.imuData[self.imuIndex]
        self.imuIndex += 1
        print "IMU", self.imuIndex, "of", len(self.imuData)
        return data