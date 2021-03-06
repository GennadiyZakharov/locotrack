'''
Created on 18.03.2011
@author: Gena
'''

from __future__ import division

import cv2
from PyQt4 import QtCore
import Queue
from ltcore.cvplayer import CvPlayer

from ltcore.objectdetectors import maxBrightDetector, massCenterDetector
from ltcore.project import Project
from ltcore.preprocessor import Preprocessor


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
        # One project
        self.project = Project()
        self.project.signalVideoSelected.connect(self.videoSelected)
        self.project.signalRecalculateChambers.connect(self.processFrame)
        self.cvPlayer.videoSourceEnded.connect(self.project.videoEnded)
        # Chamber list
        #TODO:
        #self.chambers.signalRecalculateChambers.connect(self.chambersDataUpdated)
        self.preprocessor = Preprocessor(self)
        self.preprocessor.signalNextFrame.connect(self.calculatePosition)
        self.preprocessor.signalCalibrationChanged.connect(self.calibrationChanged)
        self.preprocessor.player = self.cvPlayer
        
        self.frame = None
        # Parameters
        self.showProcessedImage = True
        self.showContour = True
        self.ellipseCrop = True
        self.analyseRunning = False
        # Visual Parameters
        self.scaleLabelPosition = (20, 20)
        self.chamberColor = cv2.cv.CV_RGB(0, 255, 0)
        self.chamberSelectedColor = cv2.cv.CV_RGB(255, 0, 0)
        self.maxBrightColor = cv2.cv.CV_RGB(255, 255, 0)
        #
        self.maxBrightDetector = maxBrightDetector()
        self.massCenterDetector = massCenterDetector()
        self.objectDetectors = [self.maxBrightDetector, self.massCenterDetector]
        self.objectDetectorIndex = 0 
        
        self.chambersQueue = Queue.Queue()  
        self.thrFramesQueue = Queue.Queue()

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
        self.frameNumber = frameNumber
        self.processFrame() #
        
    def processFrame(self):
        '''
        process saved frame -- find objects in chamber, draw chambers and
        object
        '''
        if self.frame is None :
            return
        self.preprocessor.processFrame(self.frame)         
    
    def calculatePosition(self, frame):
        # Processing all chambers 
        activeVideo = self.project.activeVideo()    
        chamberRects = []        
        if activeVideo is not None: 
            
            for chamber in self.project.activeVideo().chambers :
                x, y, width,height =chamber.getRect()
                #chamberRects.append((frame[y:y+height,x:x+width], chamber))
                #self.chambersQueue.enqueue(  )
                self.chambersQueue.put((frame[y:y+height,x:x+width], chamber))
                
            
            while True :
                if self.chambersQueue.empty() :
                    break
                chamberRect,chamber = self.chambersQueue.get()
                thrFrame = self.processChamber(chamberRect, chamber)
                self.thrFramesQueue.put((thrFrame, chamber))
                
                
            '''
            for chamberRect in chamberRects:
                thrFrames.append(self.processChamber(chamberRect, chamber))
            '''
            if self.showProcessedImage :
                while True :
                    if self.thrFramesQueue.empty() :
                        break
                    thrFrame, chamber  = self.thrFramesQueue.get()
                    x, y, width,height =chamber.getRect()
                    frame[y:y+height,x:x+width] = thrFrame
                
            '''
            if self.showProcessedImage :
                for thrFrame in thrFrames:
                
                    frame[y:y+height,x:x+width] = thrFrame
            '''         
        # Converting processed image to 3-channel form to display
        # (cvLabel can draw only in RGB mode)
        
        if self.showProcessedImage:
            frame=cv2.cvtColor(frame,cv2.cv.CV_GRAY2RGB)
        
        # Draw all chambers and object properties
        self.drawChambers(frame)
        # send processed frame to display
        self.signalNextFrame.emit(frame)
           
    def processChamber(self, chamberRect, chamber):
        '''
        Detect object properties on frame inside chamber
        '''
        chamber.frameNumber = self.frameNumber
        
        if self.ellipseCrop : 
            center = (int(chamber.width() / 2), int(chamber.height() / 2))
            th = int(max(center) / 2)
            axes = (int(chamber.width() / 2 + th / 2), int(chamber.height() / 2 + th / 2))
            cv2.ellipse(chamberRect, center, axes, 0, 0, 360, cv2.cv.RGB(0, 0, 0), thickness=th)    
        
        if self.objectDetectorIndex == 0 :
            ltObject = self.maxBrightDetector.detectObject(chamberRect)
            thrFrame = chamberRect
        elif  self.objectDetectorIndex == 1 :
            ltObject,thrFrame = self.massCenterDetector.detectObject(chamberRect, chamber, self.ellipseCrop)
            
        chamber.setLtObject(ltObject, self.frameNumber)
        return thrFrame
        
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

    def calibrationChanged(self, calibration):
        pass
