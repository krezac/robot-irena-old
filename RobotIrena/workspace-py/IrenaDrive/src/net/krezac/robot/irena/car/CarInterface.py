'''
Created on 27.2.2010

@author: Kamil.Rezac
'''
import math
import pygame

class CarInterface:
    '''
    classdocs
    '''

    CAR_WIDTH = 0.45
    CAR_LENGTH = 0.75
    GPS_CAR_COLOR = 'black'
    ODOMETRY_CAR_COLOR = 'blue'
    STEER_COLOR = 'red'
    MAX_SPEED = 2
    MAX_STEER = 0.5

    def __init__(self):
        self.powerEnabled = False
    
    def getMaxSpeed(self):
        return self.MAX_SPEED

    def getMaxSteer(self):
        return self.MAX_STEER
    
    def setPosition(self, position):
        raise NotImplementedError("Must be implemented in child class")
        
    def setAzimuth(self, azimuth):
        raise NotImplementedError("Must be implemented in child class")

    def setSpeed(self, speed):
        raise NotImplementedError("Must be implemented in child class")

    def setSteerAngle(self, steerAngle):
        raise NotImplementedError("Must be implemented in child class")
    
    def getGpsPosition(self):
        raise NotImplementedError("Must be implemented in child class")
    
    def getOdometryPosition(self):
        raise NotImplementedError("Must be implemented in child class")
    
    def synchronizePosition(self):
        raise NotImplementedError("Must be implemented in child class")

    def getAzimuth(self):
        raise NotImplementedError("Must be implemented in child class")
    
    def getSpeed(self):
        raise NotImplementedError("Must be implemented in child class")
    
    def getSteerAngle(self):
        raise NotImplementedError("Must be implemented in child class")
    
    def getStatusLine(self):
        raise NotImplementedError("Must be implemented in child class")

    def LaserData(self):
        raise NotImplementedError("Must be implemented in child class")
    
    def setPowerEnabled(self, enabled):
        self.powerEnabled = enabled
        
    def update(self):
        raise NotImplementedError("Implement in child class")
    
    def getObstacleLeft(self):
        raise NotImplementedError("Implement in child class")

    def getObstacleRight(self):
        raise NotImplementedError("Implement in child class")

    def getTotalDistance(self):
        raise NotImplementedError("Implement in child class")
    
    def getTime(self):
        raise NotImplementedError("Implement in child class")
    
    def rotateAroundOrigin(self, pt, origin, alpha):
        ptMoved = pt[0] - origin[0], pt[1] - origin[1]
        ptRotated = -ptMoved[0]*math.cos(alpha) + ptMoved[1]*math.sin(alpha), ptMoved[0]*math.sin(alpha) + ptMoved[1]*math.cos(alpha)
        return ptRotated[0] + origin[0], ptRotated[1] + origin[1]
    
    def startPressed(self):
        return True
    
    def drawCar(self, viewPort):
        self.drawCarPos(viewPort, self.getGpsPosition(), self.getAzimuth(), pygame.Color(self.GPS_CAR_COLOR))
        self.drawCarPos(viewPort, self.getOdometryPosition(), self.odometryAzimuth, pygame.Color(self.ODOMETRY_CAR_COLOR))
        
    def drawCarPos(self, viewPort, carPosition, carAzimuth, carColor):
        #carPosition = position        
        #carAzimuth = self.getAzimuth()
        steerAngle = self.getSteerAngle()
        if viewPort.getScale() > 50:
            # define car shape
            leftFrontReal = [carPosition[0]-self.CAR_WIDTH/2, carPosition[1]+self.CAR_LENGTH]
            leftRearReal = [carPosition[0]-self.CAR_WIDTH/2, carPosition[1]]
            rightFrontReal = [carPosition[0]+self.CAR_WIDTH/2, carPosition[1]+self.CAR_LENGTH]
            rightRearReal = [carPosition[0]+self.CAR_WIDTH/2, carPosition[1]]
            centerFrontReal = [carPosition[0], carPosition[1]+self.CAR_LENGTH]
            centerRearReal = [carPosition[0], carPosition[1]]
            angleDirReal = [carPosition[0], carPosition[1]+1.5*self.CAR_LENGTH]
            steerDirReal = self.rotateAroundOrigin([carPosition[0], carPosition[1]+1.5*self.CAR_LENGTH],
                                 [carPosition[0], carPosition[1]+self.CAR_LENGTH], -steerAngle)
            
            # rotate car
            leftFrontRot = self.rotateAroundOrigin(leftFrontReal, carPosition, carAzimuth)
            leftRearRot = self.rotateAroundOrigin(leftRearReal, carPosition, carAzimuth)
            rightFrontRot = self.rotateAroundOrigin(rightFrontReal, carPosition, carAzimuth)
            rightRearRot = self.rotateAroundOrigin(rightRearReal, carPosition, carAzimuth)
            centerFrontRot = self.rotateAroundOrigin(centerFrontReal, carPosition, carAzimuth)
            centerRearRot = self.rotateAroundOrigin(centerRearReal, carPosition, carAzimuth)
            angleDirRot = self.rotateAroundOrigin(angleDirReal, carPosition, carAzimuth)
            steerDirRot = self.rotateAroundOrigin(steerDirReal, carPosition, carAzimuth)
    
            leftFront = viewPort.getScreenCoord(leftFrontRot)
            leftRear = viewPort.getScreenCoord(leftRearRot)
            rightFront = viewPort.getScreenCoord(rightFrontRot)
            rightRear = viewPort.getScreenCoord(rightRearRot)
            centerFront = viewPort.getScreenCoord(centerFrontRot)
            centerRear = viewPort.getScreenCoord(centerRearRot)
            angleDir = viewPort.getScreenCoord(angleDirRot)
            steerDir = viewPort.getScreenCoord(steerDirRot)
                                    
            pygame.draw.line(viewPort.screen, carColor, leftRear, rightRear)
            pygame.draw.line(viewPort.screen, carColor, leftFront, rightFront)
            pygame.draw.line(viewPort.screen, carColor, centerRear, angleDir)
            pygame.draw.line(viewPort.screen, carColor, centerFront, steerDir)            
        else:
            # scale too small draw alternative model
            angleDirReal = carPosition[0], carPosition[1] + 40 / viewPort.getScale()
            angleDirRot = self.rotateAroundOrigin(angleDirReal, carPosition, carAzimuth)

            steerDirReal = carPosition[0], carPosition[1] + 40 / viewPort.getScale()
            steerDirRot = self.rotateAroundOrigin(steerDirReal, carPosition, -steerAngle)
            steerDirRot2 = self.rotateAroundOrigin(steerDirRot, carPosition, carAzimuth)
            
            drawPos = viewPort.getScreenCoord(carPosition)
            angleDir = viewPort.getScreenCoord(angleDirRot)
            steerDir = viewPort.getScreenCoord(steerDirRot2)

            pygame.draw.circle(viewPort.screen, carColor, drawPos, 20, 1)
            pygame.draw.line(viewPort.screen, carColor, drawPos, angleDir)
            pygame.draw.line(viewPort.screen, pygame.Color(self.STEER_COLOR), drawPos, steerDir)
            
        # draw status line
        font = pygame.font.Font(None, 26)    
        ren = font.render(self.getStatusLine(), 0, pygame.Color('black'))
        
        #draw laser data
        laserData = self.getLaserData()
        laserPts = []
        laserCenter = [150, 150]
        laserScale = 50 # points per meter
        pygame.draw.line(viewPort.screen, pygame.Color("lightgray"), [0,laserCenter[1]],[2*laserCenter[0],laserCenter[1]])
        pygame.draw.line(viewPort.screen, pygame.Color("lightgray"), [laserCenter[0], 0],[laserCenter[0], laserCenter[0]])
        pygame.draw.arc(viewPort.screen, pygame.Color("lightgray"), pygame.Rect([laserCenter[0]-1*laserScale,laserCenter[1]-1*laserScale],[2*laserScale,2*laserScale]), 0, math.pi)
        pygame.draw.arc(viewPort.screen, pygame.Color("lightgray"), pygame.Rect([laserCenter[0]-2*laserScale,laserCenter[1]-2*laserScale],[4*laserScale,4*laserScale]), 0, math.pi)
        pygame.draw.arc(viewPort.screen, pygame.Color("lightgray"), pygame.Rect([laserCenter[0]-3*laserScale,laserCenter[1]-3*laserScale],[6*laserScale,6*laserScale]), 0, math.pi)
        for angDeg in range(len(laserData)):
            dist = laserData[angDeg]
            if dist== 0 or dist > 4:
                continue
            angRad = ((180+angDeg)%360) * math.pi / 180.0
            cosAng = math.cos(angRad)
            sinAng = math.sin(angRad)
            pt = [int(laserCenter[0] + laserScale*(dist*cosAng)), int(laserCenter[1] + laserScale*(dist*sinAng))]
            laserPts.append(pt)
            pygame.draw.circle(viewPort.screen, pygame.Color('red'), pt, 1)
            
        viewPort.screen.blit(ren, (10, 50))
        
    def terminate(self):
        pass

