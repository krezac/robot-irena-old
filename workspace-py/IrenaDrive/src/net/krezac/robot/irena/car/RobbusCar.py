'''
Created on 27.2.2010

@author: Kamil.Rezac
'''
from net.krezac.robot.irena.car.CarInterface import CarInterface
from net.krezac.robot.irena.robbus.RobbusControllerThread import RobbusControllerThread
from net.krezac.robot.irena.robbus.data.CompassData import CompassData
from net.krezac.robot.irena.robbus.data.TractorData import TractorData
from net.krezac.robot.irena.robbus.data.HeadData import HeadData
import math
from net.krezac.robot import RoboUtils

class RobbusCar(CarInterface):
    '''
    classdocs
    '''


    def __init__(self, dataSource):
        '''
        constructor
        '''
        CarInterface.__init__(self)
        self.dataSource = dataSource
        
        self.cameraCounter = 0
        # start robbus controller thread
        self.odometryPosition = (0.0,0.0)
        self.odometryAzimuth = 0.0
        self.speed = 128
        self.moveSpeed = 0
        self.robbusThread = RobbusControllerThread(dataSource)
        self.compassData = CompassData()
        self.tractorData = TractorData()
        self.headData = HeadData()
        self.robbusThread.registerNode(self.compassData)
        self.robbusThread.registerNode(self.tractorData)
        self.robbusThread.registerNode(self.headData)
        self.steerAngle = 0
        
        self.robotTimeRaw = 0
        self.robotTimeLast = 0
        
        self.lastIrPicturePath = None
        self.lastVisPicturePath = None
        #robbusThread.start()        
        
        
    def terminate(self):
        self.dataSource.close()
        
    def setPosition(self, position):
        self.odometryPosition = position
        pass
        
    def setAzimuth(self, azimuth):
        # TODO implement
        pass

    def setSpeed(self, speed):
        if speed > self.getMaxSpeed():
            speed = self.getMaxSpeed()
        if speed < -self.getMaxSpeed():
            speed = -self.getMaxSpeed()
        MAX_MOVE_DELTA = 0.1 #[m/update]
        if speed != 0 and speed > self.moveSpeed + MAX_MOVE_DELTA:
            speed = self.moveSpeed + MAX_MOVE_DELTA
        if speed != 0 and speed < self.moveSpeed - MAX_MOVE_DELTA:
            speed = self.moveSpeed - MAX_MOVE_DELTA
        self.moveSpeed = speed
        shift = int(128 + (speed*128.0/self.getMaxSpeed()))
        if shift > 255:
            shift = 255
        if shift < 0:
            shift = 0
        self.tractorData.servoA = shift

    def setSteerAngle(self, steerAngle):
        if steerAngle > self.getMaxSteer():
            steerAngle = self.getMaxSteer()
        if steerAngle < -self.getMaxSteer():
            steerAngle = -self.getMaxSteer()
        MAX_STEER_DELTA = math.radians(10) # [rad/update]
        if steerAngle > self.steerAngle + MAX_STEER_DELTA:
            steerAngle = self.steerAngle + MAX_STEER_DELTA
        if steerAngle < self.steerAngle - MAX_STEER_DELTA:
            steerAngle = self.steerAngle - MAX_STEER_DELTA
        self.steerAngle = steerAngle
        shift = int(128 - (steerAngle*128.0/self.getMaxSteer()))
        if shift > 200:
            shift = 200
        if shift < 50:
            shift = 50
        self.headData.servoA = shift

    
    def getGpsPosition(self):
        return self.compassData.gpsPosition
    
    def getOdometryPosition(self):
        return self.odometryPosition
    
    def synchronizePosition(self):
        self.odometryPosition = self.getGpsPosition()
    
    def getAzimuth(self):
        return self.compassData.getAzimuth()
    
    def getTotalDistance(self):
        return self.tractorData.totalDistance
    
    def getTime(self):
        return self.robotTimeRaw / 244.0
    def getSpeed(self):
        # TODO implement
        return 0
    
    def getSteerAngle(self):
        # TODO implement
        return self.steerAngle
    
    def getObstacleLeft(self):
        if self.headData.getSonarLeft() > 0:
            return self.headData.getSonarLeft()/100.0
        else:
            return 3.0

    def getObstacleRight(self):
        if self.headData.getSonarRight() > 0:
            return self.headData.getSonarRight()/100.0
        else:
            return 3.0
    
    def setPowerEnabled(self, enabled):
        CarInterface.setPowerEnabled(self, enabled)
        if enabled:
            self.tractorData.enableMotor(1)
            self.headData.enableServo(1)
        else:
            self.tractorData.enableMotor(0)
            self.headData.enableServo(0)
    
    def startPressed(self):
        return not (self.tractorData.status & (1<<5))

    def stopPressed(self):
        return not (self.tractorData.status & (1<<6))
    
    def getStatusLine(self):
        s = "Sp:{0} St:{1} Az:{2:03.0f} Y:{15:02.1f} P:{16:02.1f} R:{17:02.1f} L:{3} C:{13} P:{4} Z:{14} L{5:.1f}S{10:.1f}M{7:.1f}/{9:02.1f} {12} ".format(
                #self.getSpeed(), math.degrees(self.getSteerAngle()), 
                self.tractorData.servoA, 
                self.headData.servoA,
                math.degrees(self.compassData.getAzimuth()),
                self.headData.leftSonar, 
                self.headData.rightSonar,
                self.tractorData.vlog, 
                self.tractorData.voltageToPercent(self.tractorData.vlog), 
                self.tractorData.vmot, 
                self.tractorData.voltageToPercent(self.tractorData.vmot), 
                self.tractorData.amot, 
                self.headData.vser, 
                self.tractorData.voltageToPercentNiMH(self.headData.vser),
                self.stopPressed(), self.headData.centerSonar, self.tractorData.rearSonar, 
                self.imuData[0], self.imuData[1], self.imuData[2])
        return s
    
    def getLaserData(self):
        return self.laserData
    
    def update(self):
        # patch to make head react on stop button press
        if self.tractorData.watchdog > 0 and not self.stopPressed():
            self.headData.enableServo(1)
        else:
            self.headData.enableServo(0)
            
        self.robbusThread.synchronizeBus()
        
        # calculate time
        currentTime = self.tractorData.timestamp
        timeDif = currentTime - self.robotTimeLast
        if timeDif < 0:
            timeDif = 256 - self.robotTimeLast + currentTime
        self.robotTimeRaw += timeDif
        self.robotTimeLast = currentTime
         
        # read laser
        self.laserData = self.dataSource.getLaserData()
        #print self.laserData
        
        # imu data
        self.imuData = self.dataSource.getIMUData()
                
        if self.cameraCounter == 0:
            self.irFrame = self.dataSource.getIrPicture()
            self.visFrame = self.dataSource.getVisiblePicture()
            self.cameraCounter = 1
        else:
            self.cameraCounter = (self.cameraCounter + 1) % 4
        
        self.lastIrPicturePath = self.dataSource.getLastIrPicturePath()
        self.lastVisPicturePath = self.dataSource.getLastVisiblePicturePath()
        
        self.carAzimuth = self.compassData.azimuth

        # oberride azimuth from odometry with the compass one
        self.odometryAzimuth = self.getAzimuth()
        
        # update odometry position
        distMoved = self.tractorData.lastDistance
        #print "Dist moved", distMoved
        if (self.steerAngle == 0): # go straight
            self.odometryPosition = self.odometryPosition[0] + distMoved*math.sin(self.odometryAzimuth), self.odometryPosition[1] + distMoved*math.cos(self.odometryAzimuth)
        else:
            radius = self.CAR_LENGTH / math.tan(self.steerAngle)
            deltaAngle = distMoved * math.cos(self.steerAngle) / radius            
            dx = radius - radius*math.cos(deltaAngle)
            dy = radius * math.sin(deltaAngle)
            #print "da, dx, dy", deltaAngle, dx, dy
                        
            tempPt = dx, dy
            tempRot = self.rotateAroundOrigin(tempPt, [0,0], self.odometryAzimuth)
            
            #print "spd ", self.speed, " ang ", self.carAngle, " mov ", distMoved, " rad ", radius, " da", deltaAngle, " dx ", dx, " dy ", dy
            self.odometryAzimuth = RoboUtils.normalizeAngle(self.odometryAzimuth + deltaAngle)
            self.odometryPosition = self.odometryPosition[0]+tempRot[0], self.odometryPosition[1]+tempRot[1]
            
            #print "Odometry position", self.odometryPosition
