'''
Created on 29 jan. 2015

@author: Gena
'''
from __future__ import division
import cv2
import numpy as np
from PyQt4 import QtCore


class Preprocessor(QtCore.QObject):
    '''
    classdocs
    '''
    signalNextFrame = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(Preprocessor, self).__init__(parent)
        # Video Player
        # Parameters
        self.frame=None
        self.invertImage = True
        self.analyseRunning = False
        self.removeBarrel = True

        # Parameners for distortion removing
        self.removeBarrelCoef =  -1.0
        self.removeBarrelFocal = 10.0
        self.centerX = 640
        self.centerY = 512
        # Filling matrices
        self.distCoeff = np.zeros((4, 1), np.float64)
        self.distCoeff[0, 0] = self.removeBarrelCoef  * 1e-5
        # assume unit matrix for camera
        self.cam = np.eye(3, dtype=np.float32)
        self.cam[0, 0] = float(self.removeBarrelFocal)  # define focal length x  fx
        self.cam[1, 1] = self.cam[0, 0]  # define focal length y    fy
        self.cam[0, 2] = self.centerX  # define center x
        self.cam[1, 2] = self.centerY  # define center y

        self.background = None
        self.nBackgroundFrames=200

        self.player=None


    @QtCore.pyqtSlot()
    def collectBackground(self):

        frames=self.player.randomFrames(self.nBackgroundFrames)
        if frames is None:
            return
        avg = np.zeros(frames[0].shape, dtype=np.float32)
        for frame in frames:
            #newframe=np.float32(frame)
            #cv2.accumulate(newframe/len(frames), avg)
            cv2.accumulateWeighted(frame, avg, 0.01)
        self.background = cv2.convertScaleAbs(avg)
        cv2.imshow('background', self.background)
        self.doPreprocess()

    @QtCore.pyqtSlot(bool)
    def setInvertImage(self, value):
        self.invertImage = value
        self.doPreprocess()

    def removeBarrelDo(self, frame):
        # here the undistortion will be computed
        return cv2.undistort(frame, self.cam, self.distCoeff)

    @QtCore.pyqtSlot(int)
    def setBackgroundFrames(self, value):
        self.nBackgroundFrames = value

    @QtCore.pyqtSlot(bool)
    def setRemoveBarrel(self, value):
        self.removeBarrel = value
        self.doPreprocess()

    @QtCore.pyqtSlot(float)
    def setRemoveBarrelCoef(self, value):
        self.removeBarrelCoef = value
        self.distCoeff[0, 0] = self.removeBarrelCoef * 1e-5
        self.doPreprocess()
    
    @QtCore.pyqtSlot(float)
    def setRemoveBarrelFocal(self, value):
        self.removeBarrelFocal = value
        self.cam[0, 0] = self.removeBarrelFocal  # define focal length x  fx
        self.cam[1, 1] = self.cam[0, 0]  # define focal length y    fy
        self.doPreprocess()

    @QtCore.pyqtSlot(int)
    def setCenterX(self, value):
        self.centerX = value
        self.cam[0, 2] = self.centerX
        self.doPreprocess()

    @QtCore.pyqtSlot(int)
    def setCenterY(self, value):
        self.centerY = value
        self.cam[1, 2] = self.centerY
        self.doPreprocess()

    @QtCore.pyqtSlot(object)
    def processFrame(self, frame):
        self.frame=frame
        self.doPreprocess()
    
    def doPreprocess(self):
        '''
        All processing before analysing separate chambers
        '''
        # Discarding color information
        if self.frame is None:
            return None

        frame=self.frame

        if self.background is not None:
            frame = cv2.absdiff(frame, self.background)

        frame = cv2.cvtColor(frame, cv2.cv.CV_RGB2GRAY);

        # Inverting frame if needed        
        if self.invertImage :
            frame = cv2.bitwise_not(frame)

        if self.removeBarrel :
            frame = self.removeBarrelDo(frame)
                
        self.signalNextFrame.emit(frame)
