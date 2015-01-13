'''
Created on Jun 20, 2014

@author: gzakharov
'''
from __future__ import print_function
from __future__ import division

from glob import glob
import os
from PyQt4 import QtCore
from ltcore.consts import videoFormats
from ltcore.video import Video
from ltcore.chamber import Chamber
from ltcore.chambersmanager import ChambersManager
from ltcore.trajectoryanalysis import TrajectoryAnalysis

class Project(QtCore.QObject):
    '''
    This class hols all information about project:
    main project folder, list of all included videofiles, etc
    '''
    projectCaption = 'Locotrack project 1.0\n'
    
    signalProjectOpened  = QtCore.pyqtSignal(QtCore.QString)
    signalProjectClosed  = QtCore.pyqtSignal()
    
    signalVideoAdded     = QtCore.pyqtSignal(QtCore.QString)
    signalVideoRemoved   = QtCore.pyqtSignal(QtCore.QString)
    
    signalVideoSelected  = QtCore.pyqtSignal(QtCore.QString)
    signalChambersMangerChanged = QtCore.pyqtSignal(ChambersManager)
    
    signalChamberAdded = QtCore.pyqtSignal(Chamber)   # New chamber added to list
    signalChamberDeleted = QtCore.pyqtSignal(Chamber) # Chamber removed from list 
    
    signalRecalculateChambers = QtCore.pyqtSignal()   # Need to recalculate object position
    
    signalActionStarted = QtCore.pyqtSignal(QtCore.QString, int)
    signalActionProcesing = QtCore.pyqtSignal(int)
    signalActionCompleted = QtCore.pyqtSignal() 

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(Project, self).__init__(parent)
        self.projectFileName = QtCore.QString()
        self.videos = {}
        self.activeVideoName = QtCore.QString()
        self.trajectoryAnalysis = TrajectoryAnalysis(self)
    
    def isEmpty(self):
        return self.projectFileName.isEmpty()
    
    def openProject(self, projectFileName):
        projectFile = open(unicode(projectFileName), 'r')
        caption = projectFile.readline().strip()
        if caption <> self.projectCaption.strip() :
            print('This is not a locotrack project')
            return
        videoFiles = projectFile.readlines()
        #videoFiles = self.projectFolder.entryList(['*.'+videoFormat for videoFormat in videoFormats], QtCore.QDir.Files | QtCore.QDir.NoSymLinks)
        if not videoFiles == []:
            self.projectFileName=projectFileName
            for videoFile in videoFiles :
                if os.path.exists(videoFile.strip()):
                    self.addVideo(QtCore.QString(videoFile.strip()))
        self.signalProjectOpened.emit(QtCore.QFileInfo(self.projectFileName).baseName())
              
    def saveProject(self, projectFileName=QtCore.QString()):
        if not projectFileName.isEmpty():
            self.projectFileName = projectFileName
            self.signalProjectOpened.emit(QtCore.QFileInfo(self.projectFileName).baseName())
        print('Saving project {}'.format(self.projectFileName))
        projectFile = open(unicode(self.projectFileName), 'w')
        projectFile.write(self.projectCaption)
        for videoFileName,video in self.videos.items() :
            projectFile.write(unicode(videoFileName)+'\n')
            video.saveChambers()
        projectFile.close()
            
    def closeProject(self):
        videoNames = self.videos.keys()[:]
        for videoFileName in videoNames:
            self.removeVideo(videoFileName)
        self.signalProjectClosed.emit()
    
    def addVideo(self, videoFileName):
        print('Adding video file to project: ' + videoFileName)
        video = Video(videoFileName)
        self.videos[videoFileName] = video
        video.chambers.signalRecalculateChambers.connect(self.recalculateChambers)
        video.loadChambers()
        self.signalVideoAdded.emit(videoFileName)
        self.setActiveVideo(videoFileName)
        
    def removeVideo(self, videoFileName):
        if not videoFileName in self.videos.keys():
            return
        if videoFileName == self.activeVideoName :
            self.setActiveVideo(QtCore.QString())
        del self.videos[videoFileName]
        self.signalVideoRemoved.emit(videoFileName)
        print('Video removed from project: ',videoFileName)
        if self.videos != {} :
            self.setActiveVideo(self.videos.keys()[0])
            
    def setActiveVideo(self, videoFileName):
        if self.activeVideoName == videoFileName :
            return
        video = self.activeVideo()
        if video is not None :
            print('Deselecting video: ',self.activeVideoName)
            video.chambers.signalChamberAdded.disconnect(self.chamberAdded)
            video.chambers.signalChamberDeleted.disconnect(self.chamberDeleted)
            #signal to remove chambers to cvGraphics
            for chamber in video.chambers :
                self.signalChamberDeleted.emit(chamber)
            #self.signalChambersMangerChanged.emit(None)
            
        self.activeVideoName = videoFileName
        if not self.activeVideoName.isEmpty():
            print('Selecting video: ',self.activeVideoName)
            self.signalChambersMangerChanged.emit(self.activeVideo().chambers)
            video = self.activeVideo()
            video.chambers.signalChamberAdded.connect(self.chamberAdded)
            video.chambers.signalChamberDeleted.connect(self.chamberDeleted)
            #putting chambers on cvGraphics
            for chamber in video.chambers :
                self.signalChamberAdded.emit(chamber)
        else :
            self.signalChambersMangerChanged.emit(None)
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
        
    def videoEnded(self):
        video = self.activeVideo()
        video.chambers.setRecordTrajectories(False)
        video.saveChambers()
   
    def chamberAdded(self, chamber):
        self.signalChamberAdded.emit(chamber)
        
    def chamberDeleted(self, chamber):
        self.signalChamberDeleted.emit(chamber)
        
    def recalculateChambers(self):
        self.signalRecalculateChambers.emit()
        
    def createTrajectoryImages(self):
        video = self.activeVideo()
        if video is not None :
            video.chambers.createTrajectoryImages() 
            
    def analyseProject(self):
        '''
        tracksCount = sum([len(video.chambers) for video in self.videos.values()])
        self.signalActionStarted.emit('',tracksCount)
        print('Analysing traks count: ',tracksCount)
        count = 0
        for video in self.videos.values() :
            for chamber in video.chambers :
                count +=1
                self.signalActionProcesing.emit(count)
                trajectoryStats = self.trajectoryAnalysis.analyseChamber(chamber,video.chambers.scale,video.frameRate)
                chamber.setTrajectoryStats(trajectoryStats)
        self.signalActionCompleted.emit()
        '''
        chamberList = []
        for video in self.videos.values() :
            for chamber in video.chambers :
                chamberList.append((chamber,video.chambers.scale,video.frameRate))
                
        self.trajectoryAnalysis.analyseChambers(chamberList)
        projectStatsFile = open(unicode(self.projectFileName)+'.txt', 'w')
        for video in self.videos.values() :
            for chamber in video.chambers :
                if chamber.trajectoryStats is not None:
                    stats = chamber.trajectoryStats.totalInfo()
                    projectStatsFile.write(stats+'\n')
        
        
        
        
            
        
        
        
        
        
        
        