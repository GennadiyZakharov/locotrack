'''
Created on 18.03.2011

@author: Gena
'''

import cv
from PyQt4 import QtCore
from ltcore.signals import *
from ltcore.chamber import Chamber

class ChambersManager(QtCore.QObject):
    '''
    classdocs
    '''


    def __init__(self,parent=None):
        '''
        Constructor
        '''
        super(ChambersManager, self).__init__(parent)
        self.chambers = []
        self.selected = -1
        self.chamberColor = cv.CV_RGB(0, 255, 0)
        self.chamberSelectedColor = cv.CV_RGB(255, 0, 0)
        self.font=cv.InitFont(3,1,1)
        # This flag is used for background accumulation
        self.accumulate = False
        self.accumulateFrames = 0
        self.background = None
        self.tempbackground = None
        self.invertImage = False
        
        
    def addChamber(self,x1,y1,x2,y2):
        chamber = Chamber(x1,y1,x2,y2)
        if self.selected >= 0 :
            self.chambers[self.selected] = chamber
        else : 
            self.chambers.append(chamber)
        
    def on_nextFrame(self,image):
        # We get new frame from cvPlayer
        if self.invertImage :
            cv.Not(image,image)
        '''
        if self.accumulateFrames :
            if self.tempbackground is None :
                self.tempbackground = cv.CreateImage(cv.GetSize(image),cv.IPL_DEPTH_8U,3)
            
            
            self.accumulateFrames -= 1
            if not self.accumulateFrames :
                self.background = self.tempbackground
                self.tempbackground = None
                self.emit()
        '''
        if self.chambers == [] :
            return
        '''
        for chamber in self.chambers :
            cv.SetImageROI(image,chamber.getRect())
            self.imageProcessor.processimage(image)
            cv.ResetImageROI(image)
        '''
        for i in xrange(len(self.chambers)) :
            if i == self.selected :
                color=self.chamberSelectedColor
            else :
                color=self.chamberColor
             
            cv.Rectangle(image,self.chambers[i].getPos(),self.chambers[i].getPos2(),
                         color,2)
            cv.PutText(  image, str(i), self.chambers[i].getPos(),
                         self.font,color)
        
        self.emit(signalNextFrame,image)
        
        
    def on_Accumulate(self,value):
        self.accumulate = True
        self.accumulateFrames = value
        self.background = None
         
    def on_Invert(self,value):
        self.invertImage = value
    
    
    def selectChamber(self,number):
        if -1 <= number < len(self.chambers) :
            self.selected = number
        
