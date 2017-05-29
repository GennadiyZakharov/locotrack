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
    signalCalibrationChanged = QtCore.pyqtSignal(bool)

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

        self.calibrationParameters=None

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

    @QtCore.pyqtSlot(QtCore.QString)
    def calibrateFromImage(self, calibrationImageName):
        # termination criteria for corners refinement
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        winSize = (11, 11)  # Window for corners refinement

        nborders = 8 # Maximum size of pattern

        img = cv2.imread(unicode(calibrationImageName))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Find the chess board corners - maximum possible
        for i in range(3,nborders)[::-1]:
            for j in range(3,nborders)[::-1]:
                ret, corners = cv2.findChessboardCorners(gray, (i, j))
                if ret:
                    break
            else:
                continue  # executed if the loop ended normally (no break)
            break  # executed if 'continue' was skipped (break)

        # If found, add object points, image points (after refining them)
        if ret:
            # Draw and display the corners
            cv2.cornerSubPix(gray, corners, winSize, (-1, -1), criteria)
            cv2.drawChessboardCorners(img, (i, j), corners, ret)
            # Recording flat 2D coordinates
            imgpoints = [corners]  # 2d points in image plane.
            # Generating corresponding set of flat 3D points in focal set of camera
            # object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
            objp = np.zeros((i * j, 3), np.float32)
            objp[:, :2] = np.mgrid[0:i, 0:j].T.reshape(-1, 2)
            objpoints = [objp]  # 3d point in real world spaceobjpoints.append()
            # Calibration
            ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
            # refine the camera matrix
            h, w = img.shape[:2]
            optimalMat, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1,(w,h))
            self.calibrationParameters = (mtx, dist, None, optimalMat)
            self.signalCalibrationChanged.emit(True)
            # undistort
            dst = cv2.undistort(img, *self.calibrationParameters)
            cv2.imshow('undistort', dst)
        else:
            print('Unable to find pattern')
            self.calibrationParameters = None
            self.signalCalibrationChanged.emit(False)
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
