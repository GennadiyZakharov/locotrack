'''
Created on 18.03.2011

@author: Gena
'''

from PyQt4 import QtCore,QtGui

class LtActions(QtCore.QObject):
    '''
    classdocs
    '''

    def __init__(self,parent=None):
        '''
        Constructor
        '''
        super(LtActions, self).__init__(parent)
        
        # Creating actions
        '''
        self.fileNewAction = self.createAction("&New...", QtGui.QKeySequence.New, 
                                          "filenew", "Create an image file")
        self.fileOpenAction = self.createAction("&Open...",
                            QtGui.QKeySequence.Open, "fileopen", "Open image file")
        self.fileSaveAction = self.createAction("&Save",
                            QtGui.QKeySequence.Save, "filesave", "Save file")
        self.fileSaveAsAction = self.createAction("Save &as...",
                            QtGui.QKeySequence.SaveAs, "filesaveas", "Save file as")
        self.filePrintAction = self.createAction("&Print...",
                            QtGui.QKeySequence.Print, "fileprint", "Print image")
        self.fileQuitAction = self.createAction("&Exit",
                            "Esc", "filequit", "Close the application")
        '''
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
                             self.videoRewAction,self.videoFwdAction,)
        
        
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

