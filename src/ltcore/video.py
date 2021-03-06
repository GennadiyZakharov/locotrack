'''
Created on Jun 20, 2014

@author: gzakharov
'''
from __future__ import print_function
from __future__ import division

from glob import glob
from math import isnan
from PyQt4 import QtCore,QtGui
import cv2
from ltcore.chambersmanager import ChambersManager
from ltcore.chamber import Chamber

class Video(QtCore.QObject):
    '''
    This class implements part of project --
    one video file with associated properties -- chambers, scale, etc 
    '''

    def __init__(self, videoFileName, parent=None):
        '''
        Constructor
        '''
        super(Video, self).__init__(parent)
        self.videoFileName = videoFileName
        self.chambers = ChambersManager(self)
        self.frameRate = -1
        # Stub to get video file length and framerate
        captureDevice = cv2.VideoCapture(unicode(videoFileName)) # Try to open file
        if captureDevice is None : # Error opening file
            #TODO: error report 
            print("Error opening video file {}".format(self.videoFileName))
            raise
        videoLength = int(captureDevice.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))-1
        self.frameRate = captureDevice.get(cv2.cv.CV_CAP_PROP_FPS)
        # Workaround over openCV bug 
        if isnan(self.frameRate) :
            print('Buggy framerate, using -1')
            self.frameRate = -1
        print('Created video',videoLength, self.frameRate)
        # Cham
        self.chambers.setVideoLength(videoLength)
        
    def loadChambers(self):
        for name in sorted(glob(str(self.videoFileName) + '*.lt1')) :
            print("Opening chamber ", name)
            chamber,scale,frameRate = Chamber.loadFromFile(name)
            if frameRate<>self.frameRate and self.frameRate>0 and frameRate >0 :
                print("Chamber framerate {} not equal to video file one {}".format(frameRate,self.frameRate))
            else :
                self.chambers.addChamber(chamber) 
            QtGui.QApplication.processEvents()  
        if len(self.chambers) > 0 :
            self.chambers.setScale(scale)
            
            
    def saveChambers(self):
        print('Saving chamber for ',self.videoFileName)
        for chamber in self.chambers :
            chamber.saveToFile(self.videoFileName + ".ch{0:02d}.lt1",
                                         self.chambers.scale, self.frameRate)
        
        
        