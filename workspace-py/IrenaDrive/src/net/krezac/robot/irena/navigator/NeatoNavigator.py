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
from net.krezac.robot.irena.main.MissionHolder import MissionHolder
import pygame
import time

class NeatoNavigator(NavigatorInterface):
    '''
    classdocs
    '''


    def __init__(self, fileName):
        '''
        Constructor
        '''
        self.missionFileName = fileName
        self.reset()
        self.firstCall = True
        self.missionStarted = True
    
    def update(self, car):
        SPEED = CarConfig.CAR_SPEED # [m/s]
        CLOSE_OBSTACLE_THRESHOLD = 0.2 # [m]
        
        if self.firstCall:
            self.firstCall = False
            car.setPosition(self.mission.getMissionPoints()[0])
        car.setPowerEnabled(True)
        
        if not self.missionStarted:
            print "not statrted"
            return NavigatorInterface.STATE_CHANGE_NONE
        
        targetDist = RoboUtils.getDistanceToPoint(car.getGpsPosition(), self.targetPoint)
        if targetDist < 2*car.CAR_LENGTH:            
            if self.activeIndex < (len(self.mission.getMissionPoints()) - 1):
                self.activeIndex += 1
                self.targetPoint = self.mission.getMissionPoints()[self.activeIndex]
            else:
                car.setSpeed(0)
                car.setPowerEnabled(False)
                print "Close enough, stopping: ", targetDist
                print "finished"
                return NavigatorInterface.STATE_CHANGE_FINISHED
        
        # full speed
        car.setSpeed(CarConfig.CAR_SPEED)
        
        # calculate angle to target
        #angleToTarget = RoboUtils.normalizeAngle(0.65 + 0*math.pi) #RoboUtils.getAngleToPoint(car.getGpsPosition(), self.targetPoint)
        angleToTarget = RoboUtils.normalizeAngle(RoboUtils.getAngleToPoint(car.getGpsPosition(), self.targetPoint))
        angleDelta = RoboUtils.normalizeAngle(angleToTarget - car.getAzimuth())
        #print angleDelta
        # run thru vfh, this produces actual steering angle
        scan = list(car.laserData)
        self.vfh.update(scan)
        goalDir = angleDelta
        tDir = self.vfh.navigate(goalDir, self.prevDir)
        closeObstacle = False #any( x < CLOSE_OBSTACLE_THRESHOLD for x in [car.getObstacleLeft(), car.getObstacleRight()] )
        A_THRESH = 8.0
        if car.tractorData.amot > A_THRESH:
            self.overCurrent += 1
        else:
            self.overCurrent = 0
        OVERCURRENT_THRESH = 14
        if tDir is None or closeObstacle or self.overCurrent >= OVERCURRENT_THRESH:
            print "!!! ---", car.tractorData.amot, tDir, min(x for x in scan if x > 0)
            car.setSpeed(0)
            self.overCurrent = 0
            print "no way"
            return NavigatorInterface.STATE_CHANGE_NONE if scan is None or not scan else NavigatorInterface.STATE_CHANGE_RETREAT

        car.setSpeed(SPEED)
        self.prevDir = tDir
        
        if tDir > car.MAX_STEER:
            car.setSteerAngle(car.MAX_STEER)
        elif tDir < -car.MAX_STEER:
            car.setSteerAngle(-car.MAX_STEER)
        else:
            car.setSteerAngle(tDir)
            
        print "done"
        return NavigatorInterface.STATE_CHANGE_NONE
    
            
    def reset(self):
        self.mission = MissionHolder()
        #mission.loadMission("missions/mission_coridor.txt")
        if self.missionFileName.endswith(".dat"):
            self.mission.loadMissionRK(self.missionFileName)
        else:
            self.mission.loadMission(self.missionFileName)
        totalDist = 0
        for i in range(1, len(self.mission.getMissionPoints())):
            totalDist += RoboUtils.getDistanceToPoint(self.mission.getMissionPoints()[i-1], self.mission.getMissionPoints()[i])
        print "TOTAL:", totalDist
        self.activeIndex = 1
        self.targetPoint = self.mission.getMissionPoints()[self.activeIndex] # pocatecni cilovy bod
        self.boundaryBox = RoboUtils.getBoundaryBox(self.mission.getMissionPoints(), 30)
        #self.vfh = VFH(laserFOV = math.radians(180), maxRange = 1.2, safetyDistance = 0.40, blockingDistance = 0.32, turnRadius = None, verbose = True)
        self.vfh = VFH(laserFOV = math.radians(180), maxRange = 2.2, safetyDistance = 0.50, blockingDistance = 0.42, turnRadius = None, verbose = True)
        self.prevDir = 0.0
        self.overCurrent = 0
        
    def getVisibleBoundaryBox(self):
        return self.boundaryBox
    
    def processEvent(self, event, viewPort):
        NavigatorInterface.processEvent(self, event, viewPort)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.targetPoint = viewPort.getRealCoord(event.pos)
            
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.missionStarted = True
    
    def drawNavigatorData(self, viewPort):
        #font = pygame.font.Font(None, 32)    
        #ren = font.render("Sickday {0}".format(0), 0, pygame.Color('black'))
        #ren = font.render("Sickday %d" % 0, 0, pygame.Color('black'))
        #viewPort.screen.blit(ren, (30, 30))
        # draw circle around target point
        pygame.draw.circle(viewPort.screen, pygame.Color('blue'), viewPort.getScreenCoord(self.targetPoint), 5, 0)
        
        # plan cesty
        missionToDraw = self.mission.getMissionPoints()
        if len(missionToDraw) > 1:
                pygame.draw.lines(viewPort.screen, pygame.Color('gray'), False, map(viewPort.getScreenCoord, missionToDraw))
