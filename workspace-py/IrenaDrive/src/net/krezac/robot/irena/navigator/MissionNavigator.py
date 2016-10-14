'''
Created on May 20, 2010

@author: krezac
'''
from net.krezac.robot.irena.navigator.NavigatorInterface import NavigatorInterface
from net.krezac.robot.irena.main.MissionHolder import MissionHolder
from net.krezac.robot import RoboUtils
import pygame
from net.krezac.robot.irena.main import CarConfig

class MissionNavigator(NavigatorInterface):
    '''
    classdocs
    '''


    def __init__(self, fileName):
        '''
        Constructorarte
        '''
        self.missionFileName = fileName
        self.reset()
        self.firstCall = True
        self.missionStarted = False
    
    def update(self, car):
        if self.firstCall:
            self.firstCall = False
            car.setPosition(self.mission.getMissionPoints()[0])
        car.setPowerEnabled(True)
        
        #temporary to fake start on replay
        # 22700 pro logs/irena_2010-06-19_14-51-15.rbl_new.rbl
        #if car.robbusThread.serial.dataPosition > 22700:
        #    self.missionStarted = True
            
        if not self.missionStarted:
            return NavigatorInterface.STATE_CHANGE_NONE
        
        # TODO enable collision avoidance
        if car.getObstacleLeft() < 1.5 or car.getObstacleRight() < 1.5:
            return NavigatorInterface.STATE_CHANGE_COLISSION
        
        targetDist = RoboUtils.getDistanceToPoint(car.getGpsPosition(), self.targetPoint)
        if targetDist < 2*car.CAR_LENGTH:            
            if self.activeIndex < (len(self.mission.getMissionPoints()) - 1):
                self.activeIndex += 1
                self.targetPoint = self.mission.getMissionPoints()[self.activeIndex]
            else:
                car.setSpeed(0)
                car.setPowerEnabled(False)
                print "Close enough, stopping: ", targetDist
                return NavigatorInterface.STATE_CHANGE_FINISHED
        
        # full speed
        car.setSpeed(CarConfig.CAR_SPEED)
        
        # calculate angle to target
        angleToTarget = RoboUtils.getAngleToPoint(car.getGpsPosition(), self.targetPoint)
        angleDelta = RoboUtils.normalizeAngle(angleToTarget - car.getAzimuth())
        
        if angleDelta > car.MAX_STEER:
            car.setSteerAngle(car.MAX_STEER)
        elif angleDelta < -car.MAX_STEER:
            car.setSteerAngle(-car.MAX_STEER)
        else:
            car.setSteerAngle(angleDelta)
            
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
        
    def getVisibleBoundaryBox(self):
        return self.boundaryBox
    
    def processEvent(self, event, viewPort):
        NavigatorInterface.processEvent(self, event, viewPort)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.targetPoint = viewPort.getRealCoord(event.pos)
            
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.missionStarted = True

    
    def drawNavigatorData(self, viewPort):
        # center point
        #pygame.draw.line(viewPort.screen, pygame.Color('black'), 
        #             viewPort.getScreenCoord([-1,0]), viewPort.getScreenCoord([1,0]))
        #pygame.draw.line(viewPort.screen, pygame.Color('black'), 
        #             viewPort.getScreenCoord([0,-1]), viewPort.getScreenCoord([0,1]))
        
        #line to target
        #carpt = car.getPosition()
        #tarpt = carpt[0], carpt[1]+10
        #dirpt = car.rotateAroundOrigin(tarpt, carpt, navigator.getAngleToTarget(targetPoint))
        #pygame.draw.line(viewPort.screen, pygame.Color('blue'), 
        #             viewPort.getScreenCoord(carpt), viewPort.getScreenCoord(dirpt))


        # draw circle around target point
        pygame.draw.circle(viewPort.screen, pygame.Color('blue'), viewPort.getScreenCoord(self.targetPoint), 5, 0)
        
                # plan cesty
        missionToDraw = self.mission.getMissionPoints()
        if len(missionToDraw) > 1:
                pygame.draw.lines(viewPort.screen, pygame.Color('gray'), False, map(viewPort.getScreenCoord, missionToDraw))

