'''
Created on 18.03.2011
@author: Gena
'''

from __future__ import division

import cv
import os
from math import sqrt
from PyQt4 import QtCore
from ltcore.signals import *
from ltcore.chamber import Chamber
from ltcore.cvplayer import CvPlayer
from ltcore.trajectoryanalysis import NewRunRestAnalyser
from glob import glob
from numpy import asarray
from math import pi

class CvProcessor(QtCore.QObject):
    '''
    This is main class for video processing
    it holds player and array of chambers
    all data, stored in this class consist project  
    
    Also this class process video and writes data to chamber
    '''
    trajectoryWriting = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(CvProcessor, self).__init__(parent)
        # Video Player
        self.cvPlayer = CvPlayer(self)
        self.cvPlayer.nextFrame.connect(self.getNextFrame)
        self.cvPlayer.videoSourceOpened.connect(self.videoOpened)
        # Chamber list
        self.chambers = [] 
        self.selected = -1
        self.scale = None
        self.frame = None
        # Parameters
        self.threshold = 60
        self.invertImage = False
        self.showProcessedImage = False
        self.showContour = True
        self.ellipseCrop = True
        # Reset Trajectory
        self.saveToFile = False
        self.videoLength = None
        self.sampleName = 'Unknown'
        # Visual Parameters
        self.scaleLabelPosition = (20, 20)
        self.chamberColor = cv.CV_RGB(0, 255, 0)
        self.chamberSelectedColor = cv.CV_RGB(255, 0, 0)
        self.maxBrightColor = cv.CV_RGB(255, 255, 0)
        self.font = cv.InitFont(3, 1, 1)
        #
        self.runRestAnalyser = NewRunRestAnalyser(self)
        #self.errorDetector = ErrorDetector()
        self.analysisMethodMaxBright = False
        
    def openProject(self, fileName):
        pass
    
    def loadVideoFile(self, fileName):
        self.cvPlayer.captureFromFile(fileName)
        self.chambers = []
        self.selected = -1
        for name in sorted(glob(fileName+'*.lt1')) :
            print "Opening chamber ",name
            chamber = Chamber.loadFromFile(name)
            self.addChamber(chamber)            
        if self.chambers != [] :
            chamber = self.chambers[0]
            self.scale = chamber.scale
            self.setSampleName(chamber.sampleName)
        self.chambersDataUpdated()
        self.emit(signalChambersUpdated, list(self.chambers), self.selected)
        
    def saveProject(self):
        '''
        Save data for all chambers and trajectories
        '''
        print 'Saving project'
        for i in range(len(self.chambers)) :
            self.chambers[i].saveToFile(self.cvPlayer.videoFileName+".ch{0}.lt1".format(i+1), 
                                         self.cvPlayer.frameRate)

    def videoOpened(self, length, frameRate):
        '''
        Get length and frame rate of opened video file
        '''
        self.saveTrajectory(False)
        self.videoLength = length
        self.frameRate = frameRate
     
        
    def videoEnded(self):
        self.saveTrajectory(False, None)
        
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
        # Crop
        if self.ellipseCrop :
            for chamber in self.chambers :
                cv.SetImageROI(frame, chamber.getRect())
                center = (int(chamber.width()/2), int(chamber.height()/2))
                th=int(max(center)/2)
                axes = (int(chamber.width()/2+th/2), int(chamber.height()/2+th/2))
                cv.Ellipse(frame, center, axes, 0, 0, 360, cv.RGB(0,0,0), thickness=th)
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
        #
        if self.analysisMethodMaxBright :
            if minVal == maxVal :
                chamber.ltObject.massCenter = None
            else:
                chamber.ltObject.massCenter = maxBrightPos
                
            if self.saveToFile :
                chamber.saveLtObjectToTrajectory()
            # Reset area selection
            cv.ResetImageROI(frame)
            return
            
        averageVal = cv.Avg(frame)[0]
        if self.ellipseCrop :
            averageVal *= 4/pi
       
        # Tresholding image
        treshold = (maxVal-averageVal) * chamber.threshold/100 + averageVal 
        cv.Threshold(frame, frame, treshold, 255, cv.CV_THRESH_TOZERO)
        
        #cv.AdaptiveThreshold(grayImage, grayImage, 255,blockSize=9)
        
        # Calculating mass center
        subFrame = cv.CreateImage( (chamber.width(), chamber.height()), cv.IPL_DEPTH_8U, 1 );
        cv.Copy(frame, subFrame);
     
        #moments = cv.Moments(subFrame) # Calculating mass center of contour        
        mat = asarray(subFrame[:,:])
        
        m00 = mat.sum()
        if m00 != 0 :
            m10 = (mat*chamber.X).sum()
            m01 = (mat*chamber.Y).sum()           
            chamber.ltObject.massCenter = ( m10/m00, m01/m00 )
        
        #mat = cv.GetMat(subFrame)
        '''
        moments = cv.Moments(cv.fromarray(mat))
        del mat
        m00 = cv.GetSpatialMoment(moments, 0, 0)
        if m00 != 0 :
            m10 = cv.GetSpatialMoment(moments, 1, 0)
            m01 = cv.GetSpatialMoment(moments, 0, 1)            
            chamber.ltObject.massCenter = ( m10/m00, m01/m00 )
        '''
        # create the storage area for contour
        storage = cv.CreateMemStorage(0)
        # Find object contours
        '''
        chamber.ltObject.contours = cv.FindContours(subFrame, storage,
                                           cv.CV_RETR_TREE, cv.CV_CHAIN_APPROX_SIMPLE)   
        '''
        # Saving to trajectory if we need it
        
        if self.saveToFile :
            chamber.saveLtObjectToTrajectory()
        # Reset area selection
        cv.ResetImageROI(frame)
        
    def drawChambers(self, frame) :
        '''
        Draw chambers, object position, scale label, etc
        '''
        # Draw scale label
        if self.scale is not None :
            # TODO: 15mm
            cv.Line(frame, self.scaleLabelPosition, (int(self.scaleLabelPosition[0] + self.scale*15), self.scaleLabelPosition[1]),
                    self.chamberColor, 2)
        
        # Drawing chambers
        for i in range(len(self.chambers)) :
            chamber = self.chambers[i]   
            
            if i == self.selected :
                color = self.chamberSelectedColor
            else :
                color = self.chamberColor

            cv.PutText(frame, str(i+1), chamber.topLeftTuple(),
                         self.font, color)
            
            # Draw contours
            cv.SetImageROI(frame, chamber.getRect())
            '''
            if self.ellipseCrop :
                center = (int(chamber.width()/2), int(chamber.height()/2))
                cv.Ellipse(frame, center, center, 0, 0, 360, color, thickness=1)
            '''
            if self.analysisMethodMaxBright :
                color = self.maxBrightColor
            else :
                color = self.chamberSelectedColor
            
            if self.showContour and (chamber.ltObject.contours is not None) :
                cv.DrawContours(frame, chamber.ltObject.contours, 200, 100, -1, 1)
            # Draw mass center and maxBright 
            if self.chambers[i].ltObject.massCenter is not None :
                point = (int(chamber.ltObject.massCenter[0]),
                         int(chamber.ltObject.massCenter[1]) )
                cv.Circle(frame, point, 2, color, cv.CV_FILLED)
            
            if not self.analysisMethodMaxBright and self.chambers[i].ltObject.maxBright is not None :
                cv.Circle(frame, self.chambers[i].ltObject.maxBright, 2, self.chamberColor, cv.CV_FILLED)
            # Draw last part of trajectory
            """
            if self.chambers[i].ltTrajectory is not None :
                trajend = self.chambers[i].ltTrajectory.end(self.maxTraj)
                if length(trajend) >= 2 :
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
    
    def addChamber(self, chamber):
        chamber.chamberDataUpdated.connect(self.chambersDataUpdated)
        self.chambers.append(chamber)
    
    def setChamber(self, rect):
        '''
        Create chamber from rect and insert it 
        into selected frameNumber
        '''
        if self.selected >=0 :
            self.chambers[self.selected].setPosition(rect.normalized())
        else :
            chamber = Chamber(rect)
            self.addChamber(chamber)
            chamber.setThreshold(self.threshold)
            chamber.scale = self.scale
            chamber.setSampleName(self.sampleName)
            self.emit(signalChambersUpdated, self.chambers, self.selected)
        self.processFrame() # Update current frame
        
        
    def setChamberTreshold(self, number, value):
        self.chambers[number].setTreshold(value)
        self.emit(signalChambersUpdated, self.chambers, self.selected)
        
    def setScale(self, rect):
        '''
        set scale according to rect
        '''
        # TODO: 15mm
        self.scale = sqrt(rect.width()**2 + rect.height()**2)/15
        for chamber in self.chambers :
            chamber.scale = self.scale
        self.processFrame() # Update current frame
    
    def selectChamber(self, number):
        '''
        set selection to chamber number
        '''
        if - 1 <= number < len(self.chambers) :
            self.selected = number
            self.processFrame() # Update current frame
            self.emit(signalChambersUpdated, list(self.chambers), self.selected)
                
    def clearChamber(self):
        '''
        Clear selected chamber
        '''
        if self.selected > -1 :
            self.chambers.pop(self.selected)
            self.selected = -1
            self.processFrame() # Update current frame
            self.emit(signalChambersUpdated, list(self.chambers), self.selected)
    
    @QtCore.pyqtSlot(int)
    def setEllipseCrop(self, value):
        self.ellipseCrop = (value == QtCore.Qt.Checked)
        self.processFrame()
    
    @QtCore.pyqtSlot(int)
    def setTreshold(self, value):
        '''
        Set theshold value (in percents)
        '''
        self.threshold = value
        for chamber in self.chambers :
            chamber.setThreshold(value)
        self.emit(signalChambersUpdated, list(self.chambers), self.selected)
        #self.processFrame() # Update current frame
    
    def saveTrajectory(self, checked):
        '''
        Enable/Disable trajectory saving
        '''
        if self.saveToFile == checked :
            return
        print 'SaveTrajectory:', checked
        if self.scale is None :
            #TODO:
            return
        self.saveToFile = checked
        self.trajectoryWriting.emit(self.saveToFile)
        if self.saveToFile :
            # Init array for trajectory from current location
            for i in range(len(self.chambers)) :
                self.chambers[i].initTrajectory(self.videoLength)
    
    def setSampleName(self, newSampleName):
        for chamber in self.chambers :
            if chamber.sampleName == self.sampleName :
                chamber.setSampleName(newSampleName) 
        self.sampleName = newSampleName
    
    @QtCore.pyqtSlot()
    def chambersDataUpdated(self):
        self.processFrame()
    
    @QtCore.pyqtSlot(int, int)    
    def moveChamber(self, dirX, dirY):
        if self.selected < 0 :
            return
        self.chambers[self.selected].move(dirX, dirY)
        self.processFrame()
        
    @QtCore.pyqtSlot(int, int)    
    def resizeChamber(self, dirX, dirY):
        if self.selected < 0 :
            return
        self.chambers[self.selected].resize(dirX, dirY)
        self.processFrame()
    
    def setAnalysisMethod(self, checked):
        self.analysisMethodMaxBright = checked
        self.processFrame()
    
    def createTrajectoryImages(self):
        for chamber in self.chambers:
            chamber.createTrajectoryImage()
    
    def analyseFromFiles(self, fileName, inputFileNames):
        print "Starting analysis"
        if os.path.isfile(fileName) :
            mode = 'a'
        else :
            mode = 'w'
        outFile = open(fileName, mode)
        if mode == 'w' :
            captionString = '                  Sample ;   Int;           Activity;             Speed ;\n'
            outFile.write(captionString)
        for name in inputFileNames :
            if not str(name).endswith('.lt1') :
                continue
            chamber = Chamber.loadFromFile(name)
            if chamber.ltTrajectory is not None :
                chamber.createTrajectoryImage()
                chamber.trajectoryImage.save(name+'.png')
                baseName = os.path.basename(str(name))
                pos = baseName.find('.ch',-10,-1)
                print baseName,pos
                if pos >=1 :
                    if self.runRestAnalyser.checkErrors(chamber) :
                        self.runRestAnalyser.analyseChamber(chamber, baseName[:pos], outFile)            
    
    def analyseChambers(self, fileName):
        '''
        Analyse all chambers and print data about it in output file
        '''
        if self.chambers == [] :
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
        
        for chamber in self.chambers :
            if chamber.ltTrajectory is not None :
                print 'Analysing chamber'
                name = os.path.basename(self.cvPlayer.videoFileName)
                if self.runRestAnalyser.checkErrors(chamber) :
                    self.runRestAnalyser.analyseChamber(chamber, name, outFile)
                '''
                #correctErrors(chamber)
                totalActivity, intervals = calculateSpeed(chamber)
                for number, activity in intervals :
                    outFile.write(formatString.format(chamber.sampleName, number, activity))
                outFile.write(formatString.format(chamber.sampleName, 'Total', totalActivity))
                '''
        outFile.close()
        print 'Analysis finished'
        