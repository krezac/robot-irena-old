'''
Created on 24.1.2010

@author: Kamil.Rezac
'''
from ViewPort import ViewPort

import sys, pygame, os
from net.krezac.robot.irena.car.SimulatedCar import SimulatedCar
from net.krezac.robot.irena.car.RobbusCar import RobbusCar
from net.krezac.robot.irena.navigator.JoystickNavigator import JoystickNavigator
from net.krezac.robot.irena.navigator.AzimuthNavigator import AzimuthNavigator
from net.krezac.robot.irena.navigator.MissionNavigator import MissionNavigator
from net.krezac.robot.irena.navigator.CollisionNavigator import CollisionNavigator
from net.krezac.robot.irena.navigator.RetreatNavigator import RetreatNavigator
from net.krezac.robot.irena.navigator.NavigatorInterface import NavigatorInterface
from net.krezac.robot import RoboUtils
from net.krezac.robot.irena.navigator.StartButtonNavigator import StartButtonNavigator
from net.krezac.robot.irena.navigator.NeatoNavigator import NeatoNavigator
from net.krezac.robot.irena.navigator.CountdownNavigator import CountdownNavigator
from net.krezac.robot.irena.navigator.LaserNavigator import LaserNavigator
from net.krezac.robot.irena.navigator.StopNavigator import StopNavigator
from net.krezac.robot.irena.datasource.LogDataSource import LogDataSource
import time
from net.krezac.robot.irena.datasource.RobotDataSource import RobotDataSource
from net.krezac.robot.irena.navigator.SickdayNavigator import SickdayNavigator

if __name__ == '__main__':
    pygame.init()
    os.environ['SDL_VIDEO_WINDOW_POS'] = '566,0'
    
    screenSize = width, height = 800, 700 # rozmer okna
    bobky = []    
    
    # logs/2010-09-17_18-04-08_irena prvni se sickem dolu
    # 2010-09-17_18-05-02_irena cela cesticka
    #dataSource = LogDataSource("logs/2011-06-07_19-59-40_irena") # prvni kolo, cekani 70s, bez cekani po kolizi
    #dataSource = LogDataSource("logs/2012-05-30_17-22-39_irena") # naklaneni doma
    #dataSource = LogDataSource("logs/2012-06-02_10-54-37_irena") # 2012 Roboorienteering 1. kolo
    dataSource = RobotDataSource()
    
    #car = SimulatedCar()
    car = RobbusCar(dataSource)
    neatoNavigator = NeatoNavigator("missions/Kolo3.dat")
    #missionNavigator = MissionNavigator("missions/test.dat")
    startButtonNavigator = StartButtonNavigator()
    #missionNavigator = MissionNavigator("missions/Kolo2.dat")
    #missionNavigator = MissionNavigator("missions/mission_homologace_rev.txt")
    #missionNavigator = MissionNavigator("missions/mission_square.txt")
    #azimuthNavigator = AzimuthNavigator()
    #sickdayNavigator = SickdayNavigator()
    #colissionNavigator = CollisionNavigator()
    stopNavigator = StopNavigator()
    #laserNavigator = LaserNavigator()
    retreatNavigator = RetreatNavigator()

    joystickNavigator = JoystickNavigator()
    #navigator = AzimuthNavigator()
    
    navigatorStack = []
    navigatorStack.append(neatoNavigator)
    navigatorStack.append(startButtonNavigator)
    #navigatorStack.append(sickdayNavigator)
    #navigatorStack.append(missionNavigator)
    #navigatorStack.append(laserNavigator)
    #navigatorStack.append(azimuthNavigator)
    #navigatorStack.append(CountdownNavigator(140)) # wait for start button press
    #navigatorStack.append(joystickNavigator) # manual control

    
    viewPort = ViewPort(screenSize)
    paused = False
    if isinstance(dataSource, LogDataSource):
        delay = 0 # 0.1
        neatoNavigator.missionStarted = True
    else:
        delay = 0
        
    while 1:
        navigator = None
        if len(navigatorStack) == 0:
            print "task complete, finished"
            pygame.time.wait(150)
        else:
            navigator = navigatorStack[-1]
        
        viewPort.setRealRangeBox(neatoNavigator.getVisibleBoundaryBox()) # velikost zobrazeneho uzemi


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                car.terminate()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    car.terminate()
                    sys.exit()                 
                elif event.key == pygame.K_r:
                    navigatorStack = []
                    navigatorStack.append(neatoNavigator) # will be reset in its handler
                    neatoNavigator.reset()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_0:
                    delay = 0
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                    delay = 0.1
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_2:
                    delay = 0.2
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_3:
                    delay = 0.3
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_4:
                    delay = 0.4
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_5:
                    delay = 0.5
       
                
            if navigator is not None:
                navigator.processEvent(event, viewPort)        
        
        if not paused or not isinstance(dataSource, LogDataSource):
            car.update()
            
        if delay > 0 and isinstance(dataSource, LogDataSource):
            pass #time.sleep(delay)
        
        if navigator is not None:
            ret = navigator.update(car)
            #print "ret", ret
            #if ret == NavigatorInterface.STATE_CHANGE_COLISSION:
            #    navigatorStack.append(colissionNavigator)
            #el
            if ret == NavigatorInterface.STATE_CHANGE_STOP:
                navigatorStack.append(stopNavigator)
            elif ret == NavigatorInterface.STATE_CHANGE_FINISHED:
                navigatorStack.pop()
            elif ret == NavigatorInterface.STATE_CHANGE_RETREAT:
                navigatorStack.append(retreatNavigator)
            elif ret == NavigatorInterface.STATE_CHANGE_NONE:
                pass
            else: 
                print "Unknown navigator state"
                car.terminate()
                sys.exit()

            viewPort.screen.fill(pygame.Color('white'))
    
            bobky.append(viewPort.getScreenCoord(car.getGpsPosition()))
            if len(bobky) > 1:
                pygame.draw.lines(viewPort.screen, pygame.Color('green'), False, bobky)
            
            navigator.drawNavigatorData(viewPort)
            car.drawCar(viewPort)        
            
            pygame.display.flip()                
        
        
