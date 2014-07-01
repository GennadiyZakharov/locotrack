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
from ltcore.chamber import Chamber
from ltcore.chambersmanager import ChambersManager

class Project(QtCore.QObject):
    '''
    This class hols all information about project:
    main project folder, list of all included videofiles, etc
    '''
    signalProjectOpened  = QtCore.pyqtSignal(QtCore.QString)
    signalProjectClosed  = QtCore.pyqtSignal()
    signalProjectUpdated = QtCore.pyqtSignal()
    
    signalVideoSelected  = QtCore.pyqtSignal(QtCore.QString)
    signalChambersMangerChanged = QtCore.pyqtSignal(ChambersManager)
    
    signalChamberAdded = QtCore.pyqtSignal(Chamber)   # New chamber added to list
    signalChamberDeleted = QtCore.pyqtSignal(Chamber) # Chamber removed from list 

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
        print('Opened video file ' + fileName)
        video = Video(fileName)
        self.videos[fileName] = video
        video.loadChambers()
        self.signalProjectUpdated.emit()
        #self.setActiveVideo(fileName)
        
    def deleteVideo(self, fileName):
        if fileName in self.videos.keys():
            
            del self.videos[fileName]
            self.signalProjectUpdated.emit()
            self.signalChambersMangerChanged.emit(None)
            
    def setActiveVideo(self, videoFileName):
        if self.activeVideoName == videoFileName :
            return
        video = self.activeVideo()
        if video is not None :
            video.chambers.signalChamberAdded.disconnect(self.chamberAdded)
            video.chambers.signalChamberDeleted.disconnect(self.chamberDeleted)
            for chamber in video.chambers :
                self.signalChamberDeleted.emit(chamber)
        self.activeVideoName = videoFileName
        self.signalVideoSelected.emit(self.activeVideoName)
        self.signalChambersMangerChanged.emit(self.activeVideo().chambers)
        video = self.activeVideo()
        video.chambers.signalChamberAdded.connect(self.chamberAdded)
        video.chambers.signalChamberDeleted.connect(self.chamberDeleted)
        for chamber in video.chambers :
            self.signalChamberAdded.emit(chamber)
        
    def activeVideo(self):
        if not self.activeVideoName in self.videos.keys() :
            return None
        return self.videos[self.activeVideoName]
        
    def setScale(self, scale):
        self.activeVideo().setScale(scale)
        
    def chamberAdded(self, chamber):
        self.signalChamberAdded.emit(chamber)
        
    def chamberDeleted(self, chamber):
        self.signalChamberDeleted.emit(chamber)
        
        
        
            
        
        
        
        
        
        
        