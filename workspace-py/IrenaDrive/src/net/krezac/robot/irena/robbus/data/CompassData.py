'''
Created on 19.2.2010

@author: Kamil.Rezac
'''

import struct
from net.krezac.robot.irena.robbus.data.RobbusData import RobbusData
import math
from net.krezac.robot.irena.gps.NmeaReader import NmeaReader

class CompassData(RobbusData):
    '''
    classdocs
    '''


    def __init__(self):
        RobbusData.__init__(self, 'c', 
                            ">B", ("nothing",), "",
                            ">BHIIB", ("timestamp", "azimuth", "latitude", "longitude", "dop"), "")
        self.gpsDataValid = False
        self.commandByte = 0        
        self.azimuth = 0
        self.hdop = 0
        self.gpsPosition = (0,0)
        self.nmeaReader = NmeaReader()
    
    def getRequestData(self):
        return self.requestDataStruct.pack(self.commandByte)
        
        
    def setResponseData(self, data):
        if data is None:
            return None
        # parse the response structure
        rawTimestamp, rawAzimuth, rawLatitude, rawLongitude, rawHdop = self.responseDataStruct.unpack(data)
        # and update fields
        self.updateTimestamp(rawTimestamp)
        if rawAzimuth > 1800:
            rawAzimuth -= 3600        
        self.azimuth = (rawAzimuth)/1800.0 * math.pi
        #print "xxxxxxxxxxxxxxxxx", rawLatitude, rawLongitude
        if rawLatitude == 2147483647 and rawLongitude ==2147483647:
            self.gpsPosition = (0,0)
            self.gpsDataValid = False
        else:
            latDeg = long(rawLatitude / 1000000)
            latMin = long(rawLatitude % 1000000) /10000.0 / 60.0
            lonDeg = long(rawLongitude / 1000000)
            lonMin = long(rawLongitude % 1000000) /10000.0 / 60.0
            lat =  latDeg + latMin
            lon = lonDeg + lonMin
            self.gpsPosition = self.nmeaReader.rad2xy(self.nmeaReader.deg2rad((lat, lon)))
            print self.gpsPosition
            self.gpsDataValid = True
        
    def getAzimuth(self):
        return self.azimuth
