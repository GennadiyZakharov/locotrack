'''
Created on 04.02.2012

@author: gena
'''
from __future__ import division

from PyQt4 import QtCore,QtGui
#from ltcore.actions import LtActions
from ltgui.analysedialog import AnalyseDialog
from ltgui.actionbutton import ActionButton
from ltcore.ltactions import createAction

class TrajectoryWidget(QtGui.QWidget):
    '''
    This widget holds GUI elements for trajectory analysing
    '''
    signalCreateTrajectoryImages = QtCore.pyqtSignal()
    signalAnalyseFromFile = QtCore.pyqtSignal(QtCore.QString, QtCore.QStringList)

    def __init__(self, analyser, parent=None):
        '''
        Constructor
        '''
        super(TrajectoryWidget, self).__init__(parent)
        self.analysisProgressDialog = QtGui.QProgressDialog()
        self.analysisProgressDialog.setWindowTitle('Analysing files')
        #
        
        self.actionAnalyseFromFiles = createAction(self,"&Analyse from files...", "",
                                       "document-open", "Open video file")
        self.actionAnalyseFromFiles.triggered.connect(self.analyseFromFile)
        '''
         = createAction(self,"&Capture...", "",
                                          "camera-web", "")
        actionPlay = createAction(self,"&Play", "", 
                                  "media-playback-start", "", True)
        actionRun =  createAction(self,"&Run", "", 
                                  "fork", "", True)
        actionRew = createAction(self,"&Rewind", "", 
                                 "media-seek-backward", "")
        actionFwd = createAction(self,"&Forward", "", 
                                 "media-seek-forward", "")
        '''
        self.actions = (self.actionAnalyseFromFiles,)
        #
        analyser.signalAnalysisStarted.connect(self.signalAnalysisStarted)             
        analyser.signalNextFileAnalysing.connect(self.signalNextFileAnalysing)
        analyser.signalAnalysisFinished.connect(self.signalAnalysisFinished)
        self.signalAnalyseFromFile.connect(analyser.analyseFromFiles)
        self.analysisProgressDialog.canceled.connect(analyser.abortAnalysis)
        #
        layout=QtGui.QGridLayout()
        #
        self.analyseFromFileButton = ActionButton(self.actionAnalyseFromFiles)
        layout.addWidget(self.analyseFromFileButton,0,0)
        self.errorTresholdSlider = QtGui.QDoubleSpinBox()
        errorTresholdLabel = QtGui.QLabel('Error Threshold (mm/s):')
        errorTresholdLabel.setBuddy(self.errorTresholdSlider)
        self.errorTresholdSlider.setMaximum(100)
        self.errorTresholdSlider.setValue(analyser.errorSpeedThreshold)
        self.errorTresholdSlider.valueChanged.connect(analyser.setErrorThreshold)
        self.errorTresholdSlider.valueChanged.connect(self.errorTresholdChanged)
        layout.addWidget(errorTresholdLabel,1,0)
        layout.addWidget(self.errorTresholdSlider,1,1)
        
        self.speedThresholdSlider = QtGui.QDoubleSpinBox()
        speedThresholdLabel = QtGui.QLabel('Speed Threshold (mm/s):')
        speedThresholdLabel.setBuddy(self.speedThresholdSlider)
        self.speedThresholdSlider.setMaximum(50)
        self.speedThresholdSlider.setValue(analyser.speedThreshold)
        self.speedThresholdSlider.valueChanged.connect(analyser.setSpeedThreshold)
        layout.addWidget(speedThresholdLabel,2,0)
        layout.addWidget(self.speedThresholdSlider,2,1)
        
        self.intervalDurationSlider = QtGui.QSpinBox()
        intervalDurationLabel = QtGui.QLabel('Interval Duration (s):')
        intervalDurationLabel.setBuddy(self.intervalDurationSlider)
        self.intervalDurationSlider.setMaximum(1000)
        self.intervalDurationSlider.setMinimum(50)
        self.intervalDurationSlider.setValue(analyser.intervalDuration)
        self.intervalDurationSlider.valueChanged.connect(analyser.setIntervalDuration)
        layout.addWidget(intervalDurationLabel,3,0)
        layout.addWidget(self.intervalDurationSlider,3,1)
        self.setLayout(layout)
        
    def errorTresholdChanged(self, value):
        if self.speedThresholdSlider.value() > value :
            self.speedThresholdSlider.setValue(value)
        
    def createTrajectoryImages(self):
        self.signalCreateTrajectoryImages.emit()
           
    def signalAnalysisStarted(self, count):
        self.analysisProgressDialog.setMaximum(count)
        self.analysisProgressDialog.show()
    
    def signalNextFileAnalysing(self, name, progress):
        self.analysisProgressDialog.setLabelText(name)
        self.analysisProgressDialog.setValue(progress)
    
    def signalAnalysisFinished(self):
        self.analysisProgressDialog.close()
    
    def analyseFromFile(self):
        '''
        '''
        analyseDialog = AnalyseDialog(self)
        if analyseDialog.exec_() :
            
            self.signalAnalyseFromFile.emit(analyseDialog.analyseFileName, analyseDialog.ltFilesList)
        
    