'''
Created on 18.03.2011

@author: Gena
'''
from __future__ import division

from math import sqrt

import cv
from PyQt4 import QtCore
from ltcore.signals import *
from ltcore.chamber import Chamber


class ChambersManager(QtCore.QObject):
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(ChambersManager, self).__init__(parent)
        
        self.chambers = []
        self.selected = -1
        self.scale = None
        self.image = None
        self.background = None
        self.invertImage = False
        self.accumulate = False # This flag is used for background accumulation
        self.accumulateFrames = 0
        self.tempAccumulateFrames = None
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
        
    def on_nextFrame(self, image, frame):
        # We get new frame from cvPlayer
        self.image = image
        self.frame = frame
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

        moments = cv.Moments(image)
        m00 = cv.GetSpatialMoment(moments, 0, 0)
        if m00 != 0 :
            m10 = cv.GetSpatialMoment(moments, 1, 0)
            m01 = cv.GetSpatialMoment(moments, 0, 1)
            chamber.setObjectPos(self.frame, ( m10/m00, m01/m00 ) )
        else :
            chamber.setObjectPos(self.frame, None )
            
        
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
                cv.Circle(image, self.chambers[i].objectPos, 1, self.chamberSelectedColor, cv.CV_FILLED)
            if self.chambers[i].maxBrightPos is not None :
                cv.Circle(image, self.chambers[i].maxBrightPos, 1, self.chamberColor, cv.CV_FILLED)
            
            
            if len(self.chambers[i].trajectory) >= 2 :
                trajend = self.chambers[i].trajectory[-self.maxTraj:]
                cv.PolyLine(image, [trajend,], 0, self.chamberColor)  
            
            cv.ResetImageROI(image)
            
                       
    def on_Accumulate(self, value):
        self.accumulateFrames = value
        self.tempAccumulateFrames = value
        self.background = cv.CreateImage(cv.GetSize(self.image), cv.IPL_DEPTH_8U, 3)

    def on_Invert(self, value):
        self.invertImage = value
        self.processFrame()
        
    def on_ShowProcessed(self, value):
        self.showProcessedImage = value
        self.processFrame()
        
    def on_ShowContour(self, value):
        self.showContour = value
        self.processFrame()
    
    def on_SetChamber(self, rect):
        if self.selected == -1 :
            self.chambers.append(Chamber(rect))
        else :
            self.chambers[self.selected] = Chamber(rect)
        self.processFrame()
        self.emit(signalChambersUpdated, list(self.chambers), self.selected)
            
    def on_SetScale(self, rect):
        self.scale = sqrt(rect.width()**2 + rect.height()**2)
        self.processFrame()
    
    def on_SelectChamber(self, number):
        if - 1 <= number < len(self.chambers) :
            self.selected = number
            self.processFrame()
            if number > -1 :
                self.chambers[number].saveTrajectory(' ')
                
    def on_ClearChamber(self):
        if self.selected > -1 :
            self.chambers.pop(self.selected)
            self.selected = -1
            self.processFrame()
            self.emit(signalChambersUpdated, list(self.chambers), self.selected)
    
    def on_SetTreshold(self, value):
        self.treshold = value / 100.0
        self.processFrame()
        
    def on_ResetBackground(self):
        self.background = None
        self.processFrame()
