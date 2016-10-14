'''
Created on 23.1.2010

@author: Kamil.Rezac
'''

import pygame
import math

class ViewPort:
    '''
    classdocs
    '''
    
    def setRealRangeBox(self, realBox):
        self.setRealRange(realBox[0], realBox[1])

    def setRealRange(self, realMin, realMax):
        self.realCenter = (realMax[0]+realMin[0])/2, (realMax[1]+realMin[1])/2
        self.scale = min([1.0*self.screen.get_width()/(realMax[0]-realMin[0]),1.0*self.screen.get_height()/(realMax[1]-realMin[1])])
        #print "Center: ", self.realCenter
        #print "Scale: ", self.scale
        
    def getScreenCoord(self, realCoord):
        xDisp = self.screen.get_width()/2 + (realCoord[0]-self.realCenter[0]) * self.scale
        yDisp = self.screen.get_height()/2 - (realCoord[1]-self.realCenter[1]) * self.scale
        return int(xDisp), int(yDisp)
    
    def getRealCoord(self, screenCoord):
        xReal = 1.0*self.realCenter[0] + (1.0*screenCoord[0] - 1.0*self.screen.get_width()/2) / self.scale
        yReal = 1.0*self.realCenter[1] + (1.0*self.screen.get_height()/2 - 1.0*screenCoord[1]) / self.scale
        return xReal, yReal
        
    def getScale(self):
        return self.scale
    
    def __init__(self, screenSize):
        '''
        Constructor
        '''
        self.screen = pygame.display.set_mode(screenSize, pygame.NOFRAME)
        self.setRealRange([-1.1,-1.1], [1.1,1.1])
        