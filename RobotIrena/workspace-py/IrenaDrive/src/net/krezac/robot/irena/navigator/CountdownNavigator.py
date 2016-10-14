'''
Created on 5.3.2010

@author: Kamil.Rezac
'''
from net.krezac.robot.irena.navigator.NavigatorInterface import NavigatorInterface
import pygame

class CountdownNavigator(NavigatorInterface):
    '''
    classdocs
    '''


    def __init__(self, timeout):
        '''
        Constructor
        '''
        self.timeout = timeout
        self.firstCall = True
        self.finalTime = 0
    
    def update(self, car):
        #dataSource = car.dataSource
        #if dataSource.logRoot == "logs/2010-09-04_12-18-16_irena":
        #    print "correct data"
        #    if dataSource.robbusLogDataPosition > 5200:
        #        return NavigatorInterface.STATE_CHANGE_FINISHED 
        #    else:
        #        return NavigatorInterface.STATE_CHANGE_NONE
        #
        #if dataSource.logRoot == "logs/2010-09-04_12-34-40_irena":
        #    print "correct data"
        #    if dataSource.robbusLogDataPosition > 1800:
        #        return NavigatorInterface.STATE_CHANGE_FINISHED 
        #    else:
        #        return NavigatorInterface.STATE_CHANGE_NONE
            
        self.now = car.getTime()
        print self.now
        if self.firstCall:
            self.firstCall = False
            self.finalTime = self.now + self.timeout
        if self.now < self.finalTime:
            return NavigatorInterface.STATE_CHANGE_NONE
        else:
            return NavigatorInterface.STATE_CHANGE_FINISHED

    def reset(self):
        self.firstCall = True
    
    def processEvent(self, event, viewPort):
        NavigatorInterface.processEvent(self, event, viewPort)
    
    def drawNavigatorData(self, viewPort):
        font = pygame.font.Font(None, 632)    
        ren = font.render(str(int(self.finalTime - self.now)), 0, pygame.Color('black'))
        viewPort.screen.blit(ren, (200, 200))
