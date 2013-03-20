'''
Created on 18.03.2011

@author: Gena
'''

from PyQt4 import QtCore, QtGui
import platform

from ltcore.signals import *
from ltcore.consts import *

from ltcore.cvprocessor import CvProcessor
from ltcore.ltactions import addActions,createAction

import imagercc

#from ltgui.cvlabel import CvLabel
from ltgui.cvgraphics import CvGraphics
from ltgui.videowidget import VideoWidget
from ltgui.chamberswidget import ChambersWidget
from ltgui.cvprocessorwidget import CvProcessorWidget
from ltgui.trajectorywidget import TrajectoryWidget
from ltgui.helpwidget import HelpWidget


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
        # ==== Creating core functional units ====
        #self.ltActions = LtActions(self) # Actions
        self.cvProcessor = CvProcessor(self)                
        # ==== Creating GUI ====
        #status = self.statusBar()
        #status.setSizeGripEnabled(False)
        # ---- Creating main video widget ----
        self.cvLabel = CvGraphics(self)
        self.cvLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.cvLabel.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.cvLabel.setObjectName("cvLabel")
        self.setCentralWidget(self.cvLabel)
        self.cvProcessor.signalNextFrame.connect(self.cvLabel.putImage)
        
        # ---- Creating dock panel for video player ----
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
        self.chambersWidget = ChambersWidget(self.cvProcessor.chambers) 
        #self.chambersWidget.analysisMethod.stateChanged.connect(self.cvProcessor.setAnalysisMethod)
        chambersDockPanel.setWidget(self.chambersWidget)
        # ---- chambersWidget ----
        self.connect(self.chambersWidget, signalEnableDnD, self.cvLabel.enableSelection)        
        self.connect(self.cvLabel, signalRegionSelected, self.chambersWidget.regionSelected)
        
        self.chambersWidget.signalChamberSelected.connect(
            self.cvLabel.selectChamberGui)
        self.chambersWidget.signalSetScale.connect(self.cvProcessor.setScale)
        
        self.cvLabel.signalChamberSelected.connect(
            self.chambersWidget.selectChamber)
        
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
        cvProcessorDockPanel.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        cvProcessorDockPanel.setFeatures(QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, cvProcessorDockPanel)
        self.cvProcessorWidget = CvProcessorWidget(self.cvProcessor) 
        cvProcessorDockPanel.setWidget(self.cvProcessorWidget)
        # ---- Creating dock panel for trajectory Widget
        cvTrajectoryDockPanel = QtGui.QDockWidget("Trajectory", self) # Created and set caption
        cvTrajectoryDockPanel.setObjectName("TrajectoryDockWidget")
        cvTrajectoryDockPanel.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        cvTrajectoryDockPanel.setFeatures(QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, cvTrajectoryDockPanel)
        self.cvTrajectoryWidget = TrajectoryWidget(self.cvProcessor.runRestAnalyser) 
        cvTrajectoryDockPanel.setWidget(self.cvTrajectoryWidget)
        self.chambersWidget.actionRecordTrajectory.toggled.connect(self.cvProcessor.setRecordTrajectory)
        self.chambersWidget.actionSaveTrajectory.triggered.connect(self.cvProcessor.saveProject)
        self.connect(self.cvTrajectoryWidget, signalAnalyseTrajectory, self.cvProcessor.analyseChambers)
        
        # ==== Creating menu ====
        
        projectMenu = self.menuBar().addMenu("&Project")
        self.quitAction = createAction(self,"Exit...", QtGui.QKeySequence.Quit, 
                                          "application-exit", "Exit program")
        projectMenu.addAction(self.quitAction)
        '''
        projectToolbar = self.addToolBar("Project")
        projectToolbar.setObjectName("projectToolBar")
        addActions(projectToolbar, (self.quitAction,))
        '''
        videoMenu = self.menuBar().addMenu("&Video")
        addActions(videoMenu, self.videoWidget.actions)
        chamberMenu = self.menuBar().addMenu("&Chamber")
        addActions(chamberMenu, self.chambersWidget.actions)
        trajectoryMenu = self.menuBar().addMenu("&Trajectory")
        addActions(trajectoryMenu, self.cvTrajectoryWidget.actions)
        
        helpMenu = self.menuBar().addMenu("&Help")
        helpAboutAction = createAction(self,"&About LocoTrack",'',
                                       'help-about','')
        helpAboutAction.triggered.connect(self.helpAbout)
        helpHelpAction = createAction(self,"&Help", QtGui.QKeySequence.HelpContents,
                                      'help-contents')
        helpHelpAction.triggered.connect(self.helpHelp)
        addActions(helpMenu, (helpAboutAction, helpHelpAction))
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
        self.quitAction.triggered.connect(self.close)      
        # Restore window settings
        settings = QtCore.QSettings()
        self.restoreGeometry(settings.value("ltMainWindow/Geometry").toByteArray())
        self.restoreState(settings.value("ltMainWindow/State").toByteArray())
        
    # ==== Slots to handle actions ====
    
    def saveProject(self):
        pass
    
    def okToContinue(self):
        if False:
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
    
    def showInfo(self, messageKind, messageText):
        '''
        Show info message and log it to logFile
        '''
        if messageKind == 0 :
            self.statusBar().showMessage(messageText,5000)
        elif messageKind == -1 :
            QtGui.QMessageBox('Error: '+messageText)
    
    # Close Event handler
    def closeEvent(self, event):
        # Asking user to confirm
        #if self.okToContinue():
        # Save settings and exit 
        settings = QtCore.QSettings()
        settings.setValue("ltMainWindow/Geometry", 
                          QtCore.QVariant(self.saveGeometry()))
        settings.setValue("ltMainWindow/State", 
                          QtCore.QVariant(self.saveState()))
        
    def helpAbout(self):
        QtGui.QMessageBox.about(self, "About LocoTrack",
                """<b>LocoTrack</b> v {0}
                <p>Copyright &copy; 2012-2013. 
                All rights reserved.
                <p>This application can be used to .
                
                <p>Python {1} - Qt {2} - PyQt {3} on {4}""".format(
                applicationVersion, platform.python_version(),
                QtCore.QT_VERSION_STR, QtCore.PYQT_VERSION_STR,
                platform.system()))
    
    def helpHelp(self):
        form = HelpWidget("index.html", self)
        form.show()