# -*- coding: utf-8 -*-
'''
Created on 07.04.2012

@author: gena
'''

from __future__ import division
from math import sqrt
import numpy as np
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
    errorTooLongMissedInterval = -1
    errorTooMuchMissedIntervals = -2
    imageMargin = 10
    
    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(NewRunRestAnalyser, self).__init__(parent)
        self.intervalDuration = 300.0 # Interval 5 minutes
        self.quantDuration = 1.0      # Length of quant 
        self.runRestSpeedThreshold = 5.0 # For imago
        #self.runRestSpeedThreshold = 0.4 # For larva
        
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
        self.imageLevels = 3
        self.imageCreators = [self.createImageLines, self.createImageDots]
        self.imageCreatorsCaptions = ['Lines','Dots (accumulate)']
        self.imageCreator = self.createImageDots
        self.setWriteSpeed(0)
    
    @QtCore.pyqtSlot(int)
    def setWriteSpeed(self, checked):
        self.writeSpeedInfo = checked
      
    @QtCore.pyqtSlot(int)
    def setImageCreator(self, index):
        self.imageCreator = self.imageCreators[index]
    
    @QtCore.pyqtSlot(int)
    def setImageLevelsCount(self, value):
        self.imageLevels = value
    
    @QtCore.pyqtSlot(float)
    def setMaxMissedIntervalDuration(self, value):
        self.maxMissedIntervalDuration = value
    
    @QtCore.pyqtSlot(int)
    def setMaxMissedIntervalCount(self, value):
        self.maxMissedIntervalCount = value
    
    @QtCore.pyqtSlot(float)
    def setErrorSpeedThreshold(self, value):
        self.errorSpeedThreshold = value
        
    @QtCore.pyqtSlot(float)
    def setRunRestSpeedThreshold(self, value):
        self.runRestSpeedThreshold = value
        
    @QtCore.pyqtSlot(float)
    def setIntervalDuration(self, value):
        self.intervalDuration = value
    
    def createImageDots(self, trajectory):
        '''
        Create trajectory image in dots representation
        '''
        minX,minY, maxX,maxY = trajectory.minMax()
        trajectoryImage = QtGui.QImage(maxX-minX + self.imageMargin * 2,
            maxY-minY + self.imageMargin * 2, QtGui.QImage.Format_RGB888)
        trajectoryImage.fill(QtCore.Qt.white)
        step = 255 // self.imageLevels
        displace = QtCore.QPoint(self.imageMargin-minX,self.imageMargin-minY)
        for ltObject in trajectory :
            if ltObject is None :
                continue
            point = self.ltObjectToPoint(ltObject,displace)
            color = trajectoryImage.pixel(point)
            level = color & 255
            newLevel = max(0, level - step)
            trajectoryImage.setPixel(point, QtGui.QColor(newLevel, newLevel, newLevel).rgb())
            QtGui.QApplication.processEvents()
        return trajectoryImage
    
    def ltObjectToPoint(self, ltObject, displace):
        return QtCore.QPointF(*ltObject.center).toPoint()+displace
    
    def createImageLines(self, trajectory):
        '''
        Create trajectory image in lines representation
        '''   
        minX,minY,maxX,maxY = trajectory.minMax()
        displace = QtCore.QPoint(self.imageMargin-minX,self.imageMargin-minY)
        trajectoryImage = QtGui.QImage(maxX-minX + self.imageMargin * 2,
            maxY-minY + self.imageMargin * 2, QtGui.QImage.Format_ARGB32_Premultiplied)
        trajectoryPainter = QtGui.QPainter(trajectoryImage)
        trajectoryPainter.setPen(QtCore.Qt.black)
        trajectoryImage.fill(QtCore.Qt.white)
        ltObject1 = None
        for ltObject2 in trajectory :
            if ltObject2 is None : continue
            if ltObject1 is None :
                ltObject1 = ltObject2
                continue
            trajectoryPainter.drawLine(self.ltObjectToPoint(ltObject1,displace),
                                       self.ltObjectToPoint(ltObject2,displace))
            ltObject1=ltObject2
            QtGui.QApplication.processEvents()
        trajectoryPainter.end()
        return trajectoryImage
     
    @QtCore.pyqtSlot(QtCore.QString, QtCore.QStringList)   
    def analyseFromFiles(self, resultsFileName, inputFileNames):
        '''
        Analyse all files from iterator inputFileNames and put results into file resultsFileName
        '''
        #Prepare result file for writing
        resultsFile = open(resultsFileName, 'w')
        captionString = '                  Sample ;   Int;           Activity;             Speed ;    FileName;\n'
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
            baseName = os.path.basename(str(name))
            pos = baseName.find('.ch')
            if pos < 0 : 
                continue  
            # Signal to update GUI
            i += 1
            self.signalNextFileAnalysing.emit(name, i)
            QtGui.QApplication.processEvents()
            chamber, scale, frameRate = Chamber.loadFromFile(name)
            if chamber.trajectory is None : 
                continue
            trajectory = chamber.trajectory.clone()
            # Ensure that start and end frame is not none
            trajectory.strip()
            # speed info
            spdName = name+'.spd' if self.writeSpeedInfo != 0 else None
            errorStatus = self.checkForErrors(trajectory, scale, frameRate, spdName) 
            if errorStatus == self.errorNoErrors :
                # Create image and analyse   
                self.analyseChamber(trajectory, chamber.sampleName, scale, frameRate, baseName[:pos], resultsFile)
                image = self.imageCreator(trajectory)
                image.save(name + '.png')         
            elif errorStatus == self.errorTooMuchMissedIntervals :
                resultsFile.write('Too much missed intervals; {};\n'.format(baseName[:pos])) 
            elif errorStatus == self.errorTooLongMissedInterval :
                resultsFile.write('Too long missed interval; {};\n'.format(baseName[:pos])) 
                    
        self.signalAnalysisFinished.emit()  
    
    @QtCore.pyqtSlot()
    def abortAnalysis(self):
        self.analyseFromFilesRunning = False
    
    def checkForErrors(self, trajectory, scale, frameRate, spdFileName=None):
        '''
        Check trajectory for errors 
        and return 0 if trajectory suitable for analysis
        '''
        def getSpeed(frame1, frame2, ltObject1, ltObject2):
            if ltObject2 is None :
                return None
            x1, y1 = ltObject1.center
            x2, y2 = ltObject2.center
            length = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / scale
            time = (frame2 - frame1) / frameRate
            return length / time
            
        if spdFileName is not None:
            spdFile = open(spdFileName, 'w')
        missedFramesCount = 0  # Number of bad frames 
        missedIntervalsCount = 0
        startFrame, endFrame = trajectory.bounds()
        # Start frame always not none (trajectory stripped)
        frame1 = startFrame 
        ltObject1 = trajectory[startFrame]
        # Cycle by all frames
        for frame2 in xrange(startFrame + 1, endFrame):
            ltObject2 = trajectory[frame2]
            # Check is frame2 buggy
            speed = getSpeed(frame1, frame2, ltObject1, ltObject2)
            if (speed is None) or (speed > self.errorSpeedThreshold):  
                # An error -- print error message
                if speed is None :
                    print "*** Object not found at frame {}".format(frame2)
                else :
                    print "*** Speed too much at frame {}".format(frame2)
                # Check, if we start new missed interval
                if missedFramesCount == 0:
                    missedIntervalsCount += 1
                    if missedIntervalsCount > self.maxMissedIntervalCount :
                        return self.errorTooMuchMissedIntervals
                missedFramesCount += 1
                if missedFramesCount / frameRate >= self.maxMissedIntervalDuration :
                    return self.errorTooLongMissedInterval
                # Continue to next frame
                continue
            # If we are here -- we found good frame -- missed intervals ended
            if missedFramesCount > 0 :
                missedFramesCount = 0
            #
            if spdFileName is not None:
                spdFile.write('{:5}  {:18.6f}\n'.format(frame1, speed)) 
            #
            frame1 = frame2
            ltObject1 = ltObject2
            QtGui.QApplication.processEvents()
        # If we here -- trajectory ended, all OK
        return self.errorNoErrors
    
    def analyseChamber(self, trajectory, sampleName, scale, frameRate, fileName, resultsFile):
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
            if not self.analyseFromFilesRunning :
                resultsFile.write('Analysis aborted')
                return
            # trying to find positive coordinates
            ltObject2 = trajectory[frame2]
            if (frame2 - startFrame) / frameRate > self.intervalDuration * intervalNumber :
                #next interval started
                resultsFile.write(self.outString.format(sampleName, intervalNumber,
                                                    ((intervalActivityCount / frameRate) / self.intervalDuration),
                                                    intervalRunLength / self.intervalDuration, fileName))
                intervalNumber += 1
                intervalRunLength = 0
                intervalActivityCount = 0
                if ltObject2 is None: # Interval ended on error -- we need to reinit next point
                    ltObject1 = None
                    continue
            if ltObject2 is None : # need next point without errors
                continue
            if ltObject1 is None : # no previous point -- store and continue
                ltObject1 = ltObject2
                frame1 = frame2
                continue
            x1, y1 = ltObject1.center
            x2, y2 = ltObject2.center
            length = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / scale
            time = (frame2 - frame1) / frameRate
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
        resultsFile.write(self.outString.format(sampleName, -1,
                                            ((totalActivityCount / frameRate) / totalTime),
                                            totalRunLength / totalTime, fileName))
