'''
Created on 29 jan. 2015

@author: Gena
'''

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
        self.invertImage = False
        self.analyseRunning = False
        self.removeBarrel = True
        self.removeBarrelCoef = -1.0e-5
        self.removeBarrelFocal = 10

    @QtCore.pyqtSlot(bool)
    def setInvertImage(self, value):
        self.invertImage = value
        self.doPreprocess()

    @QtCore.pyqtSlot(bool)
    def setRemoveBarrel(self, value):
        self.removeBarrel = value
        self.doPreprocess()

    @QtCore.pyqtSlot(float)
    def setRemoveBarrelCoef(self, value):
        self.removeBarrelCoef = value
        self.doPreprocess()
    
    @QtCore.pyqtSlot(int)
    def setRemoveBarrelFocal(self, value):
        self.removeBarrelFocal = value
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
        frame = cv2.cvtColor(self.frame, cv2.cv.CV_RGB2GRAY);
        
        # Inverting frame if needed        
        if self.invertImage :
            frame = cv2.bitwise_not(frame)
        
        if self.removeBarrel :
            distCoeff = np.zeros((4,1),np.float64)
            distCoeff[0,0] = self.removeBarrelCoef
            
            # assume unit matrix for camera
            cam = np.eye(3,dtype=np.float32)
            
            height, width  = frame.shape[0],frame.shape[1],
            
            cam[0,2] = width/2.0  # define center x
            cam[1,2] = height/2.0 # define center y
            cam[0,0] = float(self.removeBarrelFocal)        # define focal length x
            cam[1,1] = cam[0,0]        # define focal length y

            # here the undistortion will be computed
            frame = cv2.undistort(frame,cam,distCoeff)
                
        self.signalNextFrame.emit(frame)