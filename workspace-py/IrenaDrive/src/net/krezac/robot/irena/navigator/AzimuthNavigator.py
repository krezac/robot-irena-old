'''
Created on May 20, 2010

@author: krezac
'''
from net.krezac.robot.irena.navigator.NavigatorInterface import NavigatorInterface
from net.krezac.robot import RoboUtils
from net.krezac.robot.irena.main import CarConfig
import pygame

class AzimuthNavigator(NavigatorInterface):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.azimuthDiff = 0
        self.lastAzimuth = 0
        self.reset()
    
    def update(self, car):
        car.setPowerEnabled(True)
        if self.positionFixed:
            print "have position, go"
            #if car.getObstacleLeft() < 1.5 or car.getObstacleRight() < 1.5:
            #    print "COLLISION"
            #    return NavigatorInterface.STATE_CHANGE_STOP
            

            #regular navigation
            self.lastAzimuth = car.getAzimuth()
            self.azimuthDiff = RoboUtils.normalizeAngle(1.4*(self.requestedAzimuth - self.lastAzimuth))
            print self.azimuthDiff
            if self.azimuthDiff > car.MAX_STEER:
                self.azimuthDiff = car.MAX_STEER
            if self.azimuthDiff < -car.MAX_STEER:
                self.azimuthDiff = -car.MAX_STEER
            car.setSpeed(CarConfig.CAR_SPEED) #0.8
            
            car.setSteerAngle(self.azimuthDiff)
            return NavigatorInterface.STATE_CHANGE_NONE
        else:
            #capturing azimuth
            print "toCapture"
            if self.toCaptureCount > 0:
                self.capturedSamples.append(car.getAzimuth())
                self.toCaptureCount -= 1
                print "Capturing azimuth, remains", self.toCaptureCount
            else:
                self.requestedAzimuth = RoboUtils.normalizeAngle(float(sum(self.capturedSamples))/len(self.capturedSamples))
                print self.capturedSamples
                print "average azimuth", self.requestedAzimuth
                self.positionFixed = True
        return NavigatorInterface.STATE_CHANGE_NONE
        
    def reset(self):
        self.capturedSamples = []
        self.toCaptureCount = 10
        self.positionFixed = False
        self.requestedAzimuth = 1 # TODO temporary fo rebugging
        
    def processEvent(self, event, viewPort):
        NavigatorInterface.processEvent(self, event, viewPort)
    
    def drawNavigatorData(self, viewPort):
        font = pygame.font.Font(None, 32)    
        ren = font.render("Azimuth nav plan {0} curr {1} dif {2}".format(self.requestedAzimuth, self.lastAzimuth, self.azimuthDiff), 0, pygame.Color('black'))
        viewPort.screen.blit(ren, (30, 30))


        