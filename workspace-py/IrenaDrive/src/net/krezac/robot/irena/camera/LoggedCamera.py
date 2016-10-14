'''
Created on Sep 3, 2010

@author: krezac
'''
from opencv import highgui
import os
from threading import Thread, Lock, Event

class LoggedCamera(Thread):
    '''
    classdocs
    '''


    def __init__(self, logDirName):
        '''
        Constructor
        '''
        Thread.__init__(self) 
        self.lock = Lock()
        self.shouldIRun = Event()
        self.shouldIRun.set()
        
        self.visFrame = None
        self.irFrame = None

        # dirs for camera logs
        self.logRoot = logDirName
        self.irCamLogDir = "%s/cam_ir" % (logDirName)
        self.irCamLogIndex = 0
        if not os.path.exists(self.irCamLogDir):
            os.makedirs(self.irCamLogDir) 
        self.visCamLogDir = "%s/cam_vis" % (logDirName)
        self.visCamLogIndex = 0
        if not os.path.exists(self.visCamLogDir):
            os.makedirs(self.visCamLogDir) 
            
        self.lastVisiblePicturePath = None
        self.lastIrPicturePath = None

        self.visCapture = highgui.cvCreateCameraCapture(1)
        highgui.cvSetCaptureProperty (self.visCapture, highgui.CV_CAP_PROP_FRAME_WIDTH, 640)
        highgui.cvSetCaptureProperty (self.visCapture, highgui.CV_CAP_PROP_FRAME_HEIGHT, 480)
        
        self.irCapture = highgui.cvCreateCameraCapture(2)
        highgui.cvSetCaptureProperty (self.irCapture, highgui.CV_CAP_PROP_FRAME_WIDTH, 640)
        highgui.cvSetCaptureProperty (self.irCapture, highgui.CV_CAP_PROP_FRAME_HEIGHT, 480)
        
    def terminate(self):
        pass
    
    def captureVis(self):
        highgui.cvGrabFrame(self.visCapture)
        frame = highgui.cvRetrieveFrame(self.visCapture)
        #self.lock.acquire()
        #frame = self.visFrame
        #self.lock.release()
        fileName = "%s/%06d.jpg" % (self.irCamLogDir, self.irCamLogIndex)
        print fileName
        highgui.cvSaveImage(fileName, frame)
        self.irCamLogIndex += 1
        return frame
    
    def captureIr(self):
        highgui.cvGrabFrame(self.irCapture)
        frame = highgui.cvRetrieveFrame(self.irCapture)
        #self.lock.acquire()
        #frame = self.irFrame
        #self.lock.release()
        fileName = "%s/%06d.jpg" % (self.visCamLogDir, self.visCamLogIndex)
        print fileName
        highgui.cvSaveImage(fileName, frame)
        self.visCamLogIndex += 1
        return frame
    
    def getLastVisiblePicturePath(self):
        return self.logRoot + "/cam_vis/" + "%06d.jpg" % (self.visCamLogIndex - 1)

    def getLastIrPicturePath(self):
        return self.logRoot + "/cam_ir/" + "%06d.jpg" % (self.irCamLogIndex - 1)
        
    def run(self):
        while self.shouldIRun.isSet():
            highgui.cvGrabFrame(self.visCapture)
            highgui.cvGrabFrame(self.irCapture)
            visFrame = highgui.cvRetrieveFrame(self.visCapture)
            irFrame = highgui.cvRetrieveFrame(self.irCapture)
            #self.lock.acquire()
            self.visFrame = visFrame
            self.irFrame = irFrame
            #self.lock.release()
            
    def requestStop(self):
        self.shouldIRun.clear()
