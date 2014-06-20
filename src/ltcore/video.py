'''
Created on Jun 20, 2014

@author: gzakharov
'''
from __future__ import print_function
from __future__ import division

from glob import glob
from PyQt4 import QtCore,QtGui
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
        self.scale = -1
        self.frameRate = -1
        
    def loadChambers(self):
        
        fileInfo = QtCore.QFileInfo(self.videoFileName)
        directory = fileInfo.absoluteDir()
        files = directory.entryList(QtCore.QStringList(self.videoFileName+'*.lt1'),
                                  QtCore.QDir.Files | QtCore.QDir.NoSymLinks)
        if not files.isEmpty():
            for name in files:
                print("Opening chamber "+name)
                chamber,scale,frameRate = Chamber.loadFromFile(name)
                self.chambers.addChamber(chamber) 
                QtGui.QApplication.processEvents()
            if len(self.chambers) > 0 :
                self.scale = scale
                self.frameRate = frameRate
                
            '''
        for name in sorted(glob(str(self.videoFileName) + '*.lt1')) :
            print("Opening chamber "+name)
            chamber,scale,frameRate = Chamber.loadFromFile(name)
            self.chambers.addChamber(chamber) 
            QtGui.QApplication.processEvents()
            '''  
        
        
        
        