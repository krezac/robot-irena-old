'''
Created on 19.2.2010

@author: Kamil.Rezac
'''

import struct
from net.krezac.robot.irena.robbus.data.RobbusData import RobbusData
import math

class HeadDataOld(RobbusData):
    '''
    classdocs
    '''


    def __init__(self):
        RobbusData.__init__(self, 'h', 
                            ">BBB", ("watchdog", "servoA", "servoB"), "",
                            ">BBHHB", ("timestamp", "status", "leftSonar", "rightSonar", "vSer"), "")
        self.watchdog = 0        
        self.servoA = 128
        self.servoB = 128
        self.status = 0
        self.leftSonar = 0
        self.rightSonar = 0
        self.vser = 0
        
    def convertVoltage(self, vin):
        return vin / 10.0
    
    def convertCurrent(self, ain):
        return ain / 10.0
    
    def voltageToPercent(self, v):
        return (int)((v-3*3)/(3*4.2-3*3)*100)
        
    def getRequestData(self):
        return self.requestDataStruct.pack(self.watchdog, self.servoA, self.servoB)
        
        
    def setResponseData(self, data):
        if data is None:
            return None
        # parse the response structured_arrays
        rawTimestamp, rawStatus, rawLeftSonar, rawRightSonar, rawVser = self.responseDataStruct.unpack(data)
        # and update fields
        self.updateTimestamp(rawTimestamp)
        self.status = rawStatus
        self.leftSonar = rawLeftSonar / 100.0
        self.rightSonar = rawRightSonar / 100.0
        self.vser = self.convertVoltage(rawVser)
                
    def getSonarLeft(self):
        return self.leftSonar
    
    def getSonarRight(self):
        return self.rightSonar
