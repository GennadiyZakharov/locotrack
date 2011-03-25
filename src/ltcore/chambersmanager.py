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
        self.treshold = 60
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
        
    def on_nextFrame(self, image):
        # We get new frame from cvPlayer
        self.image = image
        self.processFrame()
        
    def processFrame(self):
        if self.image is None :
            return
        
        # Creating image copy to draw and process it
        image = cv.CloneImage(self.image)
        self.preProcess(image)
        self.processChambers(image)
        self.drawChambers(image)
        self.emit(signalNextFrame, image)
        
    def preProcess(self, image):
        # Inverting image if needed
        if self.invertImage :
            cv.Not(image, image)
            
        # Accumulate background
        if self.tempAccumulateFrames is not None :
            print self.tempAccumulateFrames, '/', self.accumulateFrames
            cv.ScaleAdd(image, 1 / self.accumulateFrames,
                        self.background, self.background)
            self.tempAccumulateFrames -= 1
            if self.tempAccumulateFrames == 0 :
                self.tempAccumulateFrames = None
        
        # Substract background if it avaliable
        if self.background is not None :
            cv.Sub(image, self.background, image)
        
    def processChambers(self, image):
        for chamber in self.chambers :
            cv.SetImageROI(image, chamber.getRect())
            cv.Threshold(image, image, self.treshold,
                         300, cv.CV_THRESH_TOZERO)
            self.findObject(image,chamber)
            cv.ResetImageROI(image)
            
    def findObject(self, image,chamber):
        # cv.FindContours
        # create new image for the grayscale version */
        grayImage = cv.CreateImage(cv.GetSize(image), cv.IPL_DEPTH_8U, 1);
        cv.CvtColor(image, grayImage, cv.CV_RGB2GRAY);
        storage = cv.CreateMemStorage(0)
        
        moments = cv.Moments(grayImage)
        m00 = cv.GetSpatialMoment(moments, 0, 0)
        if m00 != 0 :
            m10 = cv.GetSpatialMoment(moments, 1, 0)
            m01 = cv.GetSpatialMoment(moments, 0, 1)
            chamber.objectPos = QtCore.QPointF(m10 / m00, m01 / m00)
        else :
            chamber.objectPos = None
        countors = None
        #cv.FindContours(image, storage)
#        chamber.contours = 
        
            
              
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
            
            if self.chambers[i].objectPos is not None :
                point = self.chambers[i].objectPos + QtCore.QPointF(self.chambers[i].topLeft())
                cv.Circle(image, (int(point.x()),
                          int(point.y())), 3, self.chamberSelectedColor)
            '''
            if self.chambers[i].contours is not None :
                cv.DrawContours(image, self.chambers[i].contours,
                                _red, _green, levels, 3, cv.CV_AA, (0, 0)))
            
            '''           
    def on_Accumulate(self, value):
        print "accumulation", value
        self.accumulateFrames = value
        self.tempAccumulateFrames = value
        self.background = cv.CreateImage(cv.GetSize(self.image), cv.IPL_DEPTH_8U, 3)

    def on_Invert(self, value):
        self.invertImage = value
        self.processFrame()
    
    def on_SetChamber(self, rect):
        if self.selected == -1 :
            self.chambers.append(Chamber(rect))
        else :
            self.chambers[self.selected] = Chamber(rect)
        self.processFrame()
        #self.emit(signal
            
    def on_SetScale(self, rect):
        self.scale = sqrt(rect.width()**2 + rect.height()**2)
        self.processFrame()
    
    def on_SelectChamber(self, number):
        if - 1 <= number < len(self.chambers) :
            self.selected = number
            self.processFrame()
    
    def on_SetTreshold(self, value):
        self.treshold = value
        self.processFrame()
