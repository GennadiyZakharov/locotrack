'''
Created on 18.03.2011

@author: Gena
'''

from PyQt4 import QtCore,QtGui

class LtActions(QtCore.QObject):
    '''
    This class holds all actions, needed by LtMainWindow
    It also holds additional methods for actions maipulating  
    '''

    def __init__(self,parent=None):
        '''
        Constructor
        '''
        super(LtActions, self).__init__(parent)
        
        # ==== Project actions ====
        self.projectNewAction = self.createAction("&New...", QtGui.QKeySequence.New, 
                                          "filenew", "Create an image file")
        self.projectOpenAction = self.createAction("&Open...",
                            QtGui.QKeySequence.Open, "fileopen", "Open image file")
        self.projectSaveAction = self.createAction("&Save",
                            QtGui.QKeySequence.Save, "filesave", "Save file")
        self.projectSaveAsAction = self.createAction("Save &as...",
                            QtGui.QKeySequence.SaveAs, "filesaveas", "Save file as")
        self.projectQuitAction = self.createAction("&Exit",
                            QtGui.QKeySequence.Quit, "filequit", "Close the application")
        self.projectActions = (self.projectNewAction,self.projectOpenAction,
                               self.projectSaveAction,self.projectSaveAsAction,
                               None,self.projectQuitAction)
        
        # ==== Video Actions ====
        self.videoOpenAction = self.createAction("&Open...", "", 
                                          "videoopen", "Open video file")
        self.videoCaptureAction = self.createAction("&Capture...",
                            "", "videocapture", "")
        self.videoPlayAction = self.createAction("&Play",
                            "", "video", "")
        self.videoStopAction = self.createAction("&Stop",
                            "", "video", "")
        self.videoRewAction = self.createAction("&Rewind",
                            "", "video", "")
        self.videoFwdAction = self.createAction("&Forward",
                            "", "video", "")
        
        self.videoActions = (self.videoOpenAction,self.videoCaptureAction,
                             self.videoPlayAction,self.videoStopAction,
                             self.videoRewAction,self.videoFwdAction)
        
        
    def createAction(self, text, shortcut=None, icon=None,
                    tip=None, checkable=False):
        action = QtGui.QAction(text, self)
        
        if shortcut is not None:
            action.setShortcut(shortcut)
        if icon is not None:
            action.setIcon(QtGui.QIcon(":/%s.png" % icon))
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if checkable:
            action.setCheckable(True)
        return action

# Method to add All actions from the list
    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

