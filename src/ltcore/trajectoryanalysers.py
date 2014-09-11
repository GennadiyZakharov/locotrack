'''
Created on 10.10.2013

@author: gena
'''
from __future__ import division
from math import sqrt
from PyQt4 import QtCore, QtGui
from ltcore.trajectorystats import TrajectoryStats,IntervalStats


class RunRestAnalyser(QtCore.QObject):
    #            sampleName activity  speed  freq file name
    outString = '{:>25}; {:10.4f}; {:10.4f};  {:10.4f}; {:10.4f}; {:6.2f}; {:6.2f}; {:6.2f}; {:6.2f};  {:10.2f}; {:10.2f}; {:10.2f}; {:10.2f}; {};\n'
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
    def setRunLengthThreshold(self, value):
        self.runLengthThreshold = value
        
    @QtCore.pyqtSlot(float)
    def setIntervalDuration(self, value):
        self.intervalDuration = value
        
    @QtCore.pyqtSlot(float)
    def setQuantDuration(self, value):
        self.quantDuration = value
    
    @QtCore.pyqtSlot(QtCore.QString)
    def prepareFiles(self, resultsFileName):
        self.resultsFile = open(unicode(resultsFileName), 'w')
        self.resultFileRuns = open(unicode(resultsFileName+'.run'), 'w')
        captionString = '                  Sample ;   Activity; TotalSpeed;    RunSpeed;   Freq*100;Time:[0,0];[0,1]; [1,0];  [1,1];Length:[0,0];      [0,1];      [1,0];      [1,1]; FileName;\n'
        self.resultsFile.write(captionString)
        self.resultFileRuns.write('                  Sample ;   Int;       Run Duration;       Run Speed;       FileName;\n')
      
    def closeFiles(self):
        self.resultsFile.close()
        self.resultFileRuns.close()
        self.resultsFile = None
        self.resultFileRuns = None

    
    def analyseChamber(self, chamber, scale, frameRate):
        '''
        Analysing chamber using Run-Rest and frequency 
        Don-t use interval statistics -- output all intervals as is
        Mean speed is printed twice -- mean for all time nd mean run time (using RunRest threshold)
        '''
        def frameToTime(frame):
            return frame/frameRate
        
        trajectoryStats = TrajectoryStats()
        trajectoryStats.setBounds(chamber.rect.size())
        meanX, meanY = chamber.width()/2, chamber.height()/2
        trajectoryStats.setCenter(meanX, meanY)
        trajectory = chamber.trajectory
        startFrame, endFrame = trajectory.bounds()
        # Total values
        trajectoryStats.totalDuration = frameToTime(endFrame - startFrame) # total time in seconds
        #trajectoryStats.intervalDuration = self.intervalDuration
        # Value to form run periods
        runLength = 0
        runDuration = 0
        lastState = 1  #1- rest, 2 - run
        
        ltObject1 = None
        frame1 = None
        for frame2 in xrange(startFrame, endFrame): # Cycle for all points
            # Check for emergency abort
            # TODO: Do this
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
            speed = length / time
            # Assign current point to quadrant
            if x2 < meanX :
                xQuadrant=0
            else :
                xQuadrant=1
            if y2 < meanY :
                yQuadrant =0
            else :
                yQuadrant=1
            # Updating data
            trajectoryStats.totalLength += length
            trajectoryStats.quadrantTotalDuration[xQuadrant][yQuadrant] +=time
            trajectoryStats.quadrantTotalLength[xQuadrant][yQuadrant] +=length
            if speed >= self.runRestSpeedThreshold :
                # This is Activity
                trajectoryStats.totalRunDuration+=time
                trajectoryStats.runLength += length
                trajectoryStats.quadrantRunDuration[xQuadrant][yQuadrant] +=time
                trajectoryStats.quadrantRunLength[xQuadrant][yQuadrant] +=length
                if lastState == 1 : # Starting new activity period
                    lastState = 2
                    runLength = length
                    runDuration = time
                    trajectoryStats.runCount +=1
                else : # Previous quant was activity
                    runLength+=length
                    runDuration+=time
            else :
                # This is Rest
                if lastState == 2 : # Finished activity period
                    # Reset run
                    lastState = 1
                    #
                    '''
                    currentTime = frameToTime(frame2-startFrame)
                    interval = int(currentTime/self.intervalDuration)+1
                    intervalStats = IntervalStats()
                    intervalStats.totalDuration = time
                    intervalStats.runDuration = runDuration
                    intervalStats.runLength = runLength
                    trajectoryStats.intervals.append(intervalStats)
                    '''
                            
            ltObject1 = ltObject2
            frame1 = frame2
            QtGui.QApplication.processEvents()
        # total output
        return trajectoryStats
        
class RatRunAnalyser(QtCore.QObject):
    #            sample name 
    outString = '{:>25}; {:18.6f}; {:18.6f};  {:6.2f}; {:6.2f}; {:6.2f}; {:6.2f};  {:10.2f}; {:10.2f}; {:10.2f}; {:10.2f}; {};\n'
    #
    
    def __init__(self, errorDetector, parent=None):
        '''
        Constructor
        '''
        super(RatRunAnalyser, self).__init__(parent)    
    
    @QtCore.pyqtSlot(QtCore.QString)
    def prepareFiles(self, resultsFileName):
        self.resultsFile = open(unicode(resultsFileName), 'w')
        captionString = '                  Sample ;Record total time,s; Avg run speed,mm/s;Time:[0,0]; [0,1];  [1,0];  [1,1]; Length:[0,0];     [0,1];      [1,0];      [1,1];    FileName;\n'
        self.resultsFile.write(captionString)

      
    def closeFiles(self):
        self.resultsFile.close()
        self.resultsFile = None

    def analyseChamber(self, trajectory, sampleName, sizeX, sizeY, scale, frameRate, aviName):
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
        self.resultsFile.write(self.outString.format(sampleName, totalTime, totalLength/totalTime,
             quadrantTime[0][0],quadrantTime[0][1],quadrantTime[1][0], quadrantTime[1][1], 
             quadrantLength[0][0], quadrantLength[0][1], quadrantLength[1][0], quadrantLength[1][1],aviName))
        
        
