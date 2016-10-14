'''
Created on 20.2.2010

@author: Kamil.Rezac
'''
from net.krezac.robot import RoboUtils
import re

class MissionHolder(object):
    '''
    classdocs
    '''

    def loadMission(self, fileName):
        f = open(fileName, 'r')
        for line in f:
            point = map(float, re.findall(r'[\w\.]+', line))
            self.missionPoints.append(point)
        print self.missionPoints
        
        ((self.minX, self.minY), (self.maxX, self.maxY)) = RoboUtils.getBoundaryBox(self.missionPoints, 5)

    def loadMissionRK(self, fileName):
        f = open(fileName, 'r')
        polarCoords = []
        for line in f:
            print line
            parts = re.findall(r'[\w\.]+', line)
            print parts
            rawLat = float(parts[-2])
            rawLon = float(parts[-1])
            print rawLat, rawLon
            #gga = GPGGAParser(sentence)
            self.missionPoints.append(RoboUtils.deg2xy((rawLat, rawLon)))
            #latCen += gga.latitude
            #lonCen += gga.longitude
        f.close()

        print self.missionPoints
        
        ((self.minX, self.minY), (self.maxX, self.maxY)) = RoboUtils.getBoundaryBox(self.missionPoints, 5)
                
        
    def getMissionPoints(self):
        return self.missionPoints

    def getBoundaryBoxMin(self):            
            return [self.minX, self.minY]

    def getBoundaryBoxMax(self):            
            return [self.maxX, self.maxY]
    

    def __init__(self):
        self.missionPoints = []
        '''
        Constructor
        '''
        self.minX = 999999999999.9
        self.minY = 999999999999.9
        self.maxX = -999999999999.9
        self.maxY = -999999999999.9
        