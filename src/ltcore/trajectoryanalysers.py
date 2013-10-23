'''
Created on 10.10.2013

@author: gena
'''
from math import sqrt
from PyQt4 import QtCore, QtGui


class RunRestAnalyser(QtCore.QObject):
    #            sampleName activity  speed  freq file name
    outString = '{:>25}; {:18.6f}; {:18.6f};  {:18.6f};  {};\n'
    #               sample int  run time  run speed      file name
    outStringRuns = '{:>25}; {:5}; {:18.6f}; {:18.6f};   {};\n'
    #sample, interval, activity, speed, fileName

    
    def __init__(self, errorDetector, parent=None):
        '''
        Constructor
        '''
        super(RunRestAnalyser, self).__init__(parent)
        self.intervalDuration = 300.0 # Interval 5 minutes
        self.quantDuration = 1.0      # Length of quant 
        self.runRestSpeedThreshold = 5.0 # For imago
        self.runLengthThreshold = 0.6 # mm
        #self.runRestSpeedThreshold = 0.4 # For larva
        '''
        Speed run/rest threshold 
            0.4 mm/s for imago (smoothed trajectory)
            5.0 mm/s for imago (raw trajectory)
        '''
    
    @QtCore.pyqtSlot(float)
    def setRunRestSpeedThreshold(self, value):
        self.runRestSpeedThreshold = value
        
    @QtCore.pyqtSlot(float)
    def setIntervalDuration(self, value):
        self.intervalDuration = value
        
    @QtCore.pyqtSlot(float)
    def setQuantDuration(self, value):
        self.quantDuration = value
    
    @QtCore.pyqtSlot(QtCore.QString)
    def prepareFiles(self, resultsFileName):
        self.resultsFile = open(unicode(resultsFileName), 'w')
        self.resultFileRun = open(unicode(resultsFileName+'.run'), 'w')
        captionString = '                  Sample ;           Activity;             Speed ;       Frequency*100;    FileName;\n'
        self.resultsFile.write(captionString)
        self.resultFileRun.write('                  Sample ;   Int;       Run Duration;       Run Speed;       FileName;\n')
      
    def closeFiles(self):
        self.resultsFile.close()
        self.resultFileRun.close()
        self.resultsFile = None
        self.resultFileRun = None
    
    def analyseChamberOLd(self, trajectory, sampleName, scale, frameRate, fileName):
        '''
        Analysing chamber
        '''
        startFrame, endFrame = trajectory.bounds()
        # Total values
        totalRunLength = 0 # Summary length
        totalTime = (endFrame - startFrame) / frameRate # total time in seconds
        totalActivityCount = 0
        # Interval values
        intervalNumber = 1 # Current interval number
        intervalRunLength = 0 # Run Length on current interval
        intervalActivityCount = 0 # Activity count on this frame
        ltObject1 = None
        for frame2 in xrange(startFrame, endFrame): # Cycle for all points
            # Check for emergency abort
            '''
            if not self.analyseFromFilesRunning :
                self.resultsFile.write('Analysis aborted')
                return
            '''
            # trying to find positive coordinates
            ltObject2 = trajectory[frame2]
            if (frame2 - startFrame) / frameRate > self.intervalDuration * intervalNumber :
                #next interval started
                self.resultsFile.write(self.outString.format(sampleName, intervalNumber,
                                                    ((intervalActivityCount / frameRate) / self.intervalDuration),
                                                    intervalRunLength / self.intervalDuration, fileName))
                intervalNumber += 1
                intervalRunLength = 0
                intervalActivityCount = 0
                if ltObject2 is None: # Interval ended on error -- we need to reinit next point
                    ltObject1 = None
                    continue
            if ltObject2 is None :
                # Dismiss error frame and go to next one
                continue
            if ltObject1 is None : # no previous point -- store and continue
                ltObject1 = ltObject2
                frame1 = frame2
                continue
            
            time = frameToTime(frame2-frame1)
            if time < 1.0 :
                continue
            x1, y1 = ltObject1.center
            x2, y2 = ltObject2.center
            length = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / scale
            speed = length / time
            totalRunLength += length
            intervalRunLength += length
            #print frame1, frame2, speed
            if speed >= self.runRestSpeedThreshold :
                intervalActivityCount += frame2 - frame1 # 1 if no errors
                totalActivityCount += frame2 - frame1
            ltObject1 = ltObject2
            frame1 = frame2
            QtGui.QApplication.processEvents()
        # total output
        self.resultsFile.write(self.outString.format(sampleName, -1,
                                            ((totalActivityCount / frameRate) / totalTime),
                                            totalRunLength / totalTime, fileName))

    def analyseChamberQuant(self, trajectory, sampleName, scale, frameRate, fileName, 
                            resultsFile,resultFileRuns):
        '''
        Analysing chamber using Run-Rest and frequency 
        Don-t use interval statistics -- output all intervals as is
        '''
        def frameToTime(frame):
            return frame/frameRate
        
        startFrame, endFrame = trajectory.bounds()
        # Total values
        totalTime = frameToTime(endFrame - startFrame) # total time in seconds
        totalLength = 0       # Symmari length for all time
        totalRunDuration = 0  # Summary dutarion of run intervals
        totalRunCount = 0 
        # Value to form run periods
        runLength = 0
        runDuration = 0
        lastState = 1  #1- rest, 2 - run
        ltObject1 = None
        frame1 = None
        for frame2 in xrange(startFrame, endFrame): # Cycle for all points
            # Check for emergency abort
            
            # trying to find positive coordinates
            ltObject2 = trajectory[frame2]
            if ltObject2 is None :
                # Dismiss error frame and go to next one
                continue
            
            if ltObject1 is None : # no previous point -- store and continue
                ltObject1 = ltObject2
                frame1 = frame2
                continue
            time = frameToTime(frame2-frame1)
            if time < self.quantDuration : # Wait for quant end
                continue
            # If we are here -- we have all needed to calculate speed
            x1, y1 = ltObject1.center
            x2, y2 = ltObject2.center
            length = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / scale
            totalLength += length
            speed = length / time
            if speed >= self.runRestSpeedThreshold :
                # This is Activity
                totalRunDuration+=time
                if lastState == 1 : # Starting new activity period
                    lastState = 2
                    runLength = length
                    runDuration = time
                    totalRunCount +=1
                else : # Previous quant was activity
                    runLength+=length
                    runDuration+=time
            else :
                # This is Rest
                if lastState == 2 : # Finished activity period
                    lastState = 1
                    currentTime = frameToTime(frame2-startFrame)
                    interval = int(currentTime/self.intervalDuration)+1
                    s = self.outStringRuns.format(sampleName, interval, runDuration, 
                                                  runLength/runDuration, fileName)
                    self.resultFileRuns.write(s)
                    # Reset run
                  
            ltObject1 = ltObject2
            frame1 = frame2
            QtGui.QApplication.processEvents()
        # total output
        self.resultsFile.write(self.outString.format(sampleName, totalRunDuration / totalTime,
                                            totalLength / totalTime, (totalRunCount/totalTime)*100, fileName))

    def analyseChamber(self, trajectory, sampleName, scale, frameRate, fileName):
        '''
        Analysing chamber using Run-Rest and frequency 
        Don-t use interval statistics -- output all intervals as is
        '''
        def frameToTime(frame):
            return frame/frameRate
        
        startFrame, endFrame = trajectory.bounds()
        # Total values
        totalTime = frameToTime(endFrame - startFrame) # total time in seconds
        totalLength = 0       # Symmari length for all time
        totalRunDuration = 0  # Summary dutarion of run intervals
        totalRunCount = 0 
        # Value to form run periods
        runLength = 0
        runDuration = 0
        lastState = 1  #1- rest, 2 - run
        ltObject1 = None
        frame1 = None
        for frame2 in xrange(startFrame, endFrame): # Cycle for all points
            # Check for emergency abort
            
            # trying to find positive coordinates
            ltObject2 = trajectory[frame2]
            if ltObject2 is None :
                # Dismiss error frame and go to next one
                continue
            
            if ltObject1 is None : # no previous point -- store and continue
                ltObject1 = ltObject2
                frame1 = frame2
                continue
            time = frameToTime(frame2-frame1)
            if time < self.quantDuration : # Wait for quant end
                continue
            # If we are here -- we have all needed to calculate speed
            x1, y1 = ltObject1.center
            x2, y2 = ltObject2.center
            length = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / scale
            totalLength += length
            speed = length / time
            if speed >= self.runRestSpeedThreshold :
                # This is Activity
                totalRunDuration+=time
                if lastState == 1 : # Starting new activity period
                    lastState = 2
                    runLength = length
                    runDuration = time
                    totalRunCount +=1
                else : # Previous quant was activity
                    runLength+=length
                    runDuration+=time
            else :
                # This is Rest
                if lastState == 2 : # Finished activity period
                    # Reset run
                    lastState = 1
                    '''
                    currentTime = frameToTime(frame2-startFrame)
                    interval = int(currentTime/self.intervalDuration)+1
                    s = self.outStringRuns.format(sampleName, interval, runDuration, 
                                                  runLength/runDuration, fileName)
                    self.resultFileRuns.write(s)
                    '''        
            ltObject1 = ltObject2
            frame1 = frame2
            QtGui.QApplication.processEvents()
        # total output
        self.resultsFile.write(self.outString.format(sampleName, totalRunDuration / totalTime,
                                            totalLength / totalTime, (totalRunCount/totalTime)*100, fileName))
class RatRunAnalyser(QtCore.QObject):
    #            sample name 
    outString = '{:>25}; {:18.6f}; {:18.6f};  {:6.2f}; {:6.2f}; {:6.2f}; {:6.2f};  {:7.2f}; {:7.2f}; {:7.2f}; {:7.2f};\n'
    #
    
    def __init__(self, errorDetector, parent=None):
        '''
        Constructor
        '''
        super(RatRunAnalyser, self).__init__(parent)    
    
    @QtCore.pyqtSlot(QtCore.QString)
    def prepareFiles(self, resultsFileName):
        self.resultsFile = open(unicode(resultsFileName), 'w')
        captionString = '                  Sample ;           Activity;             Speed ;       Frequency*100;    FileName;\n'
        self.resultsFile.write(captionString)

      
    def closeFiles(self):
        self.resultsFile.close()
        self.resultsFile = None

    def analyseChamber(self, trajectory, sampleName, sizeX, sizeY, scale, frameRate, resultsFile):
        '''
        Analysing chamber
        '''
        
        def frameToTime(frame):
            return frame/frameRate
        
        startFrame, endFrame = trajectory.bounds()
        meanX = sizeX/2
        meanY = sizeY/2
        # Total values
        totalTime = frameToTime(endFrame - startFrame) # total time in seconds
        totalLength = 0 # Summary length
        
        quadrantTime = [[0,0],
                          [0,0]]  # counts in each quadrant
        quadrantLength = [[0,0],
                          [0,0]]  # counts in each quadrant
        # Interval values
        ltObject1 = None
        for frame2 in xrange(startFrame, endFrame): # Cycle for all points
            # Check for emergency abort
            '''
            if not self.analyseFromFilesRunning :
                resultsFile.write('Analysis aborted')
                return
            '''
            # trying to find positive coordinates
            ltObject2 = trajectory[frame2]
            if ltObject2 is None :
                # Dismiss error frame and go to next one
                continue
            if ltObject1 is None : # no previous point -- store and continue
                ltObject1 = ltObject2
                continue
            x1, y1 = ltObject1.center
            x2, y2 = ltObject2.center
            if x2 < meanX :
                xQuadrant=0
            else :
                xQuadrant=1
            if y2 < meanY :
                yQuadrant =0
            else :
                yQuadrant=1
            quadrantTime[xQuadrant][yQuadrant] +=1
            length = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / scale
            totalLength += length
            quadrantLength[xQuadrant][yQuadrant] +=length
            ltObject1 = ltObject2
            QtGui.QApplication.processEvents()
        # total output
        totalFrames=(endFrame - startFrame)
        quadrantTime[0][0]= quadrantTime[0][0]/totalFrames
        quadrantTime[0][1]= quadrantTime[0][1]/totalFrames
        quadrantTime[1][0]= quadrantTime[1][0]/totalFrames
        quadrantTime[1][1]= quadrantTime[1][1]/totalFrames      
        # total output
        self.resultsFile.write(self.outString.format(sampleName, totalTime, totalLength,
             quadrantTime[0][0],quadrantTime[0][1],quadrantTime[1][0], quadrantTime[1][1], 
             quadrantLength[0][0], quadrantLength[0][1], quadrantLength[1][0], quadrantLength[1][1]))
        
        
