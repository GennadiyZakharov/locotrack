'''
Created on Jun 20, 2014

@author: gzakharov
'''
from __future__ import division,print_function

from PyQt4 import QtCore, QtGui
from ltcore.consts import videoFormats,projectExtension
from ltcore.ltactions import createAction
from ltgui.actionbutton import ActionButton
import imagercc

class ProjectWidget(QtGui.QWidget):
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
        self.videoList = QtGui.QTreeWidget()
        self.videoList.setColumnCount(1)
        self.videoList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        
        layout1 = QtGui.QVBoxLayout()
        layout1.addWidget(self.videoList)
        self.setLayout(layout1)
        self.actionOpenProject = createAction(self,"&Open...", "",
                                       "project-open", "Open project")
        self.actionOpenProject.triggered.connect(self.openProject)
        self.actionSaveProject = createAction(self,"&Save", "",
                                       "document-save", "Save project")
        self.actionSaveProject.triggered.connect(self.saveProject)
        self.actionSaveProjectAs = createAction(self,"Save &as...", "",
                                       "document-save-as", "Save project as")
        self.actionSaveProjectAs.triggered.connect(self.saveProjectAs)
        self.actionCloseProject = createAction(self,"&Close", "",
                                       "project-development-close", "Close project")
        self.actionCloseProject.triggered.connect(self.closeProject)
        self.actionAddVideo = createAction(self,"&Add video...", "",
                                       "document-open", "Add video file to project")
        self.actionAddVideo.triggered.connect(self.addVideo)
        self.actionCaptureVideo = createAction(self,"&Capture video...", "",
                                          "camera-web", "")
        #self.actionCaptureVideo.triggered.connect(self.captureVideo)
        self.actionRemoveVideo = createAction(self,"Remove video", "",
                                          "dialog-close", "")
        self.actionRemoveVideo.triggered.connect(self.removeVideo)
        
        
        self.actionAnalyseProject = createAction(self, "&Analyse project", "",
                                       "", "Analyse whole files in project and make statistics")
        self.actionAnalyseProject.triggered.connect(self.analyseProject)
        
        self.actions = (self.actionOpenProject,self.actionSaveProject,self.actionSaveProjectAs,self.actionCloseProject,None,
                        self.actionAddVideo,self.actionRemoveVideo,None,self.actionAnalyseProject)
        
        
        self.videoList.setHeaderLabel('Video Files')
        self.videoItems = {}
        
        self.project.signalVideoAdded.connect(self.videoAdded)
        self.project.signalVideoRemoved.connect(self.videoRemoved)
        #self.project.signalProjectUpdated.connect(self.updateProject)
        self.project.signalVideoSelected.connect(self.selectVideo)
        self.videoList.itemClicked.connect(self.changeItem)
        
        # Open and capture video buttons
        layout2=QtGui.QHBoxLayout()
        videoAddButton = ActionButton(self.actionAddVideo)
        layout2.addWidget(videoAddButton)
        #videoCaptureButton = ActionButton(self.actionCaptureVideo)
        #layout2.addWidget(videoCaptureButton)
        videoRemoveButton = ActionButton(self.actionRemoveVideo)
        layout2.addWidget(videoRemoveButton)
        layout1.addLayout(layout2)
        
    @QtCore.pyqtSlot()
    def openProject(self):
        # Executing standard open dialog
        projectName = QtGui.QFileDialog.getOpenFileName(self,
                        "Choose project file",
                        self.lastDirectory, "Locotrack project file ({})".format("*."+projectExtension))
        if not projectName.isEmpty() :
            self.lastDirectory=QtCore.QFileInfo(projectName).absolutePath()
            self.project.openProject(projectName)
            
    def saveProject(self):
        if self.project.projectFileName.isEmpty():
            self.saveProjectAs()
        else:
            self.project.saveProject()
    
    def saveProjectAs(self):
        formats = ["*.ltp"]
        projectName = QtGui.QFileDialog.getSaveFileName(self,
                        "Choose project file",
                        self.lastDirectory, "Locotrack project file ({})".format(" ".join(formats)))
        if not projectName.isEmpty() :
            self.lastDirectory=QtCore.QFileInfo(projectName).absolutePath()
            self.project.saveProject(projectName)
    
    def closeProject(self):
        self.project.closeProject()
            
    @QtCore.pyqtSlot()   
    def addVideo(self):
        '''
        Open video file
        ''' 
        # Creating formats list
        formats = ["*.{}".format(unicode(videoFormat)) \
                   for videoFormat in videoFormats]
        # Executing standard open dialog
        fname = QtGui.QFileDialog.getOpenFileName(self,
                        "Choose video file",
                        self.lastDirectory, "Video files ({})".format(" ".join(formats)))
        if not fname.isEmpty() :
            self.lastDirectory=QtCore.QFileInfo(fname).absolutePath()
            self.project.addVideo(fname)
    
    @QtCore.pyqtSlot()
    def captureVideo(self):
        pass
    
    @QtCore.pyqtSlot()
    def removeVideo(self):
        if not self.project.activeVideoName.isEmpty() : 
            self.project.removeVideo(self.project.activeVideoName)
        
    def videoAdded(self, videoFileName):
        videoItem = QtGui.QTreeWidgetItem()
        self.videoItems[videoFileName] = videoItem
        caption = QtCore.QFileInfo(videoFileName).completeBaseName()
        videoItem.setText(0,caption)
        videoItem.videoFileName = videoFileName
        self.videoList.addTopLevelItem(videoItem)
        
    def videoRemoved(self, videoFileName):
        print('removing video',videoFileName)
        videoItem = self.videoItems[videoFileName]
        self.videoList.invisibleRootItem().removeChild(videoItem)
        del self.videoItems[videoFileName]
        self.project.setActiveVideo(QtCore.QString())
        
    @QtCore.pyqtSlot()
    def updateProject(self):
        self.videoItems = {}
        self.videoList.clear()
        for videoFileName,video in self.project.videos.items() :
            videoItem = QtGui.QTreeWidgetItem()
            self.videoItems[videoFileName] = videoItem
            caption = QtCore.QFileInfo(videoFileName).baseName()
            videoItem.setText(0,caption)
            videoItem.videoFileName = videoFileName
            self.videoList.addTopLevelItem(videoItem)
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
        
    def changeItem(self, item, column):
        if item is None :
            return
        fileName = item.videoFileName
        self.project.setActiveVideo(fileName)
        
        
    def selectVideo(self, videoFileName):
        if videoFileName.isEmpty():
            self.videoList.clearSelection()
            return
        item = self.videoItems[videoFileName]
        if item in self.videoList.selectedItems() :
            return
        self.videoList.setCurrentItem(item)
        
    def analyseProject(self):
        self.project.analyseProject()
    
        
        
        
    
            
        