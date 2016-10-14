'''
Created on Aug 20, 2010

@author: krezac
'''
import opencv
from opencv import highgui
import datetime
from net.krezac.robot.irena.laser.laser import Laser
import csv

if __name__ == '__main__':
    now = datetime.datetime.today()
    filePrefix= "%s" % (now.strftime("%Y-%m-%d_%H-%M-%S"))
    
    laser = Laser()
    laser.start()
    scan = None
    while scan == None:
        scan = laser.scan()
    laser.requestStop()
    laser.join()
    
    # transpose data
    outData = []
    for value in scan:
        outData.append([value])
    
    csvfile = open(filePrefix + "_sick.csv","wb")
    csvwriter = csv.writer(csvfile)
    csvwriter.writerows(outData)
    csvfile.close()

 

    visCapture = highgui.cvCreateCameraCapture(1)
    highgui.cvSetCaptureProperty (visCapture, highgui.CV_CAP_PROP_FRAME_WIDTH, 640)
    highgui.cvSetCaptureProperty (visCapture, highgui.CV_CAP_PROP_FRAME_HEIGHT, 480)

    irCapture = highgui.cvCreateCameraCapture(2)
    highgui.cvSetCaptureProperty (irCapture, highgui.CV_CAP_PROP_FRAME_WIDTH, 640)
    highgui.cvSetCaptureProperty (irCapture, highgui.CV_CAP_PROP_FRAME_HEIGHT, 480)

    visFrame = highgui.cvQueryFrame(visCapture)
    irFrame = highgui.cvQueryFrame(irCapture)
    highgui.cvSaveImage(filePrefix+"_cvis.jpg", visFrame)
    highgui.cvSaveImage(filePrefix+"_cir.jpg", irFrame)
    pass