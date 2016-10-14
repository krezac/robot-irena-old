'''
Created on 5.3.2010

@author: Kamil.Rezac
'''
from net.krezac.robot.irena.navigator.NavigatorInterface import NavigatorInterface
from pygame import joystick

class JoystickNavigator(NavigatorInterface):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        jCount = joystick.get_count()
        print "Joystick count: ", jCount
        if jCount > 0:
            self.joy = joystick.Joystick(0)
            self.joy.init()
        else:
            self.joy = None
    
    def update(self, car):
        if joystick.get_count() < 1:
            car.setSpeed (0)
            return NavigatorInterface.STATE_CHANGE_NONE
        
        #s = ""
        #for i in range(0,butcount):
        #    if self.joy.get_button(i):
        #        s += "1"
        #    else:
        #        s+= "0"
        #print s
        
        car.setPowerEnabled(self.joy.get_button(6))
        
        maxSpeed = car.getMaxSpeed()
        if not self.joy.get_button(4):
            maxSpeed /= 3.0        
        
        joyspeed, joysteer = -1.0*self.joy.get_axis(1), self.joy.get_axis(0)
        #print "joy", joyspeed, joysteer 
        car.setSpeed (maxSpeed * joyspeed)
        car.setSteerAngle(car.getMaxSteer() * joysteer)
        return NavigatorInterface.STATE_CHANGE_NONE

    def reset(self):
        pass # nothing to do
    
    def processEvent(self, event, viewPort):
        NavigatorInterface.processEvent(self, event, viewPort)
    
    def drawNavigatorData(self, viewPort):
        pass
