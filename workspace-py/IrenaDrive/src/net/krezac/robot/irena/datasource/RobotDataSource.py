'''
Created on 8.9.2010

@author: kamil.rezac
'''
from net.krezac.robot.irena.robbus.LoggedSerial import LoggedSerial
import os
import datetime
from net.krezac.robot.irena.laser.LoggedLaser import LoggedLaser
from net.krezac.robot.irena.imu.LoggedIMU import LoggedIMU
#from net.krezac.robot.irena.camera.LoggedCamera import LoggedCamera

class RobotDataSource(object):
    '''
    abstract parent for real and logged data source
    '''


    def __init__(self, logBaseDirectory = 'logs'):
        '''
        Constructor
        '''
        # log directory
        self.logRoot = logBaseDirectory
        now = datetime.datetime.today()
        logDirName = "%s/%s_irena" % (logBaseDirectory, now.strftime("%Y-%m-%d_%H-%M-%S"))
        if not os.path.exists(logDirName):
            os.makedirs(logDirName)
        # robbus log 
        robbusLogName = "%s/robbus.rbl" % (logDirName)
        self.robbusLog = open(robbusLogName, 'wb')
        
        # laser log
        laserRawLogName = "%s/laser_raw.csv" % (logDirName)
        self.laserRawLogFile = open(laserRawLogName, 'wb')
                    
        laserLogName = "%s/laser.csv" % (logDirName)
        self.laserLogFile = open(laserLogName, 'wb')
                    
        self.laser = LoggedLaser("/dev/lidar", 115200, self.laserRawLogFile)
        self.laser.start()
        
        # imu log
        imuRawLogName = "%s/imu_raw.txt" % (logDirName)
        self.imuRawLogFile = open(imuRawLogName, 'wt')
        
        imuLogName = "%s/imu.txt" % (logDirName)
        self.imuLogFile = open(imuLogName, 'wt')
                    
        self.imu = LoggedIMU("/dev/vectornav", 115200, self.imuRawLogFile)
        self.imu.start()

        
        #self.camera = LoggedCamera(logDirName)
        #self.camera.start()
        
        self.loggedSerial = LoggedSerial('/dev/robbus', 115200, False, self.robbusLog)
        
        
    def close(self):
        ''' close the data source '''
        self.loggedSerial.close()
        self.robbusLog.close()
        #self.laser.requestStop()
        #self.laserLogFile.close()
        #/self.laser.join(1)
        #self.camera.requestStop()
        #self.camera.join(1)
        self.imu.requestStop()
        self.imu.join(1)
        self.imuRawLogFile.close()
        self.imuLogFile.close()
        
    def writeRobbusByte(self, b):
        self.loggedSerial.writeByte(b)
    
    def readRobbusByte(self):
        return self.loggedSerial.readByte()
    
    def getVisiblePicture(self):
        return None #self.camera.captureVis()
    
    def getIrPicture(self):
        return None
        #return self.camera.captureIr()
    
    def getLastVisiblePicturePath(self):
        return None #self.camera.getLastVisiblePicturePath()
        
    def getLastIrPicturePath(self):
        return None #self.camera.getLastIrPicturePath()
    
    def getIMUData(self):
        data = self.imu.getData()
        self.imuLogFile.write(data + "\n")
        return [float(i) for i in data.split(",")]

    def getLaserData(self):
        data = self.laser.getDistanceData()
        dstr = ""
        for i in data:
            dstr += str(i)
            dstr += ","
        self.laserLogFile.write(dstr + "\n")
        return data
        