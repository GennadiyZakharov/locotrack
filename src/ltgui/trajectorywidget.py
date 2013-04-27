'''
Created on 04.02.2012

@author: gena
'''
from __future__ import division

from PyQt4 import QtCore, QtGui
#from ltcore.actions import LtActions
from ltgui.analysedialog import AnalyseDialog
from ltgui.actionbutton import ActionButton
from ltcore.ltactions import createAction

class TrajectoryWidget(QtGui.QWidget):
    '''
    This widget holds GUI elements for trajectory analysing
    '''
    signalAnalyseFromFile = QtCore.pyqtSignal(QtCore.QString, QtCore.QStringList)

    def __init__(self, analyser, parent=None):
        '''
        Constructor
        '''
        super(TrajectoryWidget, self).__init__(parent)
        self.analysisProgressDialog = QtGui.QProgressDialog()
        self.analysisProgressDialog.setWindowTitle('Analysing files')
        #
        
        self.actionAnalyseFromFiles = createAction(self, "&Analyse from files...", "",
                                       "document-open", "Open video file")
        self.actionAnalyseFromFiles.triggered.connect(self.analyseFromFile)
        self.actions = (self.actionAnalyseFromFiles,)
        #
        analyser.signalAnalysisStarted.connect(self.signalAnalysisStarted)             
        analyser.signalNextFileAnalysing.connect(self.signalNextFileAnalysing)
        analyser.signalAnalysisFinished.connect(self.signalAnalysisFinished)
        self.signalAnalyseFromFile.connect(analyser.analyseFromFiles)
        self.analysisProgressDialog.canceled.connect(analyser.abortAnalysis)
        #
        layout = QtGui.QGridLayout()
        #
        
        self.analyseFromFileButton = ActionButton(self.actionAnalyseFromFiles)
        layout.addWidget(self.analyseFromFileButton, 0, 0, 1, 2)
        #
        defaultSettingsLabel = QtGui.QLabel('Default set for:')
        layout.addWidget(defaultSettingsLabel, 1, 0)
        defaultSettigsComboBox = QtGui.QComboBox() 
        defaultSettingsLabel.setBuddy(defaultSettigsComboBox)
        layout.addWidget(defaultSettigsComboBox, 1, 1)
        defaultSettigsComboBox.addItems(['Larva', 'Imago'])
        defaultSettigsComboBox.currentIndexChanged.connect(self.setDefaultSettings)
        #
        self.errorTresholdSpinBox = QtGui.QDoubleSpinBox()
        errorTresholdLabel = QtGui.QLabel('Error threshold:')
        errorTresholdLabel.setBuddy(self.errorTresholdSpinBox)
        self.errorTresholdSpinBox.setMaximum(100)
        self.errorTresholdSpinBox.setSuffix(' mm/s')
        self.errorTresholdSpinBox.setValue(analyser.errorSpeedThreshold)
        self.errorTresholdSpinBox.valueChanged.connect(analyser.setErrorSpeedThreshold)
        self.errorTresholdSpinBox.valueChanged.connect(self.errorTresholdChanged)
        layout.addWidget(errorTresholdLabel)
        layout.addWidget(self.errorTresholdSpinBox)
        #
        maxMissedIntervalCountLabel = QtGui.QLabel('Max missed count')
        maxMissedIntervalCountSpinBox = QtGui.QSpinBox()
        maxMissedIntervalCountLabel.setBuddy(maxMissedIntervalCountSpinBox)
        maxMissedIntervalCountSpinBox.setMaximum(10)
        maxMissedIntervalCountSpinBox.setValue(analyser.maxMissedIntervalCount)
        maxMissedIntervalCountSpinBox.valueChanged.connect(analyser.setMaxMissedIntervalCount)
        layout.addWidget(maxMissedIntervalCountLabel)
        layout.addWidget(maxMissedIntervalCountSpinBox)
        #
        maxMissedIntervalDurationLabel = QtGui.QLabel('Max missed duration ')
        maxMissedIntervalDurationSpinBox = QtGui.QDoubleSpinBox()
        maxMissedIntervalDurationSpinBox.setSuffix(' s')
        maxMissedIntervalDurationLabel.setBuddy(maxMissedIntervalDurationSpinBox)
        maxMissedIntervalDurationSpinBox.setMaximum(10.0)
        maxMissedIntervalDurationSpinBox.setValue(analyser.maxMissedIntervalDuration)
        maxMissedIntervalDurationSpinBox.valueChanged.connect(analyser.setMaxMissedIntervalDuration)
        layout.addWidget(maxMissedIntervalDurationLabel)
        layout.addWidget(maxMissedIntervalDurationSpinBox)
        #
        self.speedThresholdSpinBox = QtGui.QDoubleSpinBox()
        speedThresholdLabel = QtGui.QLabel('Run threshold:')
        speedThresholdLabel.setBuddy(self.speedThresholdSpinBox)
        self.speedThresholdSpinBox.setMaximum(50)
        self.speedThresholdSpinBox.setSuffix(' mm/s')
        self.speedThresholdSpinBox.setValue(analyser.runRestSpeedThreshold)
        self.speedThresholdSpinBox.valueChanged.connect(analyser.setRunRestSpeedThreshold)
        layout.addWidget(speedThresholdLabel)
        layout.addWidget(self.speedThresholdSpinBox)
        #
        self.intervalDurationSpinBox = QtGui.QSpinBox()
        intervalDurationLabel = QtGui.QLabel('Interval Duration:')
        intervalDurationLabel.setBuddy(self.intervalDurationSpinBox)
        self.intervalDurationSpinBox.setRange(50, 1000)
        self.intervalDurationSpinBox.setSuffix(' s')
        self.intervalDurationSpinBox.setValue(analyser.intervalDuration)
        self.intervalDurationSpinBox.valueChanged.connect(analyser.setIntervalDuration)
        layout.addWidget(intervalDurationLabel)
        layout.addWidget(self.intervalDurationSpinBox)
        #
        self.quantDurationSpinBox = QtGui.QDoubleSpinBox()
        quantDurationLabel = QtGui.QLabel('Quant Duration:')
        quantDurationLabel.setBuddy(self.intervalDurationSpinBox)
        self.quantDurationSpinBox.setRange(0,5)
        self.quantDurationSpinBox.setSuffix(' s')
        self.quantDurationSpinBox.setValue(analyser.quantDuration)
        self.quantDurationSpinBox.valueChanged.connect(analyser.setQuantDuration)
        layout.addWidget(quantDurationLabel)
        layout.addWidget(self.quantDurationSpinBox)
        #
        createImageLabel = QtGui.QLabel('Image creation method')
        layout.addWidget(createImageLabel)
        self.createImageComboBox = QtGui.QComboBox()
        createImageLabel.setBuddy(self.createImageComboBox)
        self.createImageComboBox.addItems(analyser.imageCreatorsCaptions)
        self.createImageComboBox.setCurrentIndex(1)
        self.createImageComboBox.currentIndexChanged.connect(analyser.setImageCreator)
        self.createImageComboBox.currentIndexChanged.connect(self.setLevelsEnabled)
        layout.addWidget(self.createImageComboBox)
        #
        imageLevelsLabel = QtGui.QLabel('Accumulate levels')
        layout.addWidget(imageLevelsLabel)
        self.imageLevelsSpinBox = QtGui.QSpinBox()
        createImageLabel.setBuddy(self.imageLevelsSpinBox)
        self.imageLevelsSpinBox.setMaximum(10)
        self.imageLevelsSpinBox.setValue(analyser.imageLevels)
        self.imageLevelsSpinBox.valueChanged.connect(analyser.setImageLevelsCount)
        layout.addWidget(self.imageLevelsSpinBox)
        #
        writeSpeedLabel = QtGui.QLabel('Write speed info')
        layout.addWidget(writeSpeedLabel)
        writeSpeedCheckBox = QtGui.QCheckBox()
        writeSpeedLabel.setBuddy(writeSpeedCheckBox)
        layout.addWidget(writeSpeedCheckBox)
        writeSpeedCheckBox.stateChanged.connect(analyser.setWriteSpeed)
        #
        self.setLayout(layout)
        defaultSettigsComboBox.setCurrentIndex(1)
    
    @QtCore.pyqtSlot(int)
    def setDefaultSettings(self, index):
        if index == 0 :
            # Larva
            self.errorTresholdSpinBox.setValue(4.0)
            self.speedThresholdSpinBox.setValue(0.4)
            self.createImageComboBox.setCurrentIndex(0)
        elif index == 1 :
            # Imago
            self.errorTresholdSpinBox.setValue(50)
            self.speedThresholdSpinBox.setValue(5)
            self.createImageComboBox.setCurrentIndex(1)
    
    @QtCore.pyqtSlot(int)
    def setLevelsEnabled(self, index):
        self.imageLevelsSpinBox.setEnabled(index == 1)
    
    @QtCore.pyqtSlot(float)
    def errorTresholdChanged(self, value):
        if self.speedThresholdSpinBox.value() > value :
            self.speedThresholdSpinBox.setValue(value)
    
    @QtCore.pyqtSlot(int)
    def signalAnalysisStarted(self, count):
        self.analysisProgressDialog.setMaximum(count)
        self.analysisProgressDialog.show()
    
    @QtCore.pyqtSlot(QtCore.QString, int)
    def signalNextFileAnalysing(self, name, progress):
        self.analysisProgressDialog.setLabelText(name)
        self.analysisProgressDialog.setValue(progress)
    
    @QtCore.pyqtSlot(int)
    def signalAnalysisFinished(self):
        self.analysisProgressDialog.close()
    
    @QtCore.pyqtSlot()
    def analyseFromFile(self):
        '''
        '''
        analyseDialog = AnalyseDialog(self)
        if analyseDialog.exec_() :
            self.signalAnalyseFromFile.emit(analyseDialog.analyseFileName, analyseDialog.ltFilesList)
        
    
