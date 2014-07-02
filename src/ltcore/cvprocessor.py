'''
Created on 18.03.2011
@author: Gena
'''

from __future__ import division

import cv
import os
from PyQt4 import QtCore
from ltcore.cvplayer import CvPlayer
from ltcore.trajectoryanalysis import TrajectoryAnalysis

from ltcore.objectdetectors import maxBrightDetector, massCenterDetector
from ltcore.project import Project


class CvProcessor(QtCore.QObject):
    '''
    This is main class for video processing
    it holds player and array of chambers
    all data, stored in this class consist project  
    
    Also this class process video and writes data to chamber
    '''
    trajectoryWriting = QtCore.pyqtSignal(bool)
    signalNextFrame = QtCore.pyqtSignal(object)
    projectOpened = QtCore.pyqtSignal(QtCore.QString)
    projectClosed = QtCore.pyqtSignal()

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
        # One project
        self.project = Project()
        self.project.signalVideoSelected.connect(self.videoSelected)
        # Chamber list
        #self.chambers.signalRecalculateChambers.connect(self.chambersDataUpdated)
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
        self.trajectoryAnalysis = TrajectoryAnalysis(self)

    def videoOpened(self, length, frameRate, fileName):
        '''
        Get length and frame rate of opened video file
        '''
        
        self.videoClosed()
        self.videoLength = length
        #self.frameRate = frameRate
        self.project.addVideo(fileName)
        
        self.projectOpened.emit(os.path.basename(unicode(fileName)))
        
    def videoClosed(self):
        #self.chambers.clear()
        #self.videoLength = -1
        #self.frameRate = -1
        self.project.deleteVideo('')
        self.projectOpened.emit('')
        self.projectClosed.emit()
        
    def videoEnded(self):
        self.setRecordTrajectory(False)
        self.saveProject()
        self.chambers.removeTrajectory()
          
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
        activeVideo = self.project.activeVideo()
            
        if activeVideo is not None: 
            for chamber in self.project.activeVideo().chambers :
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
            activeVideo = self.project.activeVideo()
            
            if activeVideo is not None: 
                for chamber in activeVideo.chambers :
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
            ltObject = self.massCenterDetector.detectObject(frame, chamber, self.ellipseCrop)
        else:
            raise
        chamber.oldLtObject = chamber.ltObject
        chamber.setLtObject(ltObject, self.frameNumber)
        # Reset area selection
        cv.ResetImageROI(frame)
        
    def drawChambers(self, frame) :
        '''
        Draw chambersGui, object position, scale label, etc
        '''
        # Draw scale label
        activeVideo = self.project.activeVideo()
        if activeVideo is not None: 
            scale = self.project.activeVideo().scale
        if scale >= 0  :
            # TODO: 15mm
            cv.Line(frame, self.scaleLabelPosition, (int(self.scaleLabelPosition[0] + scale * 15), self.scaleLabelPosition[1]),
                    self.chamberColor, 2)
        # Drawing chambersGui Numbers
        # TODO: move to gChamber
        activeVideo = self.project.activeVideo()
        if activeVideo is None:
            return 
        for chamber in self.project.activeVideo().chambers :   
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
    
    @QtCore.pyqtSlot(bool)
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
    
    @QtCore.pyqtSlot(QtCore.QRect)
    def addChamber(self, rect):
        '''
        Create chamber from rect 
        '''
        self.project.activeVideo().chambers.createChamber(rect)
    
    def clearChamber(self, chamber):
        self.project.activeVideo().chambers.removeChamber(chamber)
    
    @QtCore.pyqtSlot(float)
    def setScale(self, scale):
        '''
        set scale (px/mm)
        '''
        print('Set scale',scale)
        self.project.setScale(scale)
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
        self.project.activeVideo().chambers.setThreshold(value)
    
    @QtCore.pyqtSlot(bool)
    def setRecordTrajectory(self, checked):
        '''
        Enable/Disable trajectory saving
        '''
        if self.recordTrajectory == checked :
            return
        if self.scale is None :
            #TODO:
            print 'Cannot save chambers: no scale present'
            self.recordTrajectory = False
            self.trajectoryWriting.emit(False)
            return
        self.recordTrajectory = checked
        if self.recordTrajectory :
            # Init array for trajectory from current location to end of video file
            self.chambers.initTrajectories(self.cvPlayer.leftBorder,self.cvPlayer.rightBorder+1)
            self.chambers.setRecordTrajectories(True)
        self.trajectoryWriting.emit(self.recordTrajectory)
        self.processFrame()
    
    @QtCore.pyqtSlot()
    def chambersDataUpdated(self):
        self.processFrame()      
    
    def createTrajectoryImages(self):
        pass#self.chambers.createTrajectoryImages() 
    
    def videoSelected(self, fileName):
        self.cvPlayer.captureFromFile(fileName)         
        
