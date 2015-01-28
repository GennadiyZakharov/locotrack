'''
Created on 29.12.2012

@author: gena

This module holds several object detection algorithms
It is done as classes to hold names and parameters

Each object detector call with frame with already set ROI
Procedure must return ltObject or None if object was not found
'''
from __future__ import print_function
from __future__ import division

import cv2
from math import pi
import numpy as np
from numpy import asarray
from ltcore.ltobject import LtObject

class maxBrightDetector(object):
    '''
    Very simple object detector
    Detects maximum bright point
    '''
    name = 'MaxBright'
    description = 'Detect only one whitest point of image'
    def detectObject(self, frame):
        (minVal, maxVal, minBrightPos, maxBrightPos) = cv2.minMaxLoc(frame)
        if minVal == maxVal :
            return None # There is no object -- all image has one color
        else:
            return LtObject(maxBrightPos)

class massCenterDetector():
    '''
    This object detector thresholds image and finds mass center of bright
    '''
    name = 'MassCenter'
    description = 'Threshold and center'
    
    def detectObject(self, frame, chamber, ellipseCrop):
        '''
        '''
        
        # If old 
        '''
        if chamber.oldLtObject is not None :
            pass
            center = chamber.oldLtObject.intCenter()
            th = int(max(center, ) / 2)
            axes = (int(chamber.width() / 2 + th / 2), int(chamber.height() / 2 + th / 2))
            cv.Ellipse(frame, center, axes, 0, 0, 360, cv.RGB(0, 0, 0), thickness=th)
        '''
        (minVal, maxVal, minBrightPos, maxBrightPos) = cv2.minMaxLoc(frame)
        averageVal = np.mean(frame)  #TODO: why fail?
        if ellipseCrop :
            averageVal *= 4 / pi
        #size = 
        # Tresholding image
        tresholdVal = (maxVal - averageVal) * (chamber.threshold / 100) + averageVal 
        avg, thrFrame=cv2.threshold(frame, tresholdVal, 255, cv2.cv.CV_THRESH_TOZERO)
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
        if m00 != 0 :
            m10=moments['m10']
            m01=moments['m01']
            ltObject = LtObject((m10 / m00, m01 / m00))
            return ltObject,thrFrame
        else :
            return None,thrFrame
