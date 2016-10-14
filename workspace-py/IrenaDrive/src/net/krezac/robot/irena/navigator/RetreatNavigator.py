'''
@author: krezac
@author: jisa
'''
from net.krezac.robot.irena.navigator.NavigatorInterface import NavigatorInterface
from net.krezac.robot.irena.car.CarInterface import CarInterface
from net.krezac.robot import RoboUtils
from net.krezac.robot.irena.main import CarConfig
import pygame

class RetreatNavigator(NavigatorInterface):
    '''
    This navigator retreats the car a bit while turning, then goes forward for the same distance, turning to the other direction.
    '''


    def __init__(self, retreatLeft = True):
        '''
        retreatLeft ... If set to True, the car turns left whille retreating. Otherwise it turns right.
        '''
        self.retreatDir = -1 if retreatLeft else +1
        self.reset()
    
    def update(self, car):
        if self.obstacleDist is None:
            self.obstacleDist = car.getTotalDistance()

        car.setPowerEnabled(True)
        
        amot = car.tractorData.amot

        A_THRESH = 5
        if amot > A_THRESH:
            self.overCurrent += 1
        else:
            self.overCurrent = 0

        RETREAT_DIST = 0.2
        OVERCURRENT_THRESH = 3
        if not self.retreated: #going backwards
            if self.overCurrent >= OVERCURRENT_THRESH:
                print "Bumped (B), stopping"
                car.setSpeed(0)
                self.reset(True)
                self.retreated = True
                return NavigatorInterface.STATE_CHANGE_NONE
            elif car.getTotalDistance() > self.obstacleDist - RETREAT_DIST:
                car.setSteerAngle(self.retreatDir * CarInterface.MAX_STEER)
                car.setSpeed(-CarConfig.CAR_SPEED / 2.0)
                return NavigatorInterface.STATE_CHANGE_NONE
            else:
                car.setSpeed(0)
                self.reset(True)
                self.retreated = True
                return NavigatorInterface.STATE_CHANGE_NONE
        else: #going forwards
            CLOSE_OBSTACLE_THRESHOLD = 320 #[mm]
            obstacleAhead = any(x > 0 and x < CLOSE_OBSTACLE_THRESHOLD for x in car.laserData)
            if self.overCurrent >= OVERCURRENT_THRESH or obstacleAhead:
                print "Bumped (F), stopping"
                car.setSpeed(0)
                self.reset()
                return NavigatorInterface.STATE_CHANGE_FINISHED
            elif car.getTotalDistance() < self.obstacleDist:
                car.setSteerAngle(-self.retreatDir * CarInterface.MAX_STEER)
                car.setSpeed(CarConfig.CAR_SPEED)
                return NavigatorInterface.STATE_CHANGE_NONE
            else:
                car.setSpeed(0)
                self.reset()
                return NavigatorInterface.STATE_CHANGE_FINISHED
        
    def reset(self, partial = False):
        if not partial:
            self.obstacleDist = None
        self.overCurrent = 0
        self.retreated = False
        
    def processEvent(self, event, viewPort):
        NavigatorInterface.processEvent(self, event, viewPort)
    
    def drawNavigatorData(self, viewPort):
        font = pygame.font.Font(None, 32)    
        ren = font.render("Retreat nav", 0, pygame.Color('black'))
        viewPort.screen.blit(ren, (30, 30))

        
