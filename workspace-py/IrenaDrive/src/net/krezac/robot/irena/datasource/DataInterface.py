'''
Created on 8.9.2010

@author: kamil.rezac
'''

class DataInterface(object):
    '''
    abstract parent for real and logged data source
    '''


    def __init__(selfparams):
        '''
        Constructor
        '''
        
    def close(self):
        ''' close the data source '''
        pass
    
    def writeRobbusByte(self, b):
        raise NotImplementedError
    
    def readRobbusByte(self):
        raise NotImplementedError
    
    def getVisiblePicture(self):
        raise NotImplementedError
    
    def getIrPicture(self):
        raise NotImplementedError
    
    def getLastVisiblePicturePath(self):
        raise NotImplementedError

    def getLastIrPicturePath(self):
        raise NotImplementedError
        
    def getLaserData(self):
        raise NotImplementedError