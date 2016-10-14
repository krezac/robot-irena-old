'''
Created on 5.3.2010

@author: Kamil.Rezac
'''
import pygame


class NavigatorInterface(object):
    '''
    classdocs
    '''
    STATE_CHANGE_NONE = 0
    STATE_CHANGE_COLISSION = 1
    STATE_CHANGE_STOP = 2
    STATE_CHANGE_FINISHED = 3
    STATE_CHANGE_RETREAT = 4

    def __init__(self):
        '''
        Constructor
        '''
        pass
        
    def update(self, car):
        ''' do a navigation step '''
        raise NotImplementedError 

    def reset(self, car):
        ''' restart navigation '''
        raise NotImplementedError 
    
    def getVisibleBoundaryBox(self):
        ''' get part of the scene which is displayed (in real coords) '''
        return (-12.0, -12.0), (12.0, 12.0)
    
    def processEvent(self, event, viewPort):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.reset()
    
    def drawNavigatorData(self, viewPort):
        ''' each navigator has to draw something '''
        raise NotImplementedError
