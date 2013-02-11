'''
Created on 18.03.2011

@author: Gena
'''

import sys, os
from PyQt4 import QtCore, QtGui

from ltcore.signals import *
from ltcore.consts import *

from ltcore.cvprocessor import CvProcessor
from ltcore.ltactions import LtActions

#from ltgui.cvlabel import CvLabel
from ltgui.cvgraphics import CvGraphics
from ltgui.videowidget import VideoWidget
from ltgui.chamberswidget import ChambersWidget
from ltgui.cvprocessorwidget import CvProcessorWidget
from ltgui.trajectorywidget import TrajectoryWidget


class LtMainWindow(QtGui.QMainWindow):
    '''
    Locotrack main window
    '''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(LtMainWindow, self).__init__(parent)
        self.setWindowTitle(applicationName + ' ' + applicationVersion)
        self.setObjectName("ltMainWindow")
                
        self.dirty = False
        
        # ==== Creating core functional units ====
        self.ltActions = LtActions(self) # Actions
        self.cvProcessor = CvProcessor(self)           
                
        # ==== Creating GUI ====
        # ---- Creating main video widget ----
        self.cvLabel = CvGraphics(self)
        self.cvLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.cvLabel.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.cvLabel.setObjectName("cvLabel")
        self.setCentralWidget(self.cvLabel)
        self.connect(self.cvProcessor, signalNextFrame, self.cvLabel.putImage)
        
        
        # ---- Creating dock panel for videoplayer ----
        videoDockPanel = QtGui.QDockWidget("Video Control", self)
        videoDockPanel.setObjectName("videoDockWidget")
        videoDockPanel.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
        videoDockPanel.setFeatures(QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, videoDockPanel)
        self.videoWidget = VideoWidget(self.cvProcessor.cvPlayer) 
        videoDockPanel.setWidget(self.videoWidget)
        
        # ---- Creating dock panel for chambers ---- 
        chambersDockPanel = QtGui.QDockWidget("Chambers", self) # Created and set caption
        chambersDockPanel.setObjectName("chambersDockWidget")
        chambersDockPanel.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        chambersDockPanel.setFeatures(QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, chambersDockPanel)
        self.chambersWidget = ChambersWidget() 
        self.chambersWidget.analysisMethod.stateChanged.connect(self.cvProcessor.setAnalysisMethod)
        chambersDockPanel.setWidget(self.chambersWidget)
        # ---- chambersWidget ----
        self.connect(self.chambersWidget, signalEnableDnD, self.cvLabel.enableSelection)        
        self.connect(self.cvLabel, signalRegionSelected, self.chambersWidget.regionSelected)
        self.connect(self.chambersWidget, signalSetChamber,
                     self.cvProcessor.addChamber)
        self.chambersWidget.signalClearChamber.connect(
                     self.cvProcessor.clearChamber)
        self.chambersWidget.signalChamberSelected.connect(
            self.cvLabel.selectChamberGui)
        
        self.cvLabel.signalChamberSelected.connect(
            self.chambersWidget.selectChamber)
        
        self.connect(self.chambersWidget, signalSetScale,
                     self.cvProcessor.setScale)
        
        self.cvProcessor.chambers.signalChamberAdded.connect(
            self.chambersWidget.addChamber)
        self.cvProcessor.chambers.signalChamberAdded.connect(
            self.cvLabel.addChamberGui)
        self.cvProcessor.chambers.signalChamberDeleted.connect(
            self.chambersWidget.removeChamber)
        self.cvProcessor.chambers.signalChamberDeleted.connect(
            self.cvLabel.delChamberGui)

        
        # ---- Creating dock panel for image processing ---- 
        cvProcessorDockPanel = QtGui.QDockWidget("Image processor", self) # Created and set caption
        cvProcessorDockPanel.setObjectName("chambersDockWidget")
        cvProcessorDockPanel.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        cvProcessorDockPanel.setFeatures(QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, cvProcessorDockPanel)
        self.cvProcessorWidget = CvProcessorWidget() 
        cvProcessorDockPanel.setWidget(self.cvProcessorWidget)
        # ---- Creating dock panel for trajectory Widget
        cvTrajectoryDockPanel = QtGui.QDockWidget("Trajectory", self) # Created and set caption
        cvTrajectoryDockPanel.setObjectName("TrajectoryDockWidget")
        cvTrajectoryDockPanel.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        cvTrajectoryDockPanel.setFeatures(QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, cvTrajectoryDockPanel)
        self.cvTrajectoryWidget = TrajectoryWidget() 
        cvTrajectoryDockPanel.setWidget(self.cvTrajectoryWidget)
        self.connect(self.cvTrajectoryWidget, signalWriteTrajectory, self.cvProcessor.saveObjectToTrajectory)
        self.connect(self.cvTrajectoryWidget, signalAnalyseTrajectory, self.cvProcessor.analyseChambers)
        self.connect(self.cvTrajectoryWidget, signalSampleNameChanged, self.cvProcessor.setSampleName)
        self.cvTrajectoryWidget.signalCreateTrajectoryImages.connect(self.cvProcessor.createTrajectoryImages)
        self.cvTrajectoryWidget.signalAnalyseFromFile.connect(self.cvProcessor.analyseFromFiles)
        self.cvTrajectoryWidget.speedTresholdSlider.setValue(self.cvProcessor.runRestAnalyser.speedTreshold)
        self.cvProcessor.trajectoryWriting.connect(self.cvTrajectoryWidget.trajectoryWriting)
        self.cvTrajectoryWidget.saveTrajectoryButton.clicked.connect(self.cvProcessor.saveProject)             
        
        # ==== Creating menu ====
        projectMenu = self.menuBar().addMenu("&Project")
        self.ltActions.addActions(projectMenu, self.ltActions.projectActions)
        
        videoMenu = self.menuBar().addMenu("&Video")
        self.ltActions.addActions(videoMenu, self.ltActions.videoActions)
        
        # ==== Making Connections actions ====

        # ---- self ----
        self.connect(self, signalCaptureFromFile, self.cvProcessor.loadVideoFile)

        
        
        # ---- cvProcessorWidget ----
        self.connect(self.cvProcessorWidget.negativeChechBox.checkBox, signalStateChanged,
                     self.cvProcessor.setNegative)
        self.connect(self.cvProcessorWidget.showProcessedChechBox.checkBox, signalStateChanged,
                     self.cvProcessor.setShowProcessed)
        self.connect(self.cvProcessorWidget.showContourChechBox.checkBox, signalStateChanged,
                     self.cvProcessor.setShowContour)
        self.cvProcessorWidget.tresholdSlider.valueChanged.connect(
                     self.cvProcessor.setTreshold)
        self.cvProcessorWidget.ellipseCropCheckBox.stateChanged.connect(
                     self.cvProcessor.setEllipseCrop)
        
        # ---- Main menu ----
        # Project menu
        self.connect(self.ltActions.projectQuitAction, signalTriggered, self.close)
        
        # Video Menu
        self.connect(self.ltActions.videoOpenAction, signalTriggered, self.on_videoOpen)
        self.connect(self.ltActions.videoCaptureAction, signalTriggered, self.cvProcessor.cvPlayer.captureFromCam)
        self.connect(self.ltActions.videoPlayAction, signalTriggered, self.cvProcessor.cvPlayer.play)
        #self.connect(self.ltActions.videoStopAction, signalTriggered, self.cvProcessor.cvPlayer.stop)
        self.connect(self.ltActions.videoRewAction, signalTriggered, self.cvProcessor.cvPlayer.seekRew)
        self.connect(self.ltActions.videoFwdAction, signalTriggered, self.cvProcessor.cvPlayer.seekFwd)
        
        
        
        # !!!!!!!!!!! Testing !!!!!!!!!!!!!!!
     
    # ==== Slots to handle actions ====
    def on_videoOpen(self):
        '''
        Open video file
        '''
        # Setting last user dir
        directory = os.path.dirname(self.cvProcessor.cvPlayer.videoFileName) \
            if self.cvProcessor.cvPlayer.videoFileName is not None else "."
        # Creating formats list
        formats = ["*.{}".format(unicode(videoFormat).lower()) \
                   for videoFormat in ('avi', 'mpg', 'ogg')]
        # Executing standard open dialog
        fname = unicode(QtGui.QFileDialog.getOpenFileName(self,
                        "Choose video file",
                        directory, "Video files (%s)" % " ".join(formats)))
        
        if fname is not None :
            self.emit(signalCaptureFromFile, fname)
            self.setWindowTitle(fname)
        
    def on_CvPlayerCapturing(self, length):
        pass 
    
    def accumulate(self):
        self.emit(signalAccumulate, self.chambersDockBar.accumulateSpinBox.value())        
    
    def saveProject(self):
        pass
    
    def okToContinue(self):
        if self.dirty:
            reply = QtGui.QMessageBox.question(self,
                                         " Unsaved Changes",
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
