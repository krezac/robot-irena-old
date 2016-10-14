'''
Created on 19.2.2010

@author: Kamil.Rezac
'''

import struct
from net.krezac.robot.irena.robbus.data.RobbusData import RobbusData
import math

class TractorData(RobbusData):
    '''
    classdocs
    '''


    def __init__(self):
        RobbusData.__init__(self, 't', 
                            ">BBBB", ("watchdog", "flags", "servoA", "servoB"), "", 
                            ">BBHHBBB", ("timestamp", "status", "odometry", "rearSonar", "vLog", "vMot", "aMot"), "")
        self.watchdog = 255        
        self.flags = 0x02 # 1 - enable motors, 2 - enable rear sonar
        self.servoA = 128
        self.servoB = 128
        self.status = 0
        self.lastOdometry = None
        self.lastDistance = 0
        self.totalDistance = 0
        self.rearSonar = 0
        self.vlog = 0
        self.vmot = 0
        self.amot = 0
        
    def enableMotor(self, enabled):
        if enabled:
            self.flags |= 0x01
        else:
            self.flags &= 0xfe
        
    def convertVoltage(self, vin):
        return vin / 10.0
    
    def convertCurrent(self, ain):
        return ain / 10.0
    
    #returns tents of percent
    def voltageToPercent(self, v):
        return (int)((v-3*3)/(3*4.2-3*3)*10)

    def convertOdometry(self, ticks):
        '''
        on motor 256 ticks per revolution
        belt 2:1
        gears 7.68:1
        wheel dia 0.14m
        thus 1 wheel revolution (0.14*pi) equals 256*2*7.68 ticks
        i.e. 1 tick is (0.14*pi)/(256*2*7.68) [meter] 
        Conversion ratio 0.000111852765783m/tick = 8940.3243004ticks/m
        '''
        #print "Conversion ratio", (0.14 * math.pi) / (256.0*2.0*7.68), (256.0*2.0*7.68) / (0.14 * math.pi)
        return ticks * (0.14 * math.pi) / (256.0*2.0*7.68)
    
    #returns tents of percent
    def voltageToPercentNiMH(self, v):
        return (int)((v-0.9*4)/(1.6*4-0.9*4)*10)
    
    def updateOdometry(self, rawOdometry):
        if self.lastOdometry is None:
            self.lastOdometry = rawOdometry
            self.lastDistance = 0
            self.totalDistance  = 0
        else:
            #print "Raw odometry", rawOdometry
            odometryRawDif = rawOdometry - self.lastOdometry
            #print "Raw odo dif", odometryRawDif
            odometryDif = 0
            if odometryRawDif > 0 and odometryRawDif < 32767: # forward, no overflow
                #print "forward, no overflow"
                odometryDif = odometryRawDif
            elif odometryRawDif < 0 and odometryRawDif > -32767: # backward, no overflow
                #print "backward, no overflow"
                odometryDif = odometryRawDif
            elif  odometryRawDif > 0 and odometryRawDif > 32767: # backward, overflow
                #print "backward, overflow"
                odometryDif = odometryRawDif - 65536
            elif  odometryRawDif < 0 and odometryRawDif < -32767: # forward overflow
                #print "forward, overflow"
                odometryDif = 65536 + odometryRawDif
                
            #print "real odometry diff", odometryDif
            self.lastDistance = self.convertOdometry(odometryDif)
            #print "real last dist", self.lastDistance
            self.totalDistance += self.lastDistance
            #print "real total dist", self.totalDistance
            self.lastOdometry = rawOdometry
            
            
    def getRequestData(self):
        return self.requestDataStruct.pack(self.watchdog, self.flags, self.servoA, self.servoB)
        
        
    def setResponseData(self, data):
        if data is None:
            return None
        # parse the response structure
        rawTimestamp, rawStatus, rawOdometry, rawRearSonar, rawVlog, rawVmot, rawAmot = self.responseDataStruct.unpack(data)
        # and update fields
        self.updateTimestamp(rawTimestamp)
        self.status = rawStatus
        self.updateOdometry(rawOdometry)
        self.rearSonar = rawRearSonar / 100.0
        self.vlog = self.convertVoltage(rawVlog)
        self.vmot = self.convertVoltage(rawVmot)
        self.amot = self.convertCurrent(rawAmot)
        #print "vlof", self.vlog, "vmot", self.vmot, "amot", self.amot
        
    def getSonarRear(self):
        return self.rearSonar       
