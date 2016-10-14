'''
Created on Jun 30, 2010

@author: krezac
'''
import sys

if __name__ == '__main__':
    logName = sys.argv[1]
    newLogName = sys.argv[1] + "_new.rbl"
    oldLog = open(logName, "rb")
    newLog = open(newLogName, "wb")
    data = oldLog.read()
    dataByte = False
    bitCount = 0
    timeoutCount = 0
    for b in data:
        bitCount += 1
        if dataByte:
            #print "data"
            newLog.write(b)
            dataByte = False
        else:
            #print "control"
            if b == "\x01": # write to bus
                newLog.write("\x00")
                dataByte = True
            elif b == "\x02": # read from buss
                newLog.write("\x01")
                dataByte = True
            elif b == "\x03": # timeout
                #print "timeout"
                timeoutCount += 1
                newLog.write("\x02")
                newLog.write("\xFF")
                pass # next byte will be control again
            else:
                print "bad control byte"
                sys.exit()
        
    newLog.close()
    oldLog.close()
    print "Timeouts:", timeoutCount