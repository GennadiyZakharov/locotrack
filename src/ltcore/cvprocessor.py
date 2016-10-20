'''
Created on 18.03.2011
@author: Gena
'''

from __future__ import division

import cv2
from PyQt4 import QtCore
import Queue
import numpy as np
from math import pi
import multiprocessing.dummy as multiprocessing
import time


from ltcore.cvplayer import CvPlayer

from ltcore.objectdetectors import maxBrightDetector, massCenterDetector
from ltcore.project import Project
from ltcore.preprocessor import Preprocessor

from ltcore.ltobject import LtObject

pool = multiprocessing.Pool(4)

def processChamberAsync(ch):
    frame, threshold = ch
    h, w = frame.shape
    #print('Frame', frame)
    #print(w,h)
    if True:
        center = ( w/2, h/2 )
        th = int(max(center) / 2)
        axes = ( (w/2 + th/2), h/2 + th / 2)
        #cv2.ellipse(frame, center, axes, 0, 0, 360, cv2.cv.RGB(0, 0, 0), thickness=th)

    (minVal, maxVal, minBrightPos, maxBrightPos) = cv2.minMaxLoc(frame)
    #print(minVal, maxVal, minBrightPos, maxBrightPos)
    averageVal = np.mean(frame)  # TODO: why fail?
    if True:
        averageVal *= 4 / pi
    # size =
    # Tresholding image
    tresholdVal = (maxVal - averageVal) * (threshold / 100) + averageVal
    avg, thrFrame = cv2.threshold(frame, tresholdVal, 255, cv2.cv.CV_THRESH_TOZERO)
    # Adaptive threshold
    '''
    blocksize = int(chamber.threshold) // 2
    if blocksize %2 == 0 :
        blocksize +=1
    cv.AdaptiveThreshold(frame, frame, 255, cv.CV_ADAPTIVE_THRESH_GAUSSIAN_C,
                         cv.CV_THRESH_BINARY,blocksize)
    '''
    # Calculating mass center
    moments = cv2.moments(thrFrame)
    m00 = moments['m00']
    if m00 != 0:
        m10 = moments['m10']
        m01 = moments['m01']
        m10 = moments['m10']
        m01 = moments['m01']

        ltObject = LtObject((m10 / m00, m01 / m00))
        direction = [[moments['mu20'], moments['mu11']],
                     [moments['mu11'], moments['mu02']]]
        direction = np.array(direction)
        eVals, eVect = np.linalg.eig(direction)
        directionVector = eVect[0] if eVals[0] >= eVals[1] else eVect[1]
        ltObject.direction = directionVector
    else:
        ltObject = None

    return (thrFrame, ltObject)

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
        
        self.chambersQueue = []
        self.thrFramesQueue = []
        self.frameCounter=0
        self.startTime = time.time()



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
        self.frameCounter += 1
        if self.frameCounter >= 20:
            curTime = time.time()
            spd = self.frameCounter / (curTime - self.startTime)
            print('Speed = {:10.4} fps'.format(spd))
            self.startTime = curTime
            self.frameCounter = 0




    def calculatePosition(self, frame):
        # Processing all chambers 
        activeVideo = self.project.activeVideo()    
        chamberRects = []
        chambersQueue = []
        if activeVideo is not None: 
            
            for chamber in self.project.activeVideo().chambers :
                x, y, width,height = chamber.getRect()
                #chamberRects.append((frame[y:y+height,x:x+width], chamber))
                #self.chambersQueue.enqueue(  )
                chambersQueue.append( (frame[y:y+height,x:x+width], chamber.threshold) )
                
            '''
            while True :
                if self.chambersQueue.empty() :
                    break
                chamberRect,chamber = self.chambersQueue.get()
                thrFrame = self.processChamber(chamberRect, chamber)
                self.thrFramesQueue.put((thrFrame, chamber))
            '''

            thrFramesQueue = pool.map(processChamberAsync, chambersQueue) # parallel execution
            #thrFramesQueue = map(processChamberAsync, chambersQueue)     # sequential execution

            i = 0
            for chamber in self.project.activeVideo().chambers :
                thrFrame, ltObject = thrFramesQueue[i]
                #print('Object',ltObject.center if ltObject is not None else 'None')
                chamber.setLtObject(ltObject,self.frameNumber)
                if self.showProcessedImage :
                    x, y, width,height =chamber.getRect()
                    frame[y:y+height,x:x+width] = thrFrame
                i+=1
                
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
            
                 
        
