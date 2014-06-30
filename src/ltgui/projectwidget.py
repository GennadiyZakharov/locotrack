'''
Created on Jun 20, 2014

@author: gzakharov
'''
from PyQt4 import QtCore, QtGui
from ltcore.ltactions import createAction
from ltgui.actionbutton import ActionButton
import imagercc

class ProjectWidget(QtGui.QTreeWidget):
    '''
    classdocs
    '''


    def __init__(self, project, parent=None):
        '''
        Constructor
        '''
        super(ProjectWidget, self).__init__(parent)
        self.project = project 
        self.lastDirectory = '.'
        self.actionOpenProject = createAction(self,"&Open...", "",
                                       "document-open", "Open project")
        self.actionOpenProject.triggered.connect(self.openProject)
        self.actionSaveProject = createAction(self,"&Save...", "",
                                       "document-open", "Save project")
        self.actionSaveProject.triggered.connect(self.saveProject)
        self.actionCloseProject = createAction(self,"&Close...", "",
                                       "document-open", "Close project")
        self.actionCloseProject.triggered.connect(self.closeProject)
        self.actions = (self.actionOpenProject,self.actionSaveProject,self.actionCloseProject)
        
        self.setColumnCount(1)
        self.setHeaderLabel('Video Files')
     
    @QtCore.pyqtSlot()
    def openProject(self):
        # Creating formats list
        formats = ["*.ltp"]
        # Executing standard open dialog
        projectName = QtGui.QFileDialog.getOpenFileName(self,
                        "Choose project file",
                        self.lastDirectory, "Video files ({})".format(" ".join(formats)))
        if not projectName.isEmpty() :
            self.lastDirectory=QtCore.QFileInfo(projectName).absolutePath()
            self.project.openProject(projectName)
            
    def saveProject(self):
        pass
    
    def closeProject(self):
        self.project.closeProject()
        
    @QtCore.pyqtSlot()
    def updateProject(self):
        videoItems = []
        for video in self.project.videos:
            videoCaption = video.videoFilePath
            videoItem = QtGui.QTreeWidgetItem(videoCaption)
            if len(video.chambersManager) > 0 :
                chamberItems = []
                for chamber in video.chambersManager :
                    chamberItem = QtGui.QTreeWidgetItem('Chamber {}'.format(chamber.number))
                    chamberItems.append(chamberItem)
                videoItem.addChildren(chamberItems)
            videoItems.append(videoItem)
        self.insertTopLevelItems(videoItems) 
            
        