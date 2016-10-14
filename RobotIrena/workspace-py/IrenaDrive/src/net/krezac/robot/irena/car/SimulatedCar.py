'''
Created on 27.2.2010

@author: Kamil.Rezac
'''
from net.krezac.robot.irena.car.CarInterface import CarInterface
import math
import pygame
from net.krezac.robot import RoboUtils
import time
import CarModel

class SimulatedCar(CarInterface):
    '''
    classdocs
    '''
    obstacles = [#(-0.1,3)
                 #, (0.3, 6)
                 #, (3, 10.1)
                 #, (6, 10.5)
                 #, (10.5, 3.0)
                 #, (10, 6.0)
                 #, (6.0, 0.0)
                 #, (3.0, -0.5)
                 ]

    def __init__(self):
        CarInterface.__init__(self)
        self.carPosition = [0,0]
        self.carAzimuth = 0
        self.steerAngle = 0
        self.speed = 0
        self.odometryAzimuth = 0
        self.totalDistance = 0
        self.laserData = [63,62,46,41,55,51,46,37,41,48,49,52,56,60,58,39,52,50,48,46,46,60,52,38,54,52,57,53,49,66,79,76,83,88,97,97,96,81,88,96,102,83,84,91,94,103,99,100,95,96,83,86,70,91,64,79,87,67,79,79,79,81,85,99,98,64,3798,3757,3771,3830,3819,3825,3791,3747,3758,3732,3733,3749,3841,3885,3952,3921,3880,3864,3826,3807,3851,3848,3842,3789,3814,3736,3719,3758,3894,3883,3872,3843,3818,3785,3766,3670,3549,3495,3453,3374,3315,3248,3227,3194,3143,3119,3098,3059,3025,2999,2952,2934,2914,2873,2872,2836,2805,2775,2752,2732,2696,2695,2662,2642,2619,2585,2571,2560,2537,2530,2473,2491,2465,2449,2408,2400,2368,2374,2346,2349,2098,2122,2259,2262,2272,2239,2236,2234,2188,2181,2146,2133,2135,2149,2112,2108,2085,2070,2107,2091,2106,2070,2067,2060,2090,2071,2083,2106,2084,2024,1986,2025,2017,1994,1978,1971,1941,1904,1887,1889,1886,1868,1827,1821,1796,1788,1793,1780,1750,1723,1719,1711,1697,1699,1659,1663,1657,1645,1672,1647,1616,1618,1602,1601,1622,1583,1598,1572,1577,1578,1581,1558,1566,1561,1523,1532,1521,1514,1524,1538,1541,1515,1514,1491,1493,1477,1485,1473,1465,1481,1463,1467,1457,1432,1430,1443,1472,1448,1463,1440,1447,1446,1444,1435,1433,1429,1420,1421,1425,1424,1424,1452,1451,1431,1413,1417,1422,1414,1434,1456,1446,1434,1436,1438,1442,1439,1429,1441,1446,1439,1461,1454,1473,1472,1461,1460,1453,1456,1461,1475,1493,1505,1484,1498,1512,1518,1527,1501,1500,1508,1537,1518,1533,1570,1579,1554,1536,1538,1560,1557,1586,1610,1602,1607,1603,1630,1639,1625,1642,1635,1651,1660,1671,1672,1667,1681,1699,1712,1712,1707,1734,1753,1752,1760,1774,1781,1782,1749,1757,1739,1740,1751,1864,1889,1907,1905,1945,1932,1953,1970,1995,2016,2022,2034,2049,2064,2069,2089,2104,2139,2137,2159,2173,2187,2217,2224,2215,2224,2279,2271,2298,2325,2337,2379,2423,2505,2554,2639,2691,2662,2655,2648,2722,2791,2757,2723,2856,3056,3507,9108,9157,9207,9281,9320,9398,9471,9532,9612,9720,9794,9881,9982,10085,10230,10363,10480,10608,10751,10892,11041,11217,11349,11560,11776,12016,12230,12481,12711,13090,13524,13955,14131,14286,14455,14568,14666,14816,15126,15450,15686,16078,16750,16529,16018,16143,16247,19100,19405,19796,0,2454,2446,2435,2402,2394,2418,2435,2454,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4012,3949,3888,3814,3791,3782,3771,3752,3753,3740,3731,3724,3725,3713,39,60,91,91,98,98,93,98,103,89,89,87,99,73,90,76,80,85,73,73,70,65,61,60,51,56,62,64,59,53,64,64,63,58,57,60,62,47,54,59,49,50,57,47,52,36,39,42,29,35,37,35,39,34,31,34,30,26,16,16,30,21,21,24,24,26,16,16,16]
        self.imuData = [0,0,0,0,0,0,0,0,0]

    def setPosition(self, position):
        self.carPosition = position
        
    def setAzimuth(self, azimuth):
        self.carAzimuth = azimuth

    def setSpeed(self, speed):
        self.speed = speed

    def setSteerAngle(self, steerAngle):
        self.steerAngle = steerAngle
    
    def getGpsPosition(self):
        return self.carPosition
    
    def getOdometryPosition(self):
        return self.carPosition
    
    def synchronizePosition(self):
        pass
    
    def getAzimuth(self):
        return RoboUtils.normalizeAngle(self.carAzimuth)

    def getSpeed(self):
        return self.speed
    
    def getSteerAngle(self):
        return self.steerAngle
    
    def getObstacleLeft(self):
        return self.getDistanceToObstacle(True)

    def getObstacleRight(self):
        return self.getDistanceToObstacle(False)

    def getTotalDistance(self):
        return self.totalDistance
    
    def getTime(self):
        return time.time()
            
    def getStatusLine(self):
        return "SIMULATED Sp:{0:01.1f} St:{1:02.0f} Az:{2:03.0f}".format(self.speed, math.degrees(self.steerAngle), math.degrees(self.carAzimuth))

    def update(self):
        timeMs = 50
        if self.powerEnabled:
            distMoved = 1.0 * self.speed * timeMs / 1000
            self.totalDistance += distMoved
            
            out = CarModel.update(self, self.carPosition[0], self.carPosition[1], self.carAzimuth, 
                                  self.CAR_LENGTH, distMoved, self.steerAngle, 0.05, 0.01, 0.01)
            self.carPosition = [out[0], out[1]]
            self.carAzimuth = out[2]
            

            if (self.steerAngle == 0): # go straight
                self.carPosition = self.carPosition[0] + distMoved*math.sin(self.carAzimuth), self.carPosition[1] + distMoved*math.cos(self.carAzimuth)
            else:
                radius = self.CAR_LENGTH / math.tan(self.steerAngle)
                deltaAngle = distMoved * math.cos(self.steerAngle) / radius            
                dx = radius - radius*math.cos(deltaAngle)
                dy = radius * math.sin(deltaAngle)
    
                tempPt = dx, dy
                tempRot = self.rotateAroundOrigin(tempPt, [0,0], self.carAzimuth)
                
                #print "spd ", self.speed, " ang ", self.carAngle, " mov ", distMoved, " rad ", radius, " da", deltaAngle, " dx ", dx, " dy ", dy
                self.carAzimuth = (self.carAzimuth + deltaAngle) % (2*math.pi)
                self.carPosition = self.carPosition[0]+tempRot[0], self.carPosition[1]+tempRot[1]
        self.odometryAzimuth = self.carAzimuth
        #pygame.time.wait(timeMs)
        
    def drawCar(self, viewPort):
        CarInterface.drawCar(self, viewPort)
        # draw obstacles
        for obstacle in SimulatedCar.obstacles:
            pygame.draw.circle(viewPort.screen, pygame.Color('red'), viewPort.getScreenCoord(obstacle), 10, 0)
            
            
    def getDistanceToObstacle(self, left):
        minDist = 3.0            
        minAngle = 0.0
        for obstacle in SimulatedCar.obstacles:
            angle = RoboUtils.normalizeAngle(RoboUtils.getAngleToPoint(self.getGpsPosition(), obstacle) - self.getAzimuth())
            if angle > -0.5 and angle < 0.5:
                print "Angle to obstacle", angle
                dist = RoboUtils.getDistanceToPoint(self.getGpsPosition(), obstacle)
                print "Distance to obstacle", dist
                if dist < minDist:
                    minDist = dist
                    minAngle = angle
        # correct for car length
        #minDist -= self.CAR_LENGTH
        
        if (minAngle < 0 and left) or (minAngle > 0 and not left):
            minDist -= 0.01
        else:
            minDist += 0.01
        print "minDist", minDist
        return  minDist   
