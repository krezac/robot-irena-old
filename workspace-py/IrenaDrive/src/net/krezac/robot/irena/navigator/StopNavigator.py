'''
Created on May 20, 2010

@author: krezac
'''
from net.krezac.robot.irena.navigator.NavigatorInterface import NavigatorInterface
from net.krezac.robot import RoboUtils
from net.krezac.robot.irena.main import CarConfig
import pygame

class StopNavigator(NavigatorInterface):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.obstacleLeft = 0
        self.obstacleRight = 0
        self.stopTime = 0;
        self.carTime = 0
        pass
    
    def update(self, car):
        car.setPowerEnabled(True)
        self.obstacleLeft = car.getObstacleLeft()
        self.obstacleRight = car.getObstacleRight()
        
        if self.obstacleLeft < CarConfig.CAR_STOP_DISTANCE or self.obstacleRight < CarConfig.CAR_STOP_DISTANCE:
            print "Too close, stopping", self.obstacleLeft, self.obstacleRight
            car.setSpeed(0)
            self.stopTime = car.getTime()
            self.carTime  = car.getTime()
            return NavigatorInterface.STATE_CHANGE_NONE
        else:
            if car.getTime() < self.stopTime + 3:
                return NavigatorInterface.STATE_CHANGE_NONE
            else:
                car.setSpeed(CarConfig.CAR_SPEED)
                return NavigatorInterface.STATE_CHANGE_FINISHED # obstacle has gone
            
        
    def reset(self):
        pass
        
    def processEvent(self, event, viewPort):
        NavigatorInterface.processEvent(self, event, viewPort)
    
    def drawNavigatorData(self, viewPort):
        font = pygame.font.Font(None, 72)    
        ren = font.render("Obstacle L:{0} R:{1}".format(self.obstacleLeft, self.obstacleRight), 0, pygame.Color('black'))
        viewPort.screen.blit(ren, (100, 400))

        font = pygame.font.Font(None, 72)    
        ren = font.render("wait L:{0}".format(3+self.carTime-self.stopTime), 0, pygame.Color('black'))
        viewPort.screen.blit(ren, (100, 550))
        