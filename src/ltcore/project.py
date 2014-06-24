'''
Created on Jun 20, 2014

@author: gzakharov
'''
from __future__ import print_function
from __future__ import division

from PyQt4 import QtCore
from ltcore.consts import videoFormats
from ltcore.video import Video

class Project(QtCore.QObject):
    '''
    This class hols all information about project:
    main project folder, list of all included videofiles, etc
    '''
    signalProjectUpdated = QtCore.pyqtSignal()

    def __init__(self, projectFolder, parent=None):
        '''
        Constructor
        '''
        super(Project, self).__init__(parent)
        self.projectFolder = QtCore.QDir(projectFolder)
        self.videos = []
        self.loadProject()
        
    def loadProject(self):
        videoFiles = self.projectFolder.entryList(['*.'+videoFormat for videoFormat in videoFormats], QtCore.QDir.Files | QtCore.QDir.NoSymLinks)
        if not videoFiles.isEmpty():
            for videoFile in videoFiles :
                video = Video(videoFile)
                self.videos.append(video)
            self.signalProjectUpdated.emit()
            
        
        
        
        
        
        
        