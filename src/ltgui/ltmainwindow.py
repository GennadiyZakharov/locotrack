'''
Created on 18.03.2011

@author: Gena
'''

import sys,os
from PyQt4 import QtCore,QtGui

from ltcore.signals import *
from ltcore.cvplayer import CvPlayer
from ltcore.chambersmanager import ChambersManager
from ltcore.actions import LtActions
from ltgui.cvlabel import CvLabel
from ltgui.videodockbar import VideoDockBar
from ltgui.chambersdockbar import ChambersDockBar

class LtMainWindow(QtGui.QMainWindow):
    '''
    classdocs
    '''

    def __init__(self,parent=None):
        '''
        Constructor
        '''
        super(LtMainWindow, self).__init__(parent)
        self.setWindowTitle("LocoTrack")
        self.setObjectName("ltMainWindow")
        
        #Signals
                
        # ==== Creating core functional units
        self.ltActions=LtActions()
        self.cvPlayer = CvPlayer(self)
        self.connect(self, QtCore.SIGNAL("captureFile"),self.cvPlayer.on_captureFromFile)
        self.chambersManager = ChambersManager()
        self.chambersManager.addChamber(100,100,250,220)
        self.chambersManager.addChamber(270,100,340,270)
        self.chambersManager.selectChamber(0)
        self.connect(self, signalAccumulate,self.chambersManager.on_Accumulate)
             
        
                
        # ==== Creating GUI ====
        # Creating main video widget
        self.cvLabel = CvLabel()
        self.cvLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.cvLabel.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.cvLabel.setObjectName("cvLabel")
        self.setCentralWidget(self.cvLabel)
        
        
        #Creating dockbar for videoplayer
        videoDockWidget = QtGui.QDockWidget("Video Control", self) # Created and set caption
        videoDockWidget.setObjectName("videoDockWidget")
        videoDockWidget.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
        videoDockWidget.setFeatures(QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, videoDockWidget)
        
                      
        #Populating videoplayer dockbar
        self.videoDockBar=VideoDockBar() 
        videoDockWidget.setWidget(self.videoDockBar)
        
        self.connect(self.videoDockBar.playButt, signalClicked,self.ltActions.videoPlayAction.trigger)
        self.connect(self.videoDockBar.stopButt, signalClicked,self.ltActions.videoStopAction.trigger)
        self.connect(self.videoDockBar.rewButt, signalClicked,self.ltActions.videoRewAction.trigger)
        self.connect(self.videoDockBar.fwdButt, signalClicked,self.ltActions.videoFwdAction.trigger)
        self.connect(self.videoDockBar.videoSlider, signalValueChanged,self.cvPlayer.on_Seek)
        
        self.connect(self.cvPlayer,signalCvPlayerCapturing,self.videoDockBar.on_videoCapturing)
         
        #Creating dockbar for chambers
        chambersDockWidget = QtGui.QDockWidget("Chambers", self) # Created and set caption
        chambersDockWidget.setObjectName("chambersDockWidget")
        chambersDockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        chambersDockWidget.setFeatures(QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, chambersDockWidget)
        
        #Populating chambers dockbar
        
        self.chambersDockBar=ChambersDockBar() 
        chambersDockWidget.setWidget(self.chambersDockBar)
        self.connect(self.chambersDockBar.brighnessSlider, signalValueChanged,
                     self.cvPlayer.on_BrightnessChanged)
        self.connect(self.chambersDockBar.contrastSlider, signalValueChanged,
                     self.cvPlayer.on_ContrastChanged)
        self.connect(self.chambersDockBar.accumulateButt, signalClicked,
                     self.on_Accumulate)
        self.connect(self.chambersDockBar.negativeChechBox, signalStateChanged,
                     self.chambersManager.on_Invert)
        

        #Creating file menu
        fileMenu = self.menuBar().addMenu("&File")
        
        # Creating video menu
        videoMenu = self.menuBar().addMenu("&Video")
        self.ltActions.addActions(videoMenu, self.ltActions.videoActions)
        
        # ==== Making Connections from actions ====
        # ---- Video actions ----
        self.connect(self.ltActions.videoOpenAction,    signalTriggered,self.on_videoOpen)
        self.connect(self.ltActions.videoCaptureAction, signalTriggered,self.cvPlayer.on_captureFromCam)
        self.connect(self.ltActions.videoPlayAction,    signalTriggered,self.cvPlayer.on_Play)
        self.connect(self.ltActions.videoStopAction,    signalTriggered,self.cvPlayer.on_Stop)
        self.connect(self.ltActions.videoRewAction,     signalTriggered,self.cvPlayer.on_Rew)
        self.connect(self.ltActions.videoFwdAction,     signalTriggered,self.cvPlayer.on_Fwd)
        
        
        self.connect(self.cvPlayer,signalNextFrame,self.chambersManager.on_nextFrame)
        self.connect(self.chambersManager,signalNextFrame,self.cvLabel.putImage)
        
        #QtCore.SIGNAL()
        
    # ==== Slots to handle actions ====
    def on_videoOpen(self):
        '''
        Open video
        '''
        # Setting last user dir
        dir = os.path.dirname(self.cvPlayer.fileName) \
            if self.cvPlayer.fileName is not None else "."
        # Creating formats list
        formats = ["*.%s" % unicode(format).lower() \
                   for format in ('avi','mpg','ogg')]
        # Executing standard open dialog
        fname = unicode(QtGui.QFileDialog.getOpenFileName(self,
                        "Choose Image",
                        dir, "Image files (%s)" % " ".join(formats)))
        
        if fname is not None :
            self.emit(QtCore.SIGNAL("captureFile"),fname)
        
    def on_CvPlayerCapturing(self,length):
        pass 
    
    def on_Accumulate(self):
        print "accumulate"
        self.emit(signalAccumulate, self.chambersDockBar.accumulateSpinBox.value())
        
        
        
    '''    
    def okToContinue(self):
        if self.dirty:
            reply = QtGui.QMessageBox.question(self,
                                         "Image Changer - Unsaved Changes",
                                         "Save unsaved changes?",
                                         QMessageBox.Yes|QMessageBox.No|
                                         QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                return False
            elif reply == QMessageBox.Yes:
                self.fileSave()
        return True
'''