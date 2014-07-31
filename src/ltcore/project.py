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
    
    signalVideoAdded     = QtCore.pyqtSignal(QtCore.QString)
    signalVideoRemoved   = QtCore.pyqtSignal(QtCore.QString)
    
    signalVideoSelected  = QtCore.pyqtSignal(QtCore.QString)
    signalChambersMangerChanged = QtCore.pyqtSignal(ChambersManager)
    
    signalChamberAdded = QtCore.pyqtSignal(Chamber)   # New chamber added to list
    signalChamberDeleted = QtCore.pyqtSignal(Chamber) # Chamber removed from list 
    
    signalRecalculateChambers = QtCore.pyqtSignal()   # Need to recalculate object position

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
              
    def saveProject(self):
        for video in self.videos.values() :
            video.saveChambers()
            
    def closeProject(self):
        self.projectFolderName = QtCore.QString()
        self.videos = {}
        self.activeVideoName = QtCore.QString()
        #self.signalProjectUpdated.emit()
        
    
    def addVideo(self, videoFileName):
        print('Opening video file ' + videoFileName)
        video = Video(videoFileName)
        self.videos[videoFileName] = video
        video.chambers.signalRecalculateChambers.connect(self.recalculateChambers)
        video.loadChambers()
        self.signalVideoAdded.emit(videoFileName)
        self.setActiveVideo(videoFileName)
        
    def removeVideo(self, videoFileName):
        if videoFileName in self.videos.keys():
            if videoFileName == self.activeVideoName :
                self.setActiveVideo(QtCore.QString())
            del self.videos[videoFileName]
            self.signalVideoRemoved.emit(videoFileName)
            
    def setActiveVideo(self, videoFileName):
        if self.activeVideoName == videoFileName :
            return
        video = self.activeVideo()
        if video is not None :
            video.chambers.signalChamberAdded.disconnect(self.chamberAdded)
            video.chambers.signalChamberDeleted.disconnect(self.chamberDeleted)
            self.signalChambersMangerChanged.emit(None)
            #signal to remove chambers to cvGraphics
            for chamber in video.chambers :
                self.signalChamberDeleted.emit(chamber)
        self.activeVideoName = videoFileName
        if not self.activeVideoName.isEmpty():
            self.signalChambersMangerChanged.emit(self.activeVideo().chambers)
            video = self.activeVideo()
            video.chambers.signalChamberAdded.connect(self.chamberAdded)
            video.chambers.signalChamberDeleted.connect(self.chamberDeleted)
            #putting chambers on cvGraphics
            for chamber in video.chambers :
                self.signalChamberAdded.emit(chamber)
        self.signalVideoSelected.emit(self.activeVideoName)
                
    def activeVideo(self):
        if not self.activeVideoName in self.videos.keys() :
            return None
        return self.videos[self.activeVideoName]
    '''
    @QtCore.pyqtSlot(float)
    def setScale(self, scale):
        if not self.activeVideoName.isEmpty():
            self.activeVideo().setScale(scale)
    ''' 
    def chamberAdded(self, chamber):
        self.signalChamberAdded.emit(chamber)
        
    def chamberDeleted(self, chamber):
        self.signalChamberDeleted.emit(chamber)
        
    def recalculateChambers(self):
        self.signalRecalculateChambers.emit()
        
        
        
        
            
        
        
        
        
        
        
        