'''
Created on May 20, 2010

@author: krezac
'''
import math
def normalizeAngle(angle):
    while angle > math.pi:
        angle = angle - 2*math.pi
        
    while angle < -math.pi:
        angle = angle + 2*math.pi
    return angle

def getBoundaryBox(data, extendPercent):
    minX = 999999999999.9
    minY = 999999999999.9
    maxX = -999999999999.9
    maxY = -999999999999.9
    
    # calculate tight bbox
    for point in data:
        if point[0] < minX:
            minX = point[0]
        if point[0] > maxX:
            maxX = point[0]
        if point[1] < minY:
            minY = point[1]
        if point[1] > maxY:
            maxY = point[1]
            
    # and extend it by given percentage
            # add some free space
    reserveX = (maxX-minX) / 200.0 * extendPercent
    reserveY = (maxY-minY) / 200.0 * extendPercent
    minX -= reserveX
    minY -= reserveY
    maxX += reserveX
    maxY += reserveY
    
    print "bbox range", minX, minY, maxX, maxY, maxX-minX, maxY-minY
    
    return [[minX, minY], [maxX, maxY]]
    
def getDistanceToPoint(fromPoint, targetPoint):
    xDif = targetPoint[0] - fromPoint[0]
    yDif = targetPoint[1] - fromPoint[1]
    return math.sqrt(xDif*xDif + yDif*yDif)

def getAngleToPoint(fromPoint, targetPoint):
    xDif = targetPoint[0] - fromPoint[0]
    yDif = targetPoint[1] - fromPoint[1]
    
    rawAngle = 0.0
    if xDif == 0:
        if yDif >= 0:
            rawAngle = 0.0
        else:
            rawAngle = math.pi
    else:
        rawAngle =  math.atan2(xDif, yDif)
            
    return normalizeAngle(rawAngle)

def deg2rad(deg):
    print "deg", deg
    rr = deg[0]*math.pi/180.0,deg[1]*math.pi/180.0
    print "rad",rr
    return rr

def rad2xy(coord):
    RADIUS = 6373000
    xy = RADIUS*coord[1]*math.cos(coord[0]), RADIUS*coord[0]
    print "xy",xy
    return xy

def deg2xy(deg):
    return rad2xy(deg2rad(deg))