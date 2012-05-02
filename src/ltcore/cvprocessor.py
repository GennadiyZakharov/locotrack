'''
Created on 18.03.2011
@author: Gena
'''

from __future__ import division

from math import sqrt

import cv
from PyQt4 import QtCore
from ltcore.signals import *
from ltcore.ltactions import LtActions
from ltcore.chamber import Chamber
from ltcore.cvplayer import CvPlayer
from ltcore.trajectoryanalysis import RunRestAnalyser

class CvProcessor(QtCore.QObject):
    '''
    This is main class for video processing
    it holds player and array of chambers
    all data, stored in this class consist project  
    
    Also this class process video and writes data to chamber
    '''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(CvProcessor, self).__init__(parent)
        # Video Player
        self.cvPlayer = CvPlayer(self)
        self.connect(self.cvPlayer, signalNextFrame, self.getNextFrame)
        self.connect(self.cvPlayer, signalCvPlayerCapturing, self.videoOpened)
        # Chamber list
        self.chambers = [] 
        self.selected = -1
        self.scale = None
        self.frame = None
        # Parameters
        self.invertImage = False
        self.treshold = 0.6
        self.showProcessedImage = False
        self.showContour = True
        # Reset Trajectory
        self.saveTrajectory = False
        self.videoLength = None
        
        # Visual Parameters
        self.scaleLabelPosition = (20, 20)
        self.chamberColor = cv.CV_RGB(0, 255, 0)
        self.chamberSelectedColor = cv.CV_RGB(255, 0, 0)
        self.font = cv.InitFont(3, 1, 1)
        #
        self.runRestAnalyser = RunRestAnalyser(self)
        
    def videoOpened(self, length, frameRate):
        '''
        Get length and frame rate of opened video file
        '''
        self.videoLength = length
        self.frameRate = frameRate 
        
    def getNextFrame(self, frame, frameNumber, frameTime):
        '''
        get frame from cvPlayer, save it and process
        '''
        self.frame = frame
        self.frameNumber = frameNumber
        self.frameTime = frameTime
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
        # Processing all chambers
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
        self.emit(signalNextFrame, frame) 
        
    def preProcess(self, frame):
        '''
        All processing before analysing separate chambers
        '''
        # Inverting frame if needed
        if self.invertImage :
            cv.Not(frame, frame)
        # Discarding color information
        grayImage = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 1)
        cv.CvtColor(frame, grayImage, cv.CV_RGB2GRAY);
        return grayImage
            
    def processChamber(self, frame, chamber):
        '''
        Detect object properties on frame inside chamber
        '''
        if frame is None :
            print 'Error -- None frame is send to ProcessFrame'
            return
        chamber.frameNumber = self.frameNumber
        chamber.ltObject.massCenter = ( -1, -1 )
        
        # Set ROI according to chamber size
        cv.SetImageROI(frame, chamber.getRect())       
        # Finding min and max 
        (minVal, maxVal, minBrightPos, maxBrightPos) = cv.MinMaxLoc(frame)
        chamber.ltObject.maxBright = maxBrightPos
        # Tresholding image
        treshold = (maxVal-minVal) * self.treshold + minVal 
        cv.Threshold(frame, frame, treshold, 255, cv.CV_THRESH_TOZERO)
        #cv.AdaptiveThreshold(grayImage, grayImage, 255,blockSize=9)
        #
        subFrame = cv.CreateImage( (chamber.width(), chamber.height()), cv.IPL_DEPTH_8U, 1 );
        cv.Copy(frame, subFrame);
        
        #moments = cv.Moments(subFrame) # Calculating mass center of contour
        
        # Calculating mass center      
        
        # !!! This Operation leads to memory leak
        # This is OpenCV bug !!!!!
        mat = cv.GetMat(subFrame)
        moments = cv.Moments(mat)
        del mat
        m00 = cv.GetSpatialMoment(moments, 0, 0)
        if m00 != 0 :
            m10 = cv.GetSpatialMoment(moments, 1, 0)
            m01 = cv.GetSpatialMoment(moments, 0, 1)            
            chamber.ltObject.massCenter = ( m10/m00, m01/m00 )
        
        # create the storage area for contour
        storage = cv.CreateMemStorage(0)
        # Find object contours
        chamber.ltObject.contours = cv.FindContours(subFrame, storage,
                                           cv.CV_RETR_TREE, cv.CV_CHAIN_APPROX_SIMPLE)   
        # Saving to trajectory if we need it
        if self.saveTrajectory :
            chamber.saveToTrajectory()
        # Reset area selection
        cv.ResetImageROI(frame)
        
    def drawChambers(self, frame) :
        '''
        Draw chambers, object position, scale label, etc
        '''
        # Draw scale label
        if self.scale is not None :
            cv.Line(frame, self.scaleLabelPosition, (int(self.scaleLabelPosition[0] + self.scale), self.scaleLabelPosition[1]),
                    self.chamberColor, 2)
        # Drawing chambers
        for i in range(len(self.chambers)) :   
            if i == self.selected :
                color = self.chamberSelectedColor
            else :
                color = self.chamberColor
            # Draw chamber borders
            cv.Rectangle(frame, self.chambers[i].leftTopPos(), self.chambers[i].bottomRightPos(),
                         color, 2)
            cv.PutText(frame, str(i), self.chambers[i].leftTopPos(),
                         self.font, color)
            # Draw contours
            cv.SetImageROI(frame, self.chambers[i].getRect())
            if self.showContour and (self.chambers[i].ltObject.contours is not None) :
                cv.DrawContours(frame, self.chambers[i].ltObject.contours, 200, 100, -1, 1)
            # Draw mass center and maxBright 
            if self.chambers[i].ltObject.massCenter is not None :
                point = (int(self.chambers[i].ltObject.massCenter[0]),
                         int(self.chambers[i].ltObject.massCenter[1]) )
                cv.Circle(frame, point, 2, self.chamberSelectedColor, cv.CV_FILLED)
            if self.chambers[i].ltObject.maxBright is not None :
                cv.Circle(frame, self.chambers[i].ltObject.maxBright, 2, self.chamberColor, cv.CV_FILLED)
            # Draw last part of trajectory
            """
            if self.chambers[i].ltTrajectory is not None :
                trajend = self.chambers[i].ltTrajectory.end(self.maxTraj)
                if len(trajend) >= 2 :
                    cv.PolyLine(frame, [trajend,], 0, self.chamberColor)
            """  
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
    
    def setChamber(self, rect):
        '''
        Create chamber from rect and insert it 
        into selected frameNumber
        '''
        chamber = Chamber(rect)
        if self.selected == -1 :
            # Append chamber to list
            self.chambers.append(chamber)
        else :
            # Replace selected chamber 
            self.chambers[self.selected] = chamber
        self.processFrame() # Update current frame
        self.emit(signalChambersUpdated, list(self.chambers), self.selected)
            
    def setScale(self, rect):
        '''
        set scale according to rect
        '''
        self.scale = sqrt(rect.width()**2 + rect.height()**2)
        self.processFrame() # Update current frame
    
    def selectChamber(self, number):
        '''
        set selection to chamber number
        '''
        if - 1 <= number < len(self.chambers) :
            self.selected = number
            self.processFrame() # Update current frame
                
    def clearChamber(self):
        '''
        Clear selected chamber
        '''
        if self.selected > -1 :
            self.chambers.pop(self.selected)
            self.selected = -1
            self.processFrame() # Update current frame
            self.emit(signalChambersUpdated, list(self.chambers), self.selected)
    
    def setTreshold(self, value):
        '''
        Set theshold value (in percents)
        '''
        self.treshold = value / 100.0
        self.processFrame() # Update current frame
        
    def writeTrajectory(self, checked, line, gender, condition):
        '''
        Enable/Disable trajectory saving
        '''
        if self.scale is None :
            return
        self.saveTrajectory = checked
        if self.saveTrajectory :
            
            '''
            # Determine Length
            lastFrame = (self.videoLength - self.frameNumber) \
                        if self.videoLength is not None else 10*1800
                 # TODO: fix right index
            # Init array for trajectory from current 
            '''
            for i in range(len(self.chambers)) :
                self.chambers[i].initTrajectory(self.cvPlayer.fileName+".ch{0}.lt1".format(i), 
                                                self.scale, self.cvPlayer.frameRate, line, gender, condition)
            
        else:
            # Clear wrote Trajectory
            for chamber in self.chambers :
                chamber.resetTrajectory()
    
    def analyseTrajectory(self):
        for i in range(len(self.chambers)) :
            trajFileName = self.cvPlayer.fileName+".ch{0}.lt1".format(i)
            self.runRestAnalyser.analyse(trajFileName)
    
    def setSampleName(self, line, gender, condition):
        self.line = line
        self.gender = gender
        self.condition = condition    