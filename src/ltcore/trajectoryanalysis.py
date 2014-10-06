# -*- coding: utf-8 -*-
'''
Created on 07.04.2012

@author: gena
'''

from __future__ import division
from __future__ import print_function
from math import sqrt
import os
from PyQt4 import QtCore, QtGui
from ltcore.chamber import Chamber  
from ltcore.errordetector import ErrorDetector   
from ltcore.trajectoryanalysers import RunRestAnalyser, RatRunAnalyser

class TrajectoryAnalysis(QtCore.QObject):

    signalAnalysisStarted = QtCore.pyqtSignal(int)
    signalNextFileAnalysing = QtCore.pyqtSignal(str, int)
    signalAnalysisFinished = QtCore.pyqtSignal()
    imageMargin = 10
    
    def __init__(self, errorDetector, parent=None):
        '''
        Constructor
        '''
        super(TrajectoryAnalysis, self).__init__(parent)
        self.errorDetector = ErrorDetector(self)
        self.analysers = [RunRestAnalyser(self), 
                          RatRunAnalyser(self)]
        self.analyser = self.analysers[0]
        self.analyseFromFilesRunning = False
        self.imageLevels = 3
        self.imageCreators = [self.createImageLines, self.createImageDots]
        self.imageCreatorsCaptions = ['Lines','Dots']
        self.imageCreator = self.createImageDots
        self.setWriteSpeed(0)
    
    @QtCore.pyqtSlot(int)
    def setWriteSpeed(self, checked):
        self.writeSpeedInfo = checked
      
    @QtCore.pyqtSlot(int)
    def setImageCreator(self, index):
        self.imageCreator = self.imageCreators[index]
      
    @QtCore.pyqtSlot(int)  
    def setAnalyser(self, index):
        self.analyser = self.analysers[index]
    
    @QtCore.pyqtSlot(int)
    def setImageLevelsCount(self, value):
        self.imageLevels = value
    
    def ltObjectToPoint(self, ltObject, displace):
        return QtCore.QPointF(*ltObject.center).toPoint()+displace
    
    def createImageDots(self, chamber):
        '''
        Create trajectory image in dots representation
        '''
        minX,minY, maxX,maxY = chamber.trajectory.minMax()
        trajectoryImage = QtGui.QImage(maxX-minX + self.imageMargin * 2,
            maxY-minY + self.imageMargin * 2, QtGui.QImage.Format_RGB888)
        trajectoryImage.fill(QtCore.Qt.white)
        step = 255 // self.imageLevels
        displace = QtCore.QPoint(self.imageMargin-minX,self.imageMargin-minY)
        for ltObject in chamber.trajectory :
            if ltObject is None :
                continue
            point = self.ltObjectToPoint(ltObject,displace)
            color = trajectoryImage.pixel(point)
            level = color & 255
            newLevel = max(0, level - step)
            trajectoryImage.setPixel(point, QtGui.QColor(newLevel, newLevel, newLevel).rgb())
            QtGui.QApplication.processEvents()
        return trajectoryImage
    
    def createImageLines(self, chamber):
        '''
        Create trajectory image in lines representation
        '''   
        width,height = chamber.width(), chamber.height()
        
        trajectoryImage = QtGui.QImage(width + self.imageMargin * 2,
            height + self.imageMargin * 2, QtGui.QImage.Format_ARGB32_Premultiplied)
        trajectoryImage.fill(QtCore.Qt.white)
        trajectoryPainter = QtGui.QPainter(trajectoryImage)
        #Draw chamber
        trajectoryPainter.setPen(QtCore.Qt.black)
        chamberRect = QtCore.QRectF(self.imageMargin,self.imageMargin,width,height)
        trajectoryPainter.drawRect(chamberRect)
        trajectoryPainter.drawEllipse(chamberRect)
        trajectoryPainter.setPen(QtCore.Qt.green)
        displace = QtCore.QPoint(self.imageMargin,self.imageMargin)
        ltObject1 = None
        for ltObject2 in chamber.trajectory :
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
    
    
    def analyseChambers(self, chamberList):
        self.signalAnalysisStarted.emit(len(chamberList))
        i = 0
        self.analyseFromFilesRunning = True
        for chamber,scale,frameRate in chamberList:
            print('Analysing chamber',i,scale,frameRate)
            if not self.analyseFromFilesRunning : 
                print('Analysis aborted')
                break
            # Signal to update GUI
            i += 1
            QtGui.QApplication.processEvents()
            if chamber.trajectory is None : 
                continue
            # speed info
            #spdName = name+'.spd' if self.writeSpeedInfo != 0 else None
            self.signalNextFileAnalysing.emit('chamber ',i)
            if not chamber.trajectory.findBorders():
                continue
            errorStatus = self.errorDetector.checkForErrors(chamber.trajectory, scale, frameRate) 
            if errorStatus == self.errorDetector.errorTooMuchMissedIntervals :
                print('Too much missed intervals; {};\n') 
            elif errorStatus == self.errorDetector.errorTooLongMissedInterval :
                print('Too long missed interval; {};\n')
            else :
                # Create image and analyse   
                trajectoryStats=self.analyser.analyseChamber(chamber,scale,frameRate)
                chamber.setTrajectoryStats(trajectoryStats)
                chamber.setTrajectoryImage(self.imageCreator(chamber))
                print(trajectoryStats.totalReport())        
                    
        self.signalAnalysisFinished.emit()  

    @QtCore.pyqtSlot()
    def abortAnalysis(self):
        self.analyseFromFilesRunning = False   
        



