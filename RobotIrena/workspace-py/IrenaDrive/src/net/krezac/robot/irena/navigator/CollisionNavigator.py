'''
Created on May 20, 2010

@author: krezac
'''
from net.krezac.robot.irena.navigator.NavigatorInterface import NavigatorInterface
from net.krezac.robot import RoboUtils
from net.krezac.robot.irena.main import CarConfig
import pygame

class CollisionNavigator(NavigatorInterface):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.reset()
        self.originalSped = 0.0
        self.obstacleLost = None
    
    def update(self, car):
        car.setPowerEnabled(True)
        obstacleLeft = car.getObstacleLeft()
        obstacleRight = car.getObstacleRight()
        
        if obstacleLeft < 0.5 or obstacleRight < 0.5:
            print "Too close, stopping", obstacleLeft, obstacleRight
            car.setSpeed(0)
            self.obstacleLost = None
            return NavigatorInterface.STATE_CHANGE_NONE
        elif obstacleLeft > 1.5 and obstacleRight > 1.5:
            car.setSpeed(CarConfig.CAR_SPEED)
            if self.obstacleLost is None:
                self.obstacleLost = car.getTotalDistance()
            if (car.getTotalDistance() - self.obstacleLost) < 1:
                return NavigatorInterface.STATE_CHANGE_NONE
            else:
                print "Gone, leaving navigator", obstacleLeft, obstacleRight
                self.obstacleLost = None
                return NavigatorInterface.STATE_CHANGE_FINISHED # obstacle has gone
        else:
            car.setSpeed(CarConfig.CAR_SPEED)
            self.obstacleLost = None
            if obstacleRight > obstacleLeft:
                car.setSteerAngle(car.MAX_STEER)
            else:
                car.setSteerAngle(-car.MAX_STEER)
            
        return NavigatorInterface.STATE_CHANGE_NONE
            
        
    def reset(self):
        pass
        
    def processEvent(self, event, viewPort):
        NavigatorInterface.processEvent(self, event, viewPort)
    
    def drawNavigatorData(self, viewPort):
        font = pygame.font.Font(None, 32)    
        ren = font.render("Collision nav", 0, pygame.Color('black'))
        viewPort.screen.blit(ren, (30, 30))

        