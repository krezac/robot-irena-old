'''
Created on 19.2.2010

@author: Kamil.Rezac
'''

import struct

class RobbusData(object):
    '''
    classdocs
    '''


    def __init__(self, address, requestFormat, requestDescription, requestPostProcess, responseFormat, responseDescription, responsePostProcess):
        '''
        Constructor
        '''
        self.address = address
        self.requestDataStruct = struct.Struct(requestFormat)
        self.responseDataStruct = struct.Struct(responseFormat)
        self.requestDescription = requestDescription
        self.requestPostProcess = requestPostProcess
        self.responseDescription = responseDescription
        self.responsePostProcess = responsePostProcess
        self.timestamp = 0
        self.lastPeriod = 0
        
        #print "Request size initialized:", address, self.requestDataStruct.size
        #print "Response size initialized:", address, self.responseDataStruct.size

        
    def getAddress(self):
        return self.address
    
    def getRequestData(self):
        raise NotImplementedError("Implement in child class")
        
        
    def setResponseData(self, data):
        raise NotImplementedError("Implement in child class")
    
    def updateTimestamp(self, newStamp):
        if newStamp > self.timestamp:
            period = newStamp - self.timestamp
        else:
            period = 265 + newStamp - self.timestamp
        self.timestamp = newStamp
        self.lastPeriod = 256.0*256/16000*period #convert to ms
        #print "Period is", self.lastPeriod, "ms"
        
    def parseRequest(self, data):
        return self.requestDataStruct.unpack(data)
    
    def parseResponse(self, data):
        return self.responseDataStruct.unpack(data)