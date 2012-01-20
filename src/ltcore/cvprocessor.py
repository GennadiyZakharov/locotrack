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


class CvProcessor(QtCore.QObject):
    '''
    This is main class for video processing
    it holds player, array of chambers
    
    also this class process video and writes data to chamber
    '''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(CvProcessor, self).__init__(parent)
        
        self.cvPlayer = CvPlayer(self)
        self.connect(self.cvPlayer, signalNextFrame, self.getNextFrame)
        
        self.chambers = [] 
        
        self.selected = -1
        self.scale = None
        self.image = None
        
        self.accumulate(None)
        self.invertImage = False
        self.treshold = 0.6
        self.showProcessedImage = False
        self.showContour = True
        self.maxTraj = 25
        
        # Visual Parameters
        self.scalepos = (20, 20)
        self.chamberColor = cv.CV_RGB(0, 255, 0)
        self.chamberSelectedColor = cv.CV_RGB(255, 0, 0)
        self.font = cv.InitFont(3, 1, 1)

    def addChamber(self, rect):
        chamber = Chamber(rect)
        if self.selected >= 0 :
            self.chambers[self.selected] = chamber
        else : 
            self.chambers.append(chamber)
        
    def getNextFrame(self, image, frameNumber):
        # We get new frame and frameNumber from cvPlayer
        self.image = image
        self.frameNumber = frameNumber
        self.processFrame()
        
    def processFrame(self):
        if self.image is None :
            return
        # Creating image copy to draw and process it
        image = cv.CloneImage(self.image)
        grayImage = self.preProcess(image)       
        self.processChambers(grayImage)
        if self.showProcessedImage :
            image = cv.CreateImage(cv.GetSize(image), cv.IPL_DEPTH_8U, 3)
            cv.CvtColor(grayImage, image, cv.CV_GRAY2RGB)
             
        self.drawChambers(image)
        self.emit(signalNextFrame, image)
        
    def preProcess(self, image):
        # Inverting image if needed
        if self.invertImage :
            cv.Not(image, image)
            
        # Accumulate background
        if self.tempAccumulateFrames is not None :
            cv.ScaleAdd(image, 1 / self.accumulateFrames,
                        self.background, self.background)
            self.tempAccumulateFrames -= 1
            if self.tempAccumulateFrames == 0 :
                self.tempAccumulateFrames = None
        
        # Substract background if it avaliable
        if self.background is not None :
            cv.Sub(image, self.background, image)
            
        grayImage = cv.CreateImage(cv.GetSize(image), cv.IPL_DEPTH_8U, 1);
        cv.CvtColor(image, grayImage, cv.CV_RGB2GRAY);
        return grayImage
        
    def processChambers(self, image):
        for chamber in self.chambers :
            self.findObject(image, chamber)
            
    def findObject(self, image, chamber):
        cv.SetImageROI(image, chamber.getRect())       
        
        (minVal, maxVal, minPoint, maxBrightPos) = cv.MinMaxLoc(image)
        chamber.setMaxBrightPos(maxBrightPos)
               
        treshold = maxVal * self.treshold 
        cv.Threshold(image, image, treshold, 200, cv.CV_THRESH_TOZERO)
        #cv.AdaptiveThreshold(grayImage, grayImage, 255,blockSize=9)
        print image
        """
        moments = cv.Moments(image)
        m00 = cv.GetSpatialMoment(moments, 0, 0)
        if m00 != 0 :
            m10 = cv.GetSpatialMoment(moments, 1, 0)
            m01 = cv.GetSpatialMoment(moments, 0, 1)
            chamber.setObjectPos(self.frameNumber, ( m10/m00, m01/m00 ) )
        else :
            chamber.setObjectPos(self.frameNumber, None )
            
        """
        # create the storage area
        storage = cv.CreateMemStorage (0)
        # find the contours
        tempimage = cv.CloneImage(image)
        chamber.contours = cv.FindContours(tempimage, storage,
                                           cv.CV_RETR_TREE, cv.CV_CHAIN_APPROX_SIMPLE)
        #contours = cv.ApproxPoly (contours,storage, cv.CV_POLY_APPROX_DP, 5)
         
        cv.ResetImageROI(image)
        
    def drawChambers(self, image) :
        # Draw scale
        if self.scale is not None :
            cv.Line(image, self.scalepos, (self.scalepos[0] + self.scale, self.scalepos[1]),
                    self.chamberColor, 2)
        # Drawing chambers
        for i in xrange(len(self.chambers)) :   
            if i == self.selected :
                color = self.chamberSelectedColor
            else :
                color = self.chamberColor
             
            cv.Rectangle(image, self.chambers[i].getPos(), self.chambers[i].getPos2(),
                         color, 2)
            cv.PutText(image, str(i), self.chambers[i].getPos(),
                         self.font, color)
            
            cv.SetImageROI(image, self.chambers[i].getRect())
            
            
            if self.showContour and (self.chambers[i].contours is not None) :
                cv.DrawContours(image, self.chambers[i].contours, 200, 100, -1, 1)
            
            if self.chambers[i].objectPos is not None :
                point = (int(self.chambers[i].objectPos[0]),
                         int(self.chambers[i].objectPos[1]) )
                #cv.SetAt(image, cv.Scalar(0,0,250,0), point);
                cv.Circle(image, point, 2, self.chamberSelectedColor, cv.CV_FILLED)
            if self.chambers[i].maxBrightPos is not None :
                cv.Circle(image, self.chambers[i].maxBrightPos, 2, self.chamberColor, cv.CV_FILLED)
            
            
            if self.chambers[i].trajectory is not None :
                trajend = self.chambers[i].trajEnd(self.maxTraj)
                if len(trajend) >= 2 :
                    cv.PolyLine(image, [trajend,], 0, self.chamberColor)  
            
            cv.ResetImageROI(image)
            
                       
    def accumulate(self, value):
        if value is not None :
            self.accumulateFrames = value
            self.tempAccumulateFrames = value
            self.background = cv.CreateImage(cv.GetSize(self.image), cv.IPL_DEPTH_8U, 3)
        else :
            self.accumulateFrames = 0
            self.tempAccumulateFrames = None
            self.background = None
            self.processFrame()

    def setNegative(self, value):
        self.invertImage = value
        self.processFrame()
        
    def setShowProcessed(self, value):
        self.showProcessedImage = value
        self.processFrame()
        
    def setShowContour(self, value):
        self.showContour = value
        self.processFrame()
    
    def setChamber(self, rect):
        '''
        Create chamber from rect and insert it 
        into selected position
        '''
        chamber = Chamber(rect)
        if self.selected == -1 :
            self.chambers.append(chamber)
        else :
            self.chambers[self.selected] = chamber
        self.processFrame() # Update current frame
        self.emit(signalChambersUpdated, list(self.chambers), self.selected)
            
    def setScale(self, rect):
        '''
        set scale accordind to rect
        '''
        self.scale = sqrt(rect.width()**2 + rect.height()**2)
        self.processFrame() # Update current frame
    
    def selectChamber(self, number):
        if - 1 <= number < len(self.chambers) :
            self.selected = number
            self.processFrame() # Update current frame
                
    def clearChamber(self):
        if self.selected > -1 :
            self.chambers.pop(self.selected)
            self.selected = -1
            self.processFrame() # Update current frame
            self.emit(signalChambersUpdated, list(self.chambers), self.selected)
    
    def setTreshold(self, value):
        self.treshold = value / 100.0
        self.processFrame() # Update current frame
        
    def resetBackground(self):
        self.background = None
        self.processFrame() # Update current frame
