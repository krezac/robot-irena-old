from itertools import islice, izip
import math

FAR_AWAY = 256.0    # A dummy far-away distance used instead of zeros in laser scans. [m]

class VFH:
    '''
    VFH+ implementation. No long-term memory is used, only the obstacles in the last laser scan are taken in account.

    The laser is expected to be mounted on the axis in the robot's facing direction.

    Modeled after "VFH+: Reliable Obstacle Avoidance for Fast Mobile Robots", I. Ulrich and J. Borenstein.
    '''
    def __init__(self, laserFOV = math.radians(270), blockingDistance = 0.35, safetyDistance = 0.5, maxRange = 1.4, turnRadius = None, mu1 = 5, mu2 = 2, mu3 = 3, binSize = math.radians(5), verbose = False):
        '''
        Params:
            laserFOV            ... Field of view of the laser. [rad]
            safetyDistance      ... This is a minimal planned distance from obstacles. [m]
            maxRange            ... Reading further than this threshold are ignored. This makes it possible to use a laser pointing to the ground. [m]
            turnRadius          ... The maximal turning trajectory of the robot is approximated with a circle with this radius. If None, a holonomic robot is assumed. [m]
            mu1, mu2, mu3       ... Parameters of the cost function. mu1 is a weight of a difference between a candidate direction annd the goal direction; mu2 is a weight of a difference between a candidate direction and the current steering direction; mu3 is a weight of difference between a candidate direction and the previously selected direction. mu1 > mu2 + mu3 must hold. TODO: mu2 is currently not used.
            binSize             ... Angular width of the bins in the histograms. laserFOV should be divisible by binSize. [rad]
            verbose             ... If verbose is set to True, some debugging information may be printed.
        '''
        self.scan = None # Laser scan in meters, right side first
        self.laserFOV = laserFOV
        self.blockingDistance = blockingDistance
        self.safetyDistance = safetyDistance
        self.maxRange = maxRange
        self.turnRadius = turnRadius
        self.mu1 = mu1
        self.mu2 = mu2
        self.mu3 = mu3
        self.binSize = binSize
        self.verbose = verbose

    def __bin(self, angle):
        ''' Find an index of a bin which the angle falls to. '''
        return int( (angle + self.laserFOV / 2.0) / self.binSize)

    def __angle(self, bin):
        ''' Find an angle corresponding to the given bin. '''
        return bin * self.binSize + self.binSize / 2.0 - self.laserFOV / 2.0

    def __obstDir(self, i):
        ''' Compute a direction to the obstacle from the scan index. '''
        return self.laserFOV * i / (len(self.scan) - 1.0) - self.laserFOV / 2.0

    def update(self, data):
        scan = [ FAR_AWAY if x == 0 else x for x in data ]
        self.scan = scan

    def isBlocked(self):
        '''Return True if there is an obstacle within self.safetyDistance in front of the robot.'''
        if self.scan is None:
            return True # better safe than sorry
        print "Blocked cond", self.blockingDistance, min(self.scan)
        return any( ( x < self.blockingDistance for x in self.scan ) )

    def navigate(self, goalDir, prevDir = 0.0, extraObs = []):
        ''' Find a direction to the goal avoiding obstacles visible in the last scan.

        Param:
             goalDir ... A direction to the goal. [rad]
             prevDir ... A previously selected steering direction. [rad]
             extraObs ... A list of extra obstacles. An obstacle is specified in local polar coordinates as a pair (angle, distance) [(rad, m)].
        Return:
             Either a preferred direction [rad, counter-clockwise], or None.
             None is returned whenever there is an obstacle very near or no direction seems reasonable.
        '''
        if self.scan is None:
            print "No scan"
            return None

        if self.isBlocked():
            print "Blocked"
            return None

        polarHistogram = self.__polarHistogram(extraObs)
        if polarHistogram is None:
            print "No polar histogram"
            return None
        binaryPolarHistogram = self.__binaryPolarHistogram(polarHistogram)
        maskedPolarHistogram = self.__maskedPolarHistogram(binaryPolarHistogram)
        openWindows = self.__openWindows(maskedPolarHistogram)
        candidates = self.__candidates(openWindows, goalDir)
        dir = self.__bestCandidate(candidates, goalDir, prevDir)
        if self.verbose:
            s = [ 'x' if x else ' ' for x in maskedPolarHistogram]
            if dir is not None:
                i = self.__bin(dir)
                s = s[:i] + ['.'] + s[i:]
            s = ''.join(s)
            print "'" + s[::-1] + "'"
        print "Dir", dir 
        return dir

    def __polarHistogram(self, extraObs = []):
        c2 = 1.0 # Certainty squared. We trust the laser, thus 1.0**2.
        a = 0.5 #TODO: How should we set this parameter?
        ws = 0.2 # TODO: ? [m]
        b = (a - 1.0) * 4.0/ ( (ws-1.0) **2 )
        self.__histogramThreshold = c2 * (a - b * (self.maxRange * 0.5)**2) #TODO: This is an ad-hoc unsupported decision. Note: It seems to work, though.

        polarHistogram = [0.0] * (1 + self.__bin(self.laserFOV / 2.0))
        obstacles = [ (beta, d) for (beta, d) in extraObs if d <= self.maxRange ]
        for i in range(len(self.scan)):
            d = self.scan[i] # distance [m]
            if d > self.maxRange:
                continue
            beta = self.__obstDir(i) # direction to the obstacle [rad]
            obstacles.append( (beta, d) )

        for (beta, d) in obstacles:
            m = c2 * (a - b * d**2) # cell magnitude
            if d < self.blockingDistance: # we are within the safety distance from an obstacle
                return None
            ratio = self.safetyDistance / d
            # if we are within the safetyDistance, asin is undefined => let's HACK
            if ratio > 1.0:
                ratio = 1.0
            elif ratio < -1.0:
                ratio = -1.0
            gamma = math.asin(ratio) # enlargement angle [rad]

            low = max(0, self.__bin( beta - gamma ))
            high = min(len(polarHistogram), self.__bin( beta + gamma ))
            for j in range(low, high):
                polarHistogram[j] += m

        return polarHistogram

    def __binaryPolarHistogram(self, polarHistogram):
        return [ x > self.__histogramThreshold for x in polarHistogram ] #NOTE: No hysteresis. (Unlike in the article)

    def __maskedPolarHistogram(self, binaryPolarHistogram):
        if self.turnRadius is None: # A holonomic robot.
            return binaryPolarHistogram 
        else:
            # !!!!!!
            # Note: The implementation below differs from the one in The Article in that:
            #                 a) This one uses polar coordinates.
            #                 b) This one knows, that even an obstacle on the left can block turning to the right.

            left = +self.laserFOV / 2.0
            right = -self.laserFOV / 2.0

            for i in xrange(len(self.scan)):
                if self.scan[i] > self.maxRange:
                    continue

                d2 = self.scan[i]**2
                beta = self.__obstDir(i) # An angle to the obstacle relative to the facing direction. [m]
                if beta > right: # Right-turning to this direction is not blocked yet.
                    gammaR =    beta - (-math.pi) / 2 # Angle to the center of a right-turning trajectory ("right center").
                    dr2 = d2 + self.turnRadius**2 - 2 * self.scan[i] * self.turnRadius * math.cos(gammaR) # A squared distance of the obstacle from the right center
                    if dr2 < (self.turnRadius + self.safetyDistance)**2: # A right-blocking obstacle.
                        right = beta

                if beta < left: # Left-turning to this direction is not blocked yet.
                    gammaL = beta - math.pi / 2 # Angle to the center of a left-turning trajectory ("left center").
                    dl2 = d2 + self.turnRadius**2 - 2 * self.scan[i] * self.turnRadius * math.cos(gammaL) # A squared distance of the obstacle from the left center. 
                    if dl2 < (self.turnRadius + self.safetyDistance)**2: # A left-blocking obstacle.
                        left = beta

            li = self.__bin(left)
            ri = self.__bin(right)

            return [ False if binaryPolarHistogram[i] == False and i >= ri and i <= li else True for i in xrange(len(binaryPolarHistogram)) ]

    def __openWindows(self, maskedPolarHistogram):
        openWindows = []
        prev = True

        for i in xrange(1 + len(maskedPolarHistogram)):
            mask = True if i == len(maskedPolarHistogram) else maskedPolarHistogram[i]
            if prev == True and mask == False: # Right edge of a window.
                right = self.__angle(i)

            if prev == False and mask == True: # Left edge of a window.
                left = self.__angle(i - 1)
                openWindows.append( (right,left) )

            prev = mask

        return openWindows

    def __candidates(self, openWindows, goalDir):
        candidates = []

        for (right, left) in openWindows:
            if goalDir >= right and goalDir <= left:
                candidates.append(goalDir)

            # Note: Not distinguishing wide and narrow openings as in The Article.
            candidates.append(right)
            candidates.append(left)

        return candidates

    def __bestCandidate(self, candidates, goalDir, prevDir):
        bestDir = None
        bestCost = None

        for dir in candidates:
            cost = self.mu1 * abs(dir - goalDir) + self.mu3 * abs(dir - prevDir) #TODO: mu2
            if bestDir is None or cost < bestCost:
                bestDir = dir
                bestCost = cost

        return bestDir

    def __remask(self, mask, n):
        ''' Rescales the mask to the given length.'''
        m = len(mask)

        if m == n:
            return mask # no need to do anything

        return [ mask[int(round(i * (m - 1) / float(n - 1)))] for i in xrange(n) ]

