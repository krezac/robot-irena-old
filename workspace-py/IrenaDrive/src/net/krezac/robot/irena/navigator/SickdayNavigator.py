'''
Created on May 20, 2010

@author: krezac
@author: jisa
'''
import math

from net.krezac.planner.vfh import VFH
from net.krezac.robot.irena.navigator.NavigatorInterface import NavigatorInterface
from net.krezac.robot import RoboUtils
from net.krezac.robot.irena.main import CarConfig
import pygame

class SickdayNavigator(NavigatorInterface):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.reset()
    
    def update(self, car):
        SPEED = CarConfig.CAR_SPEED # [m/s]
        CLOSE_OBSTACLE_THRESHOLD = 0.2 # [m]

        car.setPowerEnabled(True)
        scan = list(car.laserData)
        #scan.reverse().reverse() One revert comes to get left-to-right orientation of the data, the other because the laser is upside-down.
        self.vfh.update(scan)

        goalDir = math.radians(-45) # stick to the wall on the left

        dir = self.vfh.navigate(goalDir, self.prevDir)
        closeObstacle = False #any( x < CLOSE_OBSTACLE_THRESHOLD for x in [car.getObstacleLeft(), car.getObstacleRight()] )
        A_THRESH = 8.0
        if car.tractorData.amot > A_THRESH:
            self.overCurrent += 1
        else:
            self.overCurrent = 0
        OVERCURRENT_THRESH = 4
        if dir is None or closeObstacle or self.overCurrent >= OVERCURRENT_THRESH:
            print "!!! ---", car.tractorData.amot, min(x for x in scan if x > 0)
            car.setSpeed(0)
            self.overCurrent = 0
            return NavigatorInterface.STATE_CHANGE_NONE if scan is None or not scan else NavigatorInterface.STATE_CHANGE_RETREAT
        else:
            print "!!!", math.degrees(dir)
            car.setSteerAngle(dir)
            car.setSpeed(SPEED)
            self.prevDir = dir
            return NavigatorInterface.STATE_CHANGE_NONE
        
    def reset(self):
        #self.vfh = VFH(maxRange = 1.1, safetyDistance = 0.3, blockingDistance = 0.20, turnRadius = None, verbose = True)
        self.vfh = VFH(maxRange = 1.2, safetyDistance = 0.40, blockingDistance = 0.32, turnRadius = None, verbose = True)
        self.prevDir = 0.0
        self.overCurrent = 0
        
    def processEvent(self, event, viewPort):
        NavigatorInterface.processEvent(self, event, viewPort)
    
    def drawNavigatorData(self, viewPort):
        font = pygame.font.Font(None, 32)    
        #ren = font.render("Sickday {0}".format(0), 0, pygame.Color('black'))
        ren = font.render("Sickday %d" % 0, 0, pygame.Color('black'))
        viewPort.screen.blit(ren, (30, 30))

