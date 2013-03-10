# -*- coding: utf-8 -*-
'''
Created on 07.04.2012

@author: gena
'''

from __future__ import division
from math import sqrt
import os
from PyQt4 import QtCore, QtGui
from ltcore.chamber import Chamber     

class NewRunRestAnalyser(QtCore.QObject):
    
    outString = '{:>25}; {:5}; {:18.6f}; {:18.6f};   {};\n'
    #sample, interval, activity, speed, fileName
    signalAnalysisStarted = QtCore.pyqtSignal(int)
    signalNextFileAnalysing = QtCore.pyqtSignal(str, int)
    signalAnalysisFinished = QtCore.pyqtSignal()
    
    errorNoErrors = 0
    errorLongMissedInterval = -1
    
    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(NewRunRestAnalyser, self).__init__(parent)
        self.intervalDuration = 300.0 # Interval 5 minutes
        self.quantDuration = 1.0      # Length of quant 
        self.speedThreshold = 5.0 # For imago
        #self.speedThreshold = 0.4 # For larva
        
        # Error detection parameters
        self.maxMissedIntervalDuration = 2.0 # Seconds
        self.maxMissedIntervalCount = 5
        self.errorSpeedThreshold = 50.0 # mm/s
        '''
        Speed run/rest threshold 
            0.4 mm/s for imago (smoothed trajectory)
            5.0 mm/s for imago (raw trajectory)
        '''
        self.analyseFromFilesRunning = False
    
    def setErrorThreshold(self, value):
        self.errorSpeedThreshold = value
        
    def setSpeedThreshold(self, value):
        self.speedThreshold = value
        
    def setIntervalDuration(self, value):
        self.intervalDuration = value
    
    def checkForErrors(self, trajectory, scale, frameRate):
        '''
        Check trajectory for errors 
        and return 0 if trajectory sutable for analysis
        '''
        def isError(frame1,frame2,ltobject1,ltObject2) :
            if ltObject2 is None :
                return -1
            x1,y1 = ltObject1.center
            x2,y2 = ltObject2.center
            length = sqrt((x2-x1)**2 + (y2-y1)**2)
            time = (frame2-frame1)/frameRate
            if length/time > self.errorSpeedThreshold :
                return -2
            else :
                return 0
        
        missedFramesCount = 0  # Number of bad frames 
        missedIntervalsCount = 0
        startFrame, endFrame = trajectory.bounds()
        # Start frame always not none
        frame1 = startFrame 
        ltObject1 = trajectory[startFrame]
        # Cycle by all frames
        for frame2 in xrange(startFrame+1, endFrame):
            ltObject2 = trajectory[frame2]
            # Check is object present
            frame2Status = isError(frame1,frame2,ltObject1,ltObject2) 
            if frame2Status < 0 :
                if frame2Status == -1 :
                    print "*** Object not found at frame {}".format(frame2)
                else :
                    print "*** Speed too much at frame {}".format(frame2)
                # Check, if we start new missed interval
                if missedFramesCount == 0:
                    missedIntervalsCount += 1
                    if missedIntervalsCount > self.maxMissedIntervalCount :
                        return -2
                missedFramesCount += 1
                if missedFramesCount / frameRate >= self.maxMissedIntervalDuration :
                    return -1
                # Continue to next frame
                continue
            if missedFramesCount > 0 :
                missedFramesCount = 0
            frame1=frame2
            ltObject1=ltObject2
        return 0
    
    def analyseFromFiles(self, resultsFileName, inputFileNames):
        '''
        Analyse all files from iterator inputFileNames and put results into file resultsFileName
        '''
        print "Starting analysis"
        #Prepare result file for writing
        resultsFile = open(resultsFileName, 'w')
        captionString = '                  Sample ;   Int;           Activity;             Speed ;\n'
        resultsFile.write(captionString)
        # Emit count of tracks to analyse
        self.signalAnalysisStarted.emit(len(inputFileNames))
        i = 0
        self.analyseFromFilesRunning = True
        for name in inputFileNames :
            # Check for emergency abort
            if not self.analyseFromFilesRunning : 
                print 'Analysis aborted'
                break
            # Signal to update GUI
            self.signalNextFileAnalysing.emit(name, i)
            i += 1
            chamber, scale, frameRate = Chamber.loadFromFile(name)
            if chamber.trajectory is not None :
                trajectory = chamber.trajectory.clone()
                # Ensure that start and end frame is not none
                trajectory.strip()
                errorStatus = self.checkErrors(trajectory, scale, frameRate, resultsFile) 
                if errorStatus == 0 :
                    # Create image and analyse
                    chamber.createTrajectoryImage()
                    chamber.trajectoryImage.save(name + '.png')
                    baseName = os.path.basename(str(name))
                    pos = baseName.find('.ch', -10, -1)
                    if pos >= 1 :               
                        self.analyseChamber(trajectory, scale, frameRate, baseName[:pos], resultsFile)
                elif errorStatus == -1 :
                    resultsFile.write('Too many error') 
        self.signalAnalysisFinished.emit()  
    
    def abortAnalysis(self):
        self.analyseFromFilesRunning = False
    
    def analyseChamber(self, trajectory, scale, frameRate, fileName, resultsFile):
        '''
        Analysing chamber
        '''
        # Working with linear smoothed trajectory
        
        startFrame, endFrame = trajectory.getStartEndFrame()
        # Total values
        totalRunLength = 0 # Summary length
        totalTime = (endFrame - startFrame) / frameRate # total time in seconds
        totalActivityCount = 0
        # Interval values
        intervalNumber = 1 # Current interval number
        intervalRunLength = 0 # Run Length on current interval
        intervalActivityCount = 0 # Activity count on this frame

        missedFrames = 0
        missedCount = 0
        ltObject1 = None
        for frame2 in xrange(startFrame, endFrame): # Cycle for all points
            # Check for emergency abort
            if not self.analyseFromFilesRunning :
                logFile.write()
                return
            # trying to find positive coordinates
            ltObject2 = smoothedTrajectory[frame2]
            if (frame2 - startFrame) / frameRate > self.intervalDuration * intervalNumber :
                #next interval started
                logFile.write(self.outString.format(chamber.sampleName, intervalNumber,
                                                    ((intervalActivityCount / frameRate) / self.intervalDuration),
                                                    intervalRunLength / self.intervalDuration, fileName))
                intervalNumber += 1
                intervalRunLength = 0
                intervalActivityCount = 0
                if ltObject2 is None: # Interval ended on error -- we need to reinit next point
                    print "*** Object not found at frame {}".format(frame2)
                    ltObject1 = None
                    continue
            if ltObject2 is None : # need next point without errors
                print "*** Object not found at frame {}".format(frame2)
                if missedFrames == 0:
                    missedCount += 1
                    if missedCount > 5 :
                        print '*** Analysis aborted'
                    logFile.write('*** Aborted with to much missed intervals; {}\n'.format(fileName))
                missedFrames += 1
                if missedFrames / chamber.frameRate >= 2.0 :
                    print '*** Analysis aborted'
                    logFile.write('*** Aborted with missed object at frame {}; {}\n'.format(frame2, fileName))
                    return
                continue
            missedFrames = 0
            if ltObject1 is None : # no previous point -- store and continue
                ltObject1 = ltObject2
                frame1 = frame2
                continue
            x1, y1 = ltObject1.center
            x2, y2 = ltObject2.center
            length = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / scale
            time = (frame2 - frame1) / frameRate
            speed = length / time
            if speed >= self.errorTreshold :
                print "*** Speed too much at frame {}-{} ".format(frame1, frame2)
                if frame2 - frame1 == 1:
                    missedCount += 1
                    if missedCount > 5 :
                        print '*** Analysis aborted'
                    logFile.write('*** Aborted with to much error intervals; {}\n'.format(fileName))
            if (frame2 - frame1) / chamber.frameRate <= 1.0 :
                    continue
                    print '*** Analysis aborted'
                    logFile.write('*** Aborted with error at frame {}-{}; {}\n'.format(frame1, frame2, fileName))
                    return
            totalRunLength += length
            intervalRunLength += length
            if speed >= self.speedTreshold :
                intervalActivityCount += frame2 - frame1 # 1 if no errors
                totalActivityCount += frame2 - frame1
            x1, y1 = x2, y2
            frame1 = frame2
            QtGui.QApplication.processEvents()
        '''
        # Last interval may be smaller - dispatching it
        lastTime = (frame2 - startFrame) / chamber.frameRate - (self.intervalDuration - 1) * intervalNumber
        if lastTime >= self.intervalDuration * (1/2) :
            logFile.write(self.outString.format(chamber.sampleName, intervalNumber,
                                                ((intervalActivityCount/chamber.frameRate) / lastTime),
                                                intervalRunLength / lastTime))
        '''
        # total output
        logFile.write(self.outString.format(chamber.sampleName, -1,
                                            ((totalActivityCount / chamber.frameRate) / totalTime),
                                            totalRunLength / totalTime, fileName))
