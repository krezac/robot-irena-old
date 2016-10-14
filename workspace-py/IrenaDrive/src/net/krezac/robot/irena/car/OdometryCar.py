'''
Created on 27.2.2010

@author: Kamil.Rezac
'''
from net.krezac.robot.irena.car.CarInterface import CarInterface

class OdometryCar(CarInterface):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        abstract, so constructor should fail
        '''
        super(OdometryCar, self).__init__()
        raise NotImplementedError("Abstract parent should not be instantiated")
    
    def setPosition(self, position):
        raise NotImplementedError("Implement in child class")
        
    def setAzimuth(self, azimuth):
        raise NotImplementedError("Implement in child class")
    
    def getPosition(self):
        raise NotImplementedError("Implement in child class")
    
    def getAzimuth(self):
        raise NotImplementedError("Implement in child class")
    
    def update(self):
        raise NotImplementedError("Implement in child class")