'''
Created on May 20, 2010

@author: krezac
'''
from net.krezac.robot.irena.navigator.NavigatorInterface import NavigatorInterface
from net.krezac.robot.irena.main import CarConfig
import pygame
import math

class LaserNavigator(NavigatorInterface):
    '''
    classdocs
    '''
    decimationFactor = 10

    def __init__(self):
        '''
        Constructor
        '''
        self.reset()
        self.laserDir = 0
        self.lastData = []
        self.filteredData = []
        self.derivatedData = []
        self.discriminatedData = []
        self.decimatedData = []
        self.target = 0
        
        self.lastCartesianData = []
        self.derivatedCartesianData = []
        self.filteredCartesianData = []
        self.newMinIndex = 0
        self.newRelativeIndex = 0
    
    def update(self, car):
        car.setPowerEnabled(True)
        if car.getObstacleLeft() < CarConfig.CAR_STOP_DISTANCE or car.getObstacleRight() < CarConfig.CAR_STOP_DISTANCE:
            return NavigatorInterface.STATE_CHANGE_STOP

        viewAngle = 90
        self.lastData = self.reduceViewAngle(car.laserData, viewAngle)
        self.filteredData = self.filterData(self.lastData, 5)
        self.derivatedData = self.derivateData(self.filteredData)
        self.discriminatedData = self.discriminateData(self.derivatedData)
        self.decimatedData = self.decimateData(self.discriminatedData, self.decimationFactor)
        print self.printableData(self.decimatedData)
        self.target = self.findTarget(self.decimatedData, viewAngle)
        self.laserDir = -1.0 * math.pi * self.findAzimuth(self.decimatedData, viewAngle, self.target)/180.0
        
        # cartesian stuff
        CUT_ANGLE = 20
        
        ''' convert polar laser data to cartesian '''
        # conert to cartesian
        self.lastCartesianData = []
        for i in range(0, len(self.filteredData) - 4*CUT_ANGLE):
            angleDeg = (90 - CUT_ANGLE - 0.5*i)
            angle = angleDeg * math.pi / 180.0
            self.lastCartesianData.append([self.filteredData[i + 2*CUT_ANGLE] * math.sin(angle), self.filteredData[i + 2*CUT_ANGLE] * math.cos(angle)])
            
        self.derivatedCartesianData = self.derivateCartData(self.lastCartesianData)
        self.filteredCartesianData = self.filterData2(self.derivatedCartesianData, 77)
        self.newMinIndex = self.findMinIndex(self.filteredCartesianData, 77)
        self.newRelativeIndex = -1*(self.newMinIndex - len(self.filteredCartesianData)/2 + 38) 
        self.newLaserAzimuth = self.newRelativeIndex * 100 / len(self.filteredCartesianData)
        
        # TODO
        self.laserDir = self.newLaserAzimuth
        
        
        if self.laserDir > car.MAX_STEER:
            self.laserDir = car.MAX_STEER
        if self.laserDir < -car.MAX_STEER:
            self.laserDir = -car.MAX_STEER
        car.setSpeed(CarConfig.CAR_SPEED) #0.8            
        car.setSteerAngle(self.laserDir)
        
        self.lastIrPicturePath = car.lastIrPicturePath
        self.lastVisPicturePath = car.lastVisPicturePath
        return NavigatorInterface.STATE_CHANGE_NONE
        
    def reset(self):
        pass
        
    def processEvent(self, event, viewPort):
        NavigatorInterface.processEvent(self, event, viewPort)
    
    def findMinIndex(self, data, windowSize):
        minIndex = windowSize
        minValue = data[windowSize]
        lenHalf = len(data) / 2
        for i in range(windowSize, len(data)):
            if data[i] < minValue: #or (data[i]==minValue and abs(i-lenHalf) < abs(minIndex - lenHalf)):
                minIndex = i
                minValue = data[i]
        if minIndex < 0:
            minIndex = lenHalf
        return minIndex
        
            
    def reduceViewAngle(self, data, angle):
        samplesNeeded = 4*angle # symetric and 0.5 deg step -> *4 
        if len(data) > samplesNeeded:
            return data[(len(data)-samplesNeeded)/2:-(len(data)-samplesNeeded)/2]
        else:
            return data
    
    def filterData(self, data, windowSize):
        #print data
        outData = []
        for i in range(0, len(data) - windowSize):
            value = 0
            for j in range(0, windowSize):
                d = data[i+j]
                value += d*d
            outData.append(value)
        return outData

    def filterData2(self, data, windowSize):
        #print data
        outData = []
        for i in range(0, len(data) - windowSize):
            value = 0
            for j in range(0, windowSize):
                d = data[i+j]
                value += d
            outData.append(1.0*value/windowSize)
        return outData
    
    def derivateData(self, data):
        last = 0
        derData = []
        for value in data:
            derData.append(abs(value-last))
            last = value
        return derData

    def derivateCartData(self, data):
        last = data[0]
        derData = []
        for value in data:
            if abs(value[0]-last[0]) != 0:
                der = math.log(abs(value[1]-last[1]) / abs(value[0]-last[0]))
            else:
                der = 0
            derData.append(der)
            last = value
        return derData
    
    def discriminateData(self, data):
        sortedData = data[:]
        # calculate average and cut extremes
        avg = sum(sortedData) / len(sortedData)
        for i in range(0, len(sortedData)):
            if sortedData[i] > avg:
                sortedData[i] = avg
        sortedData.sort()
        discriminator = 0.3 * sortedData[-1]
        outData = []
        for value in data:
            if value < discriminator:
                outData.append(0)
            else:
                outData.append(discriminator);
        return outData
    
    # decimate to less data
    def decimateData(self, data, decimationFactor):
        out = []
        for i in range(0, len(data)/decimationFactor):
            sum = 0
            for j in range(0, decimationFactor):
                sum += data[i*decimationFactor + j]
            if sum > 0:
                out.append(0)
            else:
                out.append(1)
        out2 = []
        for i in range(0,len(out)):
            out2.append(out[len(out)-i-1])
        return out
    
    
    def printableData(self, data):
        out = ""
        for value in data:
            if value > 0:
                out += "_"
            else:
                out += "-"
        return out 
    
    def findTarget(self, decimatedData, viewAngle):
        middleIndex = len(decimatedData)/2
        print middleIndex
        #find max
        maxPos = 0
        maxLen = 0
        workPos = 0
        workLen = 0
        for i in range(0, len(decimatedData)):
            if decimatedData[i] > 0: # path
                if workPos == 0: # first path segment:
                    workPos = i
                    workLen = 1
                else:
                    workLen += 1
            else: # obstacle
                if workLen > maxLen or (workLen == maxLen and abs(workPos+workLen/2-middleIndex) < abs(maxPos+maxLen/2-middleIndex)): # closer to center
                    maxPos = workPos
                    maxLen = workLen
                workPos = 0
                workLen = 0
                
        # visualize max
        visStr = ""
        for i in range(0, maxPos):
            visStr += " "
        for i in range(0, maxLen):
            visStr += "x" 
        for i in range(maxPos+maxLen, len(decimatedData)):
            visStr += " " 
        #print visStr, maxPos, maxLen
        # recalculate segment center to azimuth
        return maxPos+maxLen/2
    
    def findAzimuth(self, decimatedData, viewAngle, target):
        middleIndex = len(decimatedData)/2
        return 2.0 * viewAngle * (target - middleIndex) / len(decimatedData)
    
    def firstItem(self, data):
        return data[0]
    def secondItem(self, data):
        return data[1]
    
    def drawCart(self, viewPort, x, y, data, lineColor):
        XMAX = 360
        YMAX = 150        
        
        # determine limits
        xVals = map(self.firstItem, data)
        xMax = max(xVals)
        xMin = min(xVals)
        yVals = map(self.secondItem, data)
        yMax = max(yVals)
        yMin = min(yVals)
        #print "Cart limits", xMin, xMax, yMin, yMax
        # normalize
        normalizedData = []
        for d in data:
            #print "normalizing", d
            xx = (d[0] - xMin)*XMAX/(xMax-xMin)
            #yy = (d[1] - yMin)*YMAX/(yMax-yMin)
            yy = (d[1] - yMin)*XMAX/(xMax-xMin)
            #print "xy", xx, yy
            normalizedData.append([xx, yy])
        #print "normalized data", normalizedData
        for i in range(1, len(normalizedData)):
            a = normalizedData[i-1]
            b = normalizedData[i]
            pygame.draw.line(viewPort.screen, pygame.Color(lineColor), [x+a[0], y+YMAX-a[1]], [x+b[0], y+YMAX-b[1]])
            
        font = pygame.font.Font(None, 24)    
        ren = font.render("xMin:{0:4.0f} xMax:{1:4.0f} yMin:{2:4.0f} yMax:{3:4.0f}".format(xMin, xMax, yMin, yMax), 0, pygame.Color('blue'))
        viewPort.screen.blit(ren, (x, y))
    
    def drawLaserData(self, viewPort, x, y, data, lineColor):
        MAX_SIZE = 150
        dataMax = max(data)
        dataMin = min(data)
        normalizedData = []
        for d in data:
            normalizedData.append((d-dataMin)*MAX_SIZE/(dataMax-dataMin))
        
        #box
        #pygame.draw.line(viewPort.screen, pygame.Color("black"), [x,y], [x, y+MAX_SIZE])
        #pygame.draw.line(viewPort.screen, pygame.Color("black"), [x+len(data),y], [x+len(data), y+MAX_SIZE])
        #pygame.draw.line(viewPort.screen, pygame.Color("black"), [x,y], [x+len(data), y])
        #pygame.draw.line(viewPort.screen, pygame.Color("black"), [x,y+MAX_SIZE], [x+len(data), y+MAX_SIZE])
        for i in range(1, len(normalizedData)):
            pygame.draw.line(viewPort.screen, pygame.Color(lineColor), [x+i,y+MAX_SIZE - normalizedData[len(normalizedData)-i-1]], [x+i,y+MAX_SIZE - normalizedData[len(normalizedData)-i]])
        
    def drawNavigatorData(self, viewPort):
        #font = pygame.font.Font(None, 72)    
        #ren = font.render("Laser {0}".format(self.laserDir), 0, pygame.Color('black'))
        #viewPort.screen.blit(ren, (100, 100))
        
        self.drawLaserData(viewPort, 10, 50, self.lastData, "red")
        self.drawLaserData(viewPort, 10, 370, self.derivatedCartesianData, "red")
        self.drawLaserData(viewPort, 10, 530, self.filteredCartesianData, "red")

        pygame.draw.line(viewPort.screen, pygame.Color("black"), [10+self.newMinIndex,530], [10+self.newMinIndex, 700])
        font = pygame.font.Font(None, 36)    
        ren = font.render("min {0} rel {1} len {2} az {3}".format(self.newMinIndex, self.newRelativeIndex, len(self.filteredCartesianData), self.newLaserAzimuth), 0, pygame.Color('black'))
        viewPort.screen.blit(ren, (30, 530))

        #self.drawLaserData(viewPort, 410, 50, self.discriminatedData, "red")
        #self.drawLaserData(viewPort, 410, 50, self.decimatedData, "red")
        
        #pygame.draw.line(viewPort.screen, pygame.Color("black"), [10+len(self.lastData)-self.target*self.decimationFactor,50], [10+len(self.lastData)-self.target*self.decimationFactor, 700])
        pygame.draw.line(viewPort.screen, pygame.Color("gray"), [10+len(self.lastData)/2,50], [10+len(self.lastData)/2, 700])
        
        font = pygame.font.Font(None, 72)    
        ren = font.render("{0:3.0f} deg".format(self.laserDir*180/math.pi), 0, pygame.Color('black'))
        viewPort.screen.blit(ren, (500, 100))
        
        vis = pygame.image.load(self.lastVisPicturePath)        
        visrect = vis.get_rect()
        vis = pygame.transform.scale(vis, (visrect.right/2, visrect.bottom/2))
        visrect = visrect.move([400, 210])
        viewPort.screen.blit(vis, visrect)

        vis = pygame.image.load(self.lastIrPicturePath)        
        visrect = vis.get_rect()
        vis = pygame.transform.scale(vis, (visrect.right/2, visrect.bottom/2))
        visrect = visrect.move([400, 460])
        viewPort.screen.blit(vis, visrect)
        
        f2 = self.filterData2(self.lastData, 3)
        self.drawCart(viewPort, 10, 210, self.lastCartesianData, "black")
        