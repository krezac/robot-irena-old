'''
Created on 20.2.2010

@author: Kamil.Rezac
'''
from net.krezac.robot.irena.gps.GPGGAParser import GPGGAParser
import math

class NmeaReader():
    def deg2rad(self, deg):
        #print "deg", deg
        rr = deg[0]*math.pi/180.0,deg[1]*math.pi/180.0
        #print "rad",rr
        return rr
    
    def rad2xy(self, coord):
        RADIUS = 6373000
        xy = RADIUS*coord[1]*math.cos(coord[0]), RADIUS*coord[0]
        #print "xy",xy
        return xy
    
    def readFile(self, fileName):
        f = open(fileName, 'r')
        polarCoords = []
        latCen = 0
        lonCen = 0
        for sentence in f:
            if sentence.startswith("$GPGGA"):
                gga = GPGGAParser(sentence)
                polarCoords.append((gga.latitude, gga.longitude))
                latCen += gga.latitude
                lonCen += gga.longitude
        f.close()
        cartesianCoords = map(self.rad2xy,map(self.deg2rad,polarCoords))        
        f2 = open("out2.txt", 'w')
        for coord in cartesianCoords:
            f2.write("{0}\t{1}\n".format(coord[0], coord[1]))
        f2.close()

    
if __name__ == '__main__':
    #reader = NmeaReader()
    #reader.readFile('stromovka.nmea')
    #oo = deg2rad((1,1))
    #print "oo", oo
    #print rad2xy(deg2rad((50.165367,16.277153)))
    #print rad2xy(deg2rad((50.166383,16.278158)))
    pass