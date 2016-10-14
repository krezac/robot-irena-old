'''
Created on 15.3.2012

@author: Kamil.Rezac

Calculation of car position update
'''
import math
import random

def update(self, xPosition, yPosition, orientation, carLength, distMoved, steerAngle, 
           positionSigma, orientationSigma, steerSigma):
    
    # add noise
    if positionSigma > 0:
        xPosition += random.gauss(0, positionSigma)
        yPosition += random.gauss(0, positionSigma)
    
    if orientationSigma > 0:
        orientation += random.gauss(0, positionSigma)
        
    if steerSigma > 0:
        steerAngle += random.gauss(0, steerSigma)

    xNewPosition = xPosition
    yNewPosition = yPosition
    if (self.steerAngle == 0): # go straight
        xNewPosition += distMoved * math.sin(orientation)
        yNewPosition += distMoved * math.cos(orientation)
        newOrientation = orientation
    else:
        radius = carLength / math.tan(steerAngle)
        deltaAngle = distMoved * math.cos(steerAngle) / radius            
        dx = radius * (1. - math.cos(deltaAngle))
        dy = radius * math.sin(deltaAngle)
        
        newOrientation = (orientation + deltaAngle) % (2 * math.pi)
        xNewPosition += -dx * math.cos(orientation) + dy * math.sin(orientation)
        yNewPosition +=  dx * math.sin(orientation) + dy * math.cos(orientation)
    
    return [xNewPosition, yNewPosition, newOrientation]
