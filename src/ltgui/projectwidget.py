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
        self.videoItems = {}
        
        self.project.signalProjectUpdated.connect(self.updateProject)
        self.project.signalVideoSelected.connect(self.selectVideo)
        self.currentItemChanged.connect(self.changeItem)
        
     
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
        self.videoItems = {}
        self.clear()
        for videoFileName,video in self.project.videos.items() :
            videoItem = QtGui.QTreeWidgetItem()
            self.videoItems[videoFileName] = videoItem
            caption = QtCore.QFileInfo(videoFileName).baseName()
            videoItem.setText(0,caption)
            videoItem.videoFileName = videoFileName
            self.addTopLevelItem(videoItem)
            '''
            if len(video.chambers) > 0 :
                chamberItems = {}
                for chamber in video.chambers :
                    chamberItem = QtGui.QTreeWidgetItem()
                    chamberItem.setText(0,'Chamber {}'.format(chamber.number))
                    chamberItems[chamber.number]=chamberItem
                videoItem.addChildren(chamberItems.values())
                self.expandItem(videoItem)
            '''
    def changeItem(self, current, previous):
        fileName = current.videoFileName
        self.project.setActiveVideo(fileName)
        
    def selectVideo(self, videoFileName):
        self.SelectItem
        
        
    
            
        