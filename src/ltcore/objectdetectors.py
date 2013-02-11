'''
Created on 29.12.2012

@author: gena

This module holds several object detection algorithms
It is done ad procedures, but classes also suitable

Each object detector call with frame with already set ROI
Procedure must return ltObject or None if object was not found
'''
from __future__ import division

import cv
from math import pi
from numpy import asarray
from ltcore.ltobject import LtObject

def maxBrightDetector(frame):
    '''
    Very simple object detector
    Detects maximum bright point
    '''
    (minVal, maxVal, minBrightPos, maxBrightPos) = cv.MinMaxLoc(frame)
    if minVal == maxVal :
        return None # There is no object -- all image has one color
    else:
        return LtObject(maxBrightPos)

def massCenterDetector(frame, size, matrices, threshold, ellipseCrop):
    '''
    This object detector thresholds image and finds mass center of bright
    
    '''
    (minVal, maxVal, minBrightPos, maxBrightPos) = cv.MinMaxLoc(frame)
    averageVal = cv.Avg(frame)[0]
    if ellipseCrop :
        averageVal *= 4 / pi
    # Tresholding image
    tresholdVal = (maxVal - averageVal) * (threshold / 100) + averageVal 
    cv.Threshold(frame, frame, tresholdVal, 255, cv.CV_THRESH_TOZERO)
    # Calculating mass center
    '''
    moments = cv.Moments(frame)
    The ability to calculate moments from frame 
    was broken in OpenCV 2.4.0 and still not fixed! 
    HATE!!! 
    '''
    # Creating copy of a frame, including only one chamber
    subFrame = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1);
    cv.Copy(frame, subFrame);        
    # Converting frame to matrix
    mat = asarray(subFrame[:, :])
    '''
    moments = cv.Moments(cv.fromarray(mat))
    Creating cv array from matrix  also broken -- it leads to memory leaks!
    HATE!!!
    '''
    # Calculating moments using matrix operations
    # matrixX and matrixY depends only on chamber size
    # so, it was calculated and stored in chamber 
    m00 = mat.sum()
    if m00 != 0 :
        m10 = (mat * matrices[0]).sum()
        m01 = (mat * matrices[1]).sum()
        m20 = (mat * (matrices[0] ** 2) ).sum()
        m02 = (mat * (matrices[1] ** 2) ).sum()
        ltObject = LtObject((m10 / m00, m01 / m00))
        return ltObject
    else :
        return None
