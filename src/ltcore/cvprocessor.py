'''
Created on 18.03.2011
@author: Gena
'''

from __future__ import division

import cv2
import os
from PyQt4 import QtCore
from ltcore.cvplayer import CvPlayer

from ltcore.objectdetectors import maxBrightDetector, massCenterDetector
from ltcore.project import Project


class CvProcessor(QtCore.QObject):
    '''
    This is main class for video processing
    it holds player and array of chambers
    all data, stored in this class consist project  
    
    Also this class process video and writes data to chamber
    '''
    signalNextFrame = QtCore.pyqtSignal(object)
    signalClearFrame = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(CvProcessor, self).__init__(parent)
        # Video Player
        self.cvPlayer = CvPlayer(self)
        self.cvPlayer.nextFrame.connect(self.getNextFrame)
        self.cvPlayer.videoSourceOpened.connect(self.videoSourceOpened)
        #self.cvPlayer.videoSourceClosed.connect(self.videoSourceClosed)
        # One project
        self.project = Project()
        self.project.signalVideoSelected.connect(self.videoSelected)
        self.project.signalRecalculateChambers.connect(self.processFrame)
        self.cvPlayer.videoSourceEnded.connect(self.project.videoEnded)
        # Chamber list
        #TODO:
        #self.chambers.signalRecalculateChambers.connect(self.chambersDataUpdated)
        self.frame = None
        # Parameters
        self.invertImage = False
        self.showProcessedImage = True
        self.showContour = True
        self.ellipseCrop = True
        self.analyseRunning = False
        # Reset Trajectory
        #self.recordTrajectory = False
        # Visual Parameters
        self.scaleLabelPosition = (20, 20)
        self.chamberColor = cv2.cv.CV_RGB(0, 255, 0)
        #(redVal,greenVal,blueVal) Color.green()  #cv.CV_RGB(0, 255, 0)
        self.chamberSelectedColor = cv2.cv.CV_RGB(255, 0, 0)
        self.maxBrightColor = cv2.cv.CV_RGB(255, 255, 0)
        #self.font = cv.InitFont(3, 1, 1)
        #
        self.maxBrightDetector = maxBrightDetector()
        self.massCenterDetector = massCenterDetector()
        self.objectDetectors = [self.maxBrightDetector, self.massCenterDetector]
        self.objectDetectorIndex = 0   

    def videoSourceOpened(self, length, frameRate, fileName):
        '''
        Get length and frame rate of opened video file
        '''
        self.videoLength = length
          
    def getNextFrame(self, frame, frameNumber):
        '''
        get frame from cvPlayer, save it and process
        '''
        self.frame = frame
        #cv2.imshow('frame',frame)
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
        #frame = self.frame.copy()
        # Preprocessing -- negative, gray etc
        # TODO:
        grayFrame = self.preProcess(self.frame)       
        # Processing all chambersGui
        
        activeVideo = self.project.activeVideo()            
        if activeVideo is not None: 
            for chamber in self.project.activeVideo().chambers :
                self.processChamber(grayFrame, chamber)
        
        # Converting processed image to 3-channel form to display
        # (cvLabel can draw only in RGB mode)
        
        if self.showProcessedImage :
            frame = cv2.cvtColor(grayFrame, cv2.cv.CV_GRAY2RGB);
            #frame = cv2.CreateImage(cv.GetSize(grayFrame), cv.IPL_DEPTH_8U, 3)
        else:
            frame=self.frame
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
            frame = cv2.bitwise_not(frame)
        # Crop
        if self.ellipseCrop :
            activeVideo = self.project.activeVideo()
            
            if activeVideo is not None: 
                for chamber in activeVideo.chambers :
                    x, y, width,height =chamber.getRect()
                    chamberRect = frame[y:y+height,x:x+width]
                    center = (int(chamber.width() / 2), int(chamber.height() / 2))
                    th = int(max(center) / 2)
                    axes = (int(chamber.width() / 2 + th / 2), int(chamber.height() / 2 + th / 2))
                    cv2.ellipse(chamberRect, center, axes, 0, 0, 360, cv2.cv.RGB(0, 0, 0), thickness=th)
                    #cv.ResetImageROI(frame)
            
        # Discarding color information
        grayImage = cv2.cvtColor(frame, cv2.cv.CV_RGB2GRAY);
        #cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 1)
        #cv.CvtColor(frame, grayImage, cv.CV_RGB2GRAY);
        return grayImage
    
    def calculatePosition(self, frame):
        pass
           
    def processChamber(self, frame, chamber):
        '''
        Detect object properties on frame inside chamber
        '''
        chamber.frameNumber = self.frameNumber
        # Set ROI according to chamber size
        x,y,width,height = chamber.getRect()
        chamberROI = frame[y:y+height,x:x+width]  #cv.SetImageROI(frame, )       
        if self.objectDetectorIndex == 0 :
            ltObject = self.maxBrightDetector.detectObject(chamberROI)
        elif  self.objectDetectorIndex == 1 :
            ltObject,thrFrame = self.massCenterDetector.detectObject(chamberROI, chamber, self.ellipseCrop)
            if self.showProcessedImage:
                frame[y:y+height,x:x+width]=thrFrame
        else:
            raise
        
        chamber.setLtObject(ltObject, self.frameNumber)
        
        # Reset area selection
        # cv.ResetImageROI(frame)
        
    def drawChambers(self, frame) :
        '''
        Draw chambersGui, object position, scale label, etc
        '''
        # Draw scale label
        activeVideo = self.project.activeVideo()
        if activeVideo is not None: 
            scale = self.project.activeVideo().chambers.scale
            if scale >= 0  :
                # TODO: 15mm
                cv2.line(frame, self.scaleLabelPosition, (int(self.scaleLabelPosition[0] + scale * 15), self.scaleLabelPosition[1]),
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
            x,y,width,height = chamber.getRect()
            color = self.chamberSelectedColor
            # Draw mass center
            xx,yy = chamber.ltObject.center
            point = (x+int(xx),y+int(yy))
            cv2.circle(frame, point, 2, color, cv2.cv.CV_FILLED)
            # Draw contours
            '''
            
            if self.showContour and (chamber.ltObject is not None) and (chamber.ltObject.contour is not None) :
                cv.DrawContours(frame, chamber.ltObject.contours, 200, 100, -1, 1)
            # Reset to full image
            cv.ResetImageROI(frame)
            '''
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
       
    @QtCore.pyqtSlot()
    def chambersDataUpdated(self):
        self.processFrame()      
    
    def videoSelected(self, fileName):
        if fileName.isEmpty() :
            self.cvPlayer.captureClose()
            self.frame=None
            self.signalClearFrame.emit()
            self.analyseRunning = False
        else:
            self.cvPlayer.captureFromFile(fileName)
            
                 
        
