'''
Created on 18.03.2011

@author: Gena
'''

import sys, os
from PyQt4 import QtCore, QtGui

from ltcore.signals import *
from ltcore.consts import *

from ltcore.cvplayer import CvPlayer
from ltcore.chambersmanager import ChambersManager
from ltcore.ltactions import LtActions

from ltgui.cvlabel import CvLabel
from ltgui.videowidget import VideoWidget
from ltgui.chamberswidget import ChambersWidget
from ltgui.cvprocessorwidget import CvProcessorWidget


class LtMainWindow(QtGui.QMainWindow):
    '''
    Locotrack main window
    '''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(LtMainWindow, self).__init__(parent)
        self.setWindowTitle(appName + ' ' + appVersion)
        self.setObjectName("ltMainWindow")
                
        self.dirty = True
        
        # ==== Creating core functional units ====
        self.ltActions = LtActions(self) # Actions
        self.cvPlayer = CvPlayer(self)
        self.chambersManager = ChambersManager(self)           
                
        # ==== Creating GUI ====
        # ---- Creating main video widget ----
        self.cvLabel = CvLabel()
        self.cvLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.cvLabel.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.cvLabel.setObjectName("cvLabel")
        self.setCentralWidget(self.cvLabel)
        
        # ---- Creating dock panel for videoplayer ----
        videoDockPanel = QtGui.QDockWidget("Video Control", self)
        videoDockPanel.setObjectName("videoDockWidget")
        videoDockPanel.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
        videoDockPanel.setFeatures(QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, videoDockPanel)
        self.videoWidget = VideoWidget() 
        videoDockPanel.setWidget(self.videoWidget)
        
        # ---- Creating dock panel for chambers ---- 
        chambersDockPanel = QtGui.QDockWidget("Chambers", self) # Created and set caption
        chambersDockPanel.setObjectName("chambersDockWidget")
        chambersDockPanel.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        chambersDockPanel.setFeatures(QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, chambersDockPanel)
        self.chambersWidget = ChambersWidget() 
        chambersDockPanel.setWidget(self.chambersWidget)
        
        # ---- Creating dock panel for image processing ---- 
        cvProcessorDockPanel = QtGui.QDockWidget("Image processor", self) # Created and set caption
        cvProcessorDockPanel.setObjectName("chambersDockWidget")
        cvProcessorDockPanel.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        cvProcessorDockPanel.setFeatures(QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, cvProcessorDockPanel)
        self.cvProcessorWidget = CvProcessorWidget() 
        cvProcessorDockPanel.setWidget(self.cvProcessorWidget)
                     
        # ==== Creating menu ====
        projectMenu = self.menuBar().addMenu("&Project")
        self.ltActions.addActions(projectMenu, self.ltActions.projectActions)
        
        videoMenu = self.menuBar().addMenu("&Video")
        self.ltActions.addActions(videoMenu, self.ltActions.videoActions)
        
        # ==== Making Connections actions ====
        # ---- Core video processing ----
        self.connect(self.cvPlayer, signalNextFrame, self.chambersManager.on_nextFrame)
        self.connect(self.cvPlayer, signalNextFrame, self.videoWidget.on_NextFrame)
        self.connect(self.chambersManager, signalNextFrame, self.cvLabel.putImage)
        
        self.connect(self.cvLabel, signalRegionSelected, self.chambersWidget.on_RegionSelected)
        self.connect(self.chambersWidget, signalEnableDnD, self.cvLabel.on_EnableDnD)
        
        # ---- self ----
        self.connect(self, signalCaptureFromFile, self.cvPlayer.on_captureFromFile)
        
        # ---- videoWidget ----
        self.connect(self.videoWidget.playButt, signalClicked, self.ltActions.videoPlayAction.trigger)
        self.connect(self.videoWidget.stopButt, signalClicked, self.ltActions.videoStopAction.trigger)
        self.connect(self.videoWidget.rewButt, signalClicked, self.ltActions.videoRewAction.trigger)
        self.connect(self.videoWidget.fwdButt, signalClicked, self.cvPlayer.timerEvent)
        self.connect(self.videoWidget.videoSlider, signalValueChanged, self.cvPlayer.on_Seek)
        self.connect(self.cvPlayer, signalCvPlayerCapturing, self.videoWidget.on_videoCapturing)
        self.connect(self.videoWidget.brighnessSlider, signalValueChanged,
                     self.cvPlayer.on_BrightnessChanged)
        self.connect(self.videoWidget.contrastSlider, signalValueChanged,
                     self.cvPlayer.on_ContrastChanged)
        
        # ---- chambersWidget ----
       
        self.connect(self.chambersWidget, signalSetChamber,
                     self.chambersManager.on_SetChamber)
        self.connect(self.chambersWidget, signalSetScale,
                     self.chambersManager.on_SetScale)
        self.connect(self.chambersWidget, signalChangeSelection,
                     self.chambersManager.on_SelectChamber)
        self.connect(self.chambersManager, signalChambersUpdated,
                     self.chambersWidget.on_chamberListUpdated)
        self.connect(self.chambersWidget.batchButton, signalClicked,
                     self.cvPlayer.on_StartBatchProcess)
        
        # ---- cvProcessorWidget ----
        self.connect(self.cvProcessorWidget.negativeChechBox.checkBox, signalStateChanged,
                     self.chambersManager.on_Invert)
        self.connect(self.cvProcessorWidget.showProcessedChechBox.checkBox, signalStateChanged,
                     self.chambersManager.on_ShowProcessed)
        self.connect(self.cvProcessorWidget.showContourChechBox.checkBox, signalStateChanged,
                     self.chambersManager.on_ShowContour)
        self.connect(self.cvProcessorWidget.tresholdSlider, signalValueChanged,
                     self.chambersManager.on_SetTreshold)
        self.connect(self.cvProcessorWidget, signalAccumulate, self.chambersManager.on_Accumulate)
        
        
        # ---- Main menu ----
        # Project menu
        self.connect(self.ltActions.projectQuitAction, signalTriggered, self.close)
        
        # Video Menu
        self.connect(self.ltActions.videoOpenAction, signalTriggered, self.on_videoOpen)
        self.connect(self.ltActions.videoCaptureAction, signalTriggered, self.cvPlayer.on_captureFromCam)
        self.connect(self.ltActions.videoPlayAction, signalTriggered, self.cvPlayer.on_Play)
        self.connect(self.ltActions.videoStopAction, signalTriggered, self.cvPlayer.on_Stop)
        self.connect(self.ltActions.videoRewAction, signalTriggered, self.cvPlayer.on_Rew)
        self.connect(self.ltActions.videoFwdAction, signalTriggered, self.cvPlayer.on_Fwd)
        
        
        
        # !!!!!!!!!!! Testing !!!!!!!!!!!!!!!
     
    # ==== Slots to handle actions ====
    def on_videoOpen(self):
        '''
        Open video file
        '''
        # Setting last user dir
        dir = os.path.dirname(self.cvPlayer.fileName) \
            if self.cvPlayer.fileName is not None else "."
        # Creating formats list
        formats = ["*.%s" % unicode(format).lower() \
                   for format in ('avi', 'mpg', 'ogg')]
        # Executing standard open dialog
        fname = unicode(QtGui.QFileDialog.getOpenFileName(self,
                        "Choose Image",
                        dir, "Image files (%s)" % " ".join(formats)))
        
        if fname is not None :
            self.emit(signalCaptureFromFile, fname)
        
    def on_CvPlayerCapturing(self, length):
        pass 
    
    def on_Accumulate(self):
        self.emit(signalAccumulate, self.chambersDockBar.accumulateSpinBox.value())        
    
    def saveProject(self):
        pass
    
    def okToContinue(self):
        if self.dirty:
            reply = QtGui.QMessageBox.question(self,
                                         appName + " - Unsaved Changes",
                                         "Save unsaved changes?",
                                         QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | 
                                         QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Cancel:
                return False
            elif reply == QtGui.QMessageBox.Yes:
                self.saveProject()
        return True
    
    # Close Event handler
    def closeEvent(self, event):
        # Asking user to confirm
        if self.okToContinue():
            # Save settings and exit
            '''
            settings = QtCore.QSettings()
            filename = QtCore.QVariant(QtCore.QString(self.filename)) \
                if self.filename is not None else QtCore.QVariant()
            settings.setValue("LastFile", filename)
            recentFiles = QtCore.QVariant(self.recentFiles) \
                if self.recentFiles else QtCore.QVariant()
            settings.setValue("RecentFiles", recentFiles)
            settings.setValue("Geometry", QtCore.QVariant(self.saveGeometry()))
            settings.setValue("MainWindow/State",
                              QtCore.QVariant(self.saveState()))
            '''
        else:
            event.ignore()
