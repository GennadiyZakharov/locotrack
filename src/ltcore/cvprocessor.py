'''
Created on 18.03.2011
@author: Gena
'''

from __future__ import division

import cv
import os
from math import sqrt
from PyQt4 import QtCore,QtGui
from ltcore.signals import *
from ltcore.chamber import Chamber
from ltcore.cvplayer import CvPlayer
from ltcore.trajectoryanalysis import NewRunRestAnalyser
from glob import glob
from ltcore.objectdetectors import maxBrightDetector, massCenterDetector
from ltcore.chambersmanager import ChambersManager

class CvProcessor(QtCore.QObject):
    '''
    This is main class for video processing
    it holds player and array of chambers
    all data, stored in this class consist project  
    
    Also this class process video and writes data to chamber
    '''
    trajectoryWriting = QtCore.pyqtSignal(bool)
    signalNextFrame = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(CvProcessor, self).__init__(parent)
        # Video Player
        self.cvPlayer = CvPlayer(self)
        self.cvPlayer.nextFrame.connect(self.getNextFrame)
        self.cvPlayer.videoSourceOpened.connect(self.videoOpened)
        self.cvPlayer.videoSourceClosed.connect(self.videoClosed)
        # Chamber list
        self.chambers = ChambersManager()
        self.chambers.signalRecalculateChambers.connect(self.chambersDataUpdated)
        self.scale = None
        self.frame = None
        # Parameters
        self.invertImage = False
        self.showProcessedImage = True
        self.showContour = True
        self.ellipseCrop = True
        self.analyseFromFilesRunning = False
        # Reset Trajectory
        self.recordTrajectory = False
        self.videoLength = None
        # Visual Parameters
        self.scaleLabelPosition = (20, 20)
        self.chamberColor = cv.CV_RGB(0, 255, 0)
        self.chamberSelectedColor = cv.CV_RGB(255, 0, 0)
        self.maxBrightColor = cv.CV_RGB(255, 255, 0)
        self.font = cv.InitFont(3, 1, 1)
        #
        self.maxBrightDetector = maxBrightDetector()
        self.massCenterDetector = massCenterDetector()
        self.objectDetectors = [self.maxBrightDetector, self.massCenterDetector]
        self.objectDetectorIndex = 0
        self.runRestAnalyser = NewRunRestAnalyser(self)
        #self.errorDetector = ErrorDetector()
        
    def openProject(self, fileName):
        pass
        
    def saveProject(self):
        '''
        Save data for all chambers and trajectories
        '''
        print 'Saving project'
        for chamber in self.chambers :
            chamber.saveToFile(self.cvPlayer.videoFileName + ".ch{0:02d}.lt1",
                                         self.scale, self.cvPlayer.frameRate)

    def videoOpened(self, length, frameRate, fileName):
        '''
        Get length and frame rate of opened video file
        '''
        self.videoLength = length
        self.frameRate = frameRate
        for name in sorted(glob(str(fileName) + '*.lt1')) :
            print "Opening chamber ", name
            chamber,scale,frameRate = Chamber.loadFromFile(name)
            self.chambers.addChamber(chamber) 
            QtGui.QApplication.processEvents()  
        if len(self.chambers) > 0 :
            self.scale = scale
        
    def videoClosed(self):
        self.chambers.clear()
        self.videoLength = -1
        self.frameRate = -1
    
    def videoEnded(self):
        self.setRecordTrajectory(False, None)
        
    
        
    def getNextFrame(self, frame, frameNumber):
        '''
        get frame from cvPlayer, save it and process
        '''
        self.frame = frame
        self.frameNumber = frameNumber
        self.processFrame() #
        
    def processFrame(self):
        '''
        process saved frame -- find objects in chamber, draw chambers and
        object
        '''
        if self.frame is None :
            return
        # Creating frame copy to draw and process it
        frame = cv.CloneImage(self.frame)
        # Preprocessing -- negative, gray etc
        grayFrame = self.preProcess(frame)       
        # Processing all chambersGui
        for chamber in self.chambers :
            self.processChamber(grayFrame, chamber)
        # Converting processed image to 3-channel form to display
        # (cvLabel can draw only in RGB mode)
        if self.showProcessedImage :
            frame = cv.CreateImage(cv.GetSize(grayFrame), cv.IPL_DEPTH_8U, 3)
            cv.CvtColor(grayFrame, frame, cv.CV_GRAY2RGB);
        # Draw all chambers and object properties
        self.drawChambers(frame)
        # send processed frame to display
        self.signalNextFrame.emit(frame) 
        
    def preProcess(self, frame):
        '''
        All processing before analysing separate chambers
        '''
        # Inverting frame if needed
        if self.invertImage :
            cv.Not(frame, frame)
        # Crop
        if self.ellipseCrop :
            for chamber in self.chambers :
                cv.SetImageROI(frame, chamber.getRect())
                center = (int(chamber.width() / 2), int(chamber.height() / 2))
                th = int(max(center) / 2)
                axes = (int(chamber.width() / 2 + th / 2), int(chamber.height() / 2 + th / 2))
                cv.Ellipse(frame, center, axes, 0, 0, 360, cv.RGB(0, 0, 0), thickness=th)
                cv.ResetImageROI(frame)
            
        # Discarding color information
        grayImage = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 1)
        cv.CvtColor(frame, grayImage, cv.CV_RGB2GRAY);
        return grayImage
    
    def calculatePosition(self, frame):
        pass
           
    def processChamber(self, frame, chamber):
        '''
        Detect object properties on frame inside chamber
        '''
        chamber.frameNumber = self.frameNumber
        # Set ROI according to chamber size
        cv.SetImageROI(frame, chamber.getRect())       
        if self.objectDetectorIndex == 0 :
            ltObject = self.maxBrightDetector.detectObject(frame)
        elif  self.objectDetectorIndex == 1 :
            ltObject = self.massCenterDetector.detectObject(frame, (chamber.width(), chamber.height()),
                                                  chamber.matrices(), chamber.threshold, self.ellipseCrop)
        else:
            raise
        chamber.setLtObject(ltObject, self.frameNumber)
        # Reset area selection
        cv.ResetImageROI(frame)
        
    def drawChambers(self, frame) :
        '''
        Draw chambersGui, object position, scale label, etc
        '''
        # Draw scale label
        if self.scale is not None :
            # TODO: 15mm
            cv.Line(frame, self.scaleLabelPosition, (int(self.scaleLabelPosition[0] + self.scale * 15), self.scaleLabelPosition[1]),
                    self.chamberColor, 2)
        # Drawing chambersGui Numbers
        # TODO: move to gChamber
        for chamber in self.chambers :   
            if chamber.ltObject is None : # No object to draw
                return
            # Draw object
            cv.SetImageROI(frame, chamber.getRect())
            color = self.chamberSelectedColor
            # Draw mass center
            point = tuple(int(coor) for coor in chamber.ltObject.center)
            cv.Circle(frame, point, 2, color, cv.CV_FILLED)
            # Draw contours
            if self.showContour and (chamber.ltObject is not None) and (chamber.ltObject.contour is not None) :
                cv.DrawContours(frame, chamber.ltObject.contours, 200, 100, -1, 1)
            # Reset to full image
            cv.ResetImageROI(frame)

    def setNegative(self, value):
        '''
        Set if we need to negative image
        '''
        self.invertImage = value
        self.processFrame()
        
    def setShowProcessed(self, value):
        '''
        Sent processed or original image
        '''
        self.showProcessedImage = value
        self.processFrame()
        
    def setShowContour(self, value):
        self.showContour = value
        self.processFrame()
        
    def setObjectDetector(self, index):
        self.objectDetectorIndex = index
        self.processFrame()
    
    def addChamber(self, rect):
        '''
        Create chamber from rect 
        '''
        self.chambers.createChamber(rect)
    
    def clearChamber(self, chamber):
        self.chambers.removeChamber(chamber)
    
    def setScale(self, rect):
        '''
        set scale according to rect
        '''
        # TODO: 15mm
        self.scale = sqrt(rect.width() ** 2 + rect.height() ** 2) / 15
        self.processFrame() # Update current frame
    
    @QtCore.pyqtSlot(int)
    def setEllipseCrop(self, value):
        self.ellipseCrop = (value == QtCore.Qt.Checked)
        self.processFrame()
    
    @QtCore.pyqtSlot(int)
    def setTreshold(self, value):
        '''
        Set theshold value (in percents)
        '''
        self.chambers.setThreshold(value)
    
    def setRecordTrajectory(self, checked):
        '''
        Enable/Disable trajectory saving
        '''
        if self.recordTrajectory == checked :
            return
        if self.scale is None :
            #TODO:
            print 'Cannot save chambers: no scale present'
            return
        self.recordTrajectory = checked
        if self.recordTrajectory :
            # Init array for trajectory from current location to end of video file
            self.chambers.initTrajectories(self.frameNumber,self.videoLength)
            self.chambers.setRecordTrajectories(True)
        self.trajectoryWriting.emit(self.recordTrajectory)
        self.processFrame()
    
    @QtCore.pyqtSlot()
    def chambersDataUpdated(self):
        self.processFrame()      
    
    def createTrajectoryImages(self):
        self.chambers.createTrajectoryImages()          
    
    def analyseChambers(self, fileName):
        '''
        Analyse all chambersGui and print data about it in output file
        '''
        if self.chambersGui == [] :
            return
        print "Starting analysis"
        if os.path.isfile(fileName) :
            mode = 'a'
        else :
            mode = 'w'
        outFile = open(fileName, mode)
        if mode == 'w' :
            captionString = '                  Sample ;   Int;           Activity;             Speed ;\n'
            outFile.write(captionString)
        
        for chamber in self.chambersGui :
            if chamber.trajectory is not None :
                print 'Analysing chamber'
                name = os.path.basename(self.cvPlayer.videoFileName)
                if self.runRestAnalyser.checkErrors(chamber) :
                    self.runRestAnalyser.analyseChamber(chamber, name, outFile)
        outFile.close()
        print 'Analysis finished'
        
