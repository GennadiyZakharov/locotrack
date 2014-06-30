'''
Created on Jun 20, 2014

@author: gzakharov
'''
from __future__ import print_function
from __future__ import division

from glob import glob
from PyQt4 import QtCore
from ltcore.consts import videoFormats
from ltcore.video import Video

class Project(QtCore.QObject):
    '''
    This class hols all information about project:
    main project folder, list of all included videofiles, etc
    '''
    signalProjectOpened  = QtCore.pyqtSignal(QtCore.QString)
    signalProjectClosed  = QtCore.pyqtSignal()
    signalProjectUpdated = QtCore.pyqtSignal()
    signalVideoSelected  = QtCore.pyqtSignal(QtCore.QString)

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(Project, self).__init__(parent)
        self.projectFolderName = QtCore.QString()
        self.videos = {}
        self.activeVideoName = QtCore.QString()
    
    def isEmpty(self):
        return self.projectFolderName.isEmpty()
    
    def openProject(self, projectFolderName):
        videoFiles = self.projectFolder.entryList(['*.'+videoFormat for videoFormat in videoFormats], QtCore.QDir.Files | QtCore.QDir.NoSymLinks)
        if not videoFiles.isEmpty():
            self.projectFolderName=projectFolderName
            for videoFile in videoFiles :
                self.addVideo(videoFile)
            self.signalProjectUpdated.emit()
        
              
    def saveProject(self):
        for video in self.videos :
            video.saveChambers()
            
    def closeProject(self):
        self.projectFolderName = QtCore.QString()
        self.videos = {}
        self.activeVideoName = QtCore.QString()
        self.signalProjectUpdated.emit()
        
    
    def addVideo(self, fileName):
        video = Video(fileName)
        self.videos[fileName] = video
        self.activeVideo = fileName
        self.signalProjectUpdated.emit()
        
    def deleteVideo(self, fileName):
        if fileName in self.videos.keys():
            del self.videos[fileName]
            self.signalProjectUpdated.emit()
            
    def setActiveVideo(self, videoFileName):
        if self.activeVideoName == videoFileName :
            return
        self.activeVideoName = videoFileName
        self.signalVideoSelected.emit(self)
        
    def activeVideo(self):
        if not self.videoFileName in self.videos.keys() :
            return None
        self.videos[self.videoFileName]
        
    def setScale(self, scale):
        self.activeVideo().setScale(scale)
        
        
        
            
        
        
        
        
        
        
        