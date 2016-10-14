'''
Created on 20.2.2010

@author: Kamil.Rezac
'''
import math

def deg2rad(deg):
    return deg[0]*math.pi/180.0,deg[1]*math.pi/180.0

def rad2xy(coord):
            RADIUS = 6373000
            return RADIUS*coord[1]*math.cos(coord[0]), RADIUS*coord[0]

class RychnovReader():
    
    
    def readFile(self, fileName):
        f = open(fileName, 'r')
        polarCoords = []
        for line in f:
            parts = line.rsplit(" ")
            rawLat = float(parts[1])
            rawLon = float(parts[2])
            print rawLat, rawLon
            #gga = GPGGAParser(sentence)
            polarCoords.append((rawLat, rawLon))
            #latCen += gga.latitude
            #lonCen += gga.longitude
        f.close()
        cartesianCoords = map(rad2xy,map(deg2rad,polarCoords))        
        f2 = open("rychnov3.txt", 'w')
        for coord in cartesianCoords:
            f2.write("{0}\t{1}\n".format(coord[0], coord[1]))
        f2.close()

    
if __name__ == '__main__':
    reader = RychnovReader()
    reader.readFile('rychnov3.rch')
