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
        self.setColumnCount(1)
        
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
            
        