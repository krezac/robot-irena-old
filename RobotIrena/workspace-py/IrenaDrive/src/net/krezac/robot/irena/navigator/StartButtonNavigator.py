'''
Created on 5.3.2010

@author: Kamil.Rezac
'''
from net.krezac.robot.irena.navigator.NavigatorInterface import NavigatorInterface
from pygame import joystick
import pygame

class StartButtonNavigator(NavigatorInterface):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def update(self, car):
        if car.startPressed():
            return NavigatorInterface.STATE_CHANGE_FINISHED
        else:
            return NavigatorInterface.STATE_CHANGE_NONE

    def reset(self):
        pass # nothing to do
    
    def processEvent(self, event, viewPort):
        NavigatorInterface.processEvent(self, event, viewPort)
    
    def drawNavigatorData(self, viewPort):
        font = pygame.font.Font(None, 132)    
        ren = font.render("Press START", 0, pygame.Color('black'))
        viewPort.screen.blit(ren, (100, 400))
