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
from ltgui.trajectoryanalyserswidgets import RunRestAnalyserWidget,RatRunAnalyserWidget
from ltgui.errordetectorwidget import ErrorDetectorWidget

class TrajectoryWidget(QtGui.QWidget):
    '''
    This widget holds GUI elements for trajectory analysing
    '''
    signalAnalyseFromFile = QtCore.pyqtSignal(QtCore.QString, QtCore.QStringList)

    def __init__(self, trajectoryAnalysis, parent=None):
        '''
        Constructor
        '''
        super(TrajectoryWidget, self).__init__(parent)
        self.trajectoryAnalysis = trajectoryAnalysis
        self.trajectoryAnalyserWidgets=[RunRestAnalyserWidget(self.trajectoryAnalysis.analysers[0]),
                                        RatRunAnalyserWidget(self.trajectoryAnalysis.analysers[1])]
        self.trajectoryAnalyserCaptions=['RunRest',
                                          'RatRun']
        self.errorDetectorWidget = ErrorDetectorWidget(self.trajectoryAnalysis.errorDetector)
        
        self.analyseDialog = AnalyseDialog(self)
        self.analysisProgressDialog = QtGui.QProgressDialog()
        self.analysisProgressDialog.setWindowTitle('Analysing files')
        #
                #
        self.trajectoryAnalysis.signalAnalysisStarted.connect(self.signalAnalysisStarted)             
        self.trajectoryAnalysis.signalNextFileAnalysing.connect(self.signalNextFileAnalysing)
        self.trajectoryAnalysis.signalAnalysisFinished.connect(self.signalAnalysisFinished) 
        #
        layout = QtGui.QGridLayout()
        #
        
        #self.analyseFromFileButton = ActionButton(self.actionAnalyseFromFiles)
        #layout.addWidget(self.analyseFromFileButton, 0, 0, 1, 2)
        #
        defaultSettingsLabel = QtGui.QLabel('Default set for:')
        layout.addWidget(defaultSettingsLabel, 1, 0)
        self.defaultSettigsComboBox = QtGui.QComboBox() 
        defaultSettingsLabel.setBuddy(self.defaultSettigsComboBox)
        layout.addWidget(self.defaultSettigsComboBox, 1, 1)
        self.defaultSettigsComboBox.addItems(['Imago', 'Larva', 'Rat'])
        self.defaultSettigsComboBox.currentIndexChanged.connect(self.setPreset)
        #
        createImageLabel = QtGui.QLabel('Image creation method')
        layout.addWidget(createImageLabel,2,0)
        self.createImageComboBox = QtGui.QComboBox()
        createImageLabel.setBuddy(self.createImageComboBox)
        self.createImageComboBox.addItems(self.trajectoryAnalysis.imageCreatorsCaptions)
        self.createImageComboBox.setCurrentIndex(1)
        self.createImageComboBox.currentIndexChanged.connect(self.trajectoryAnalysis.setImageCreator)
        self.createImageComboBox.currentIndexChanged.connect(self.setLevelsEnabled)
        layout.addWidget(self.createImageComboBox,2,1)
        #
        imageLevelsLabel = QtGui.QLabel('Accumulate levels')
        layout.addWidget(imageLevelsLabel,3,0)
        self.imageLevelsSpinBox = QtGui.QSpinBox()
        createImageLabel.setBuddy(self.imageLevelsSpinBox)
        self.imageLevelsSpinBox.setMaximum(10)
        self.imageLevelsSpinBox.setValue(self.trajectoryAnalysis.imageLevels)
        self.imageLevelsSpinBox.valueChanged.connect(self.trajectoryAnalysis.setImageLevelsCount)
        layout.addWidget(self.imageLevelsSpinBox,3,1)
        #
        writeSpeedLabel = QtGui.QLabel('Write speed info')
        layout.addWidget(writeSpeedLabel,4,0)
        writeSpeedCheckBox = QtGui.QCheckBox()
        writeSpeedLabel.setBuddy(writeSpeedCheckBox)
        layout.addWidget(writeSpeedCheckBox,4,1)
        writeSpeedCheckBox.stateChanged.connect(self.trajectoryAnalysis.setWriteSpeed)
        #
        layout.addWidget(self.errorDetectorWidget,5,0,1,2)
        
        self.tabWidget=QtGui.QTabWidget()
        for i in range(2) :
            self.tabWidget.addTab(self.trajectoryAnalyserWidgets[i], self.trajectoryAnalyserCaptions[i])
        self.tabWidget.currentChanged.connect(self.trajectoryAnalysis.setAnalyser)
        layout.addWidget(self.tabWidget,6,0,1,2)
        
        self.setLayout(layout)
        self.defaultSettigsComboBox.setCurrentIndex(0)
    
    @QtCore.pyqtSlot(int)
    def setLevelsEnabled(self, index):
        self.imageLevelsSpinBox.setEnabled(index == 1)
        
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
        self.analyseDialog.clearData()
        if self.analyseDialog.exec_() :
            self.trajectoryAnalysis.analyseFromFiles(self.analyseDialog.analyseFileName, self.analyseDialog.ltFilesList)
    
    def abortAnalysis(self):
        self.trajectoryAnalysis.abortAnalysis()
        
    @QtCore.pyqtSlot(int)
    def setPreset(self, index):
        self.defaultSettigsComboBox.setCurrentIndex(index)
        self.errorDetectorWidget.setPreset(index)       
        if index == 1 :
            # Larva
            self.createImageComboBox.setCurrentIndex(0)
            self.tabWidget.setCurrentIndex(0)
        elif index == 0 :
            # Imago
            self.createImageComboBox.setCurrentIndex(1)
            self.tabWidget.setCurrentIndex(0)
        elif index == 2 :
            # Rat
            self.createImageComboBox.setCurrentIndex(0)
            self.tabWidget.setCurrentIndex(0)

        self.tabWidget.currentWidget().setPreset(index)
    
        
