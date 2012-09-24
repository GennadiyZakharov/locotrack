'''
Created on 04.02.2012

@author: gena
'''
from __future__ import division

from PyQt4 import QtCore,QtGui
#from ltcore.actions import LtActions
from ltcore.signals import *
from ltgui.labeledwidgets import LabelledSlider,LabelledLineEdit

class TrajectoryWidget(QtGui.QWidget):
    '''
    This widget hols GUI elements for trajectory analysing
    '''
    signalCreateTrajectoryImages = QtCore.pyqtSignal()
    signalAnalyseFromFile = QtCore.pyqtSignal(QtCore.QString, object)

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(TrajectoryWidget, self).__init__(parent)
        #
        layout=QtGui.QVBoxLayout()
        #
        self.sampleEdit = LabelledLineEdit('Sample Name')
        layout.addWidget(self.sampleEdit)
        self.sampleEdit.lineEdit.textChanged.connect(self.descriptionChanged)
        #
        self.recordTrajectoryButton = QtGui.QPushButton('Record trajectory')
        self.recordTrajectoryButton.setCheckable(True)
        self.recordTrajectoryButton.setEnabled(False)
        self.recordTrajectoryButton.toggled.connect(self.setTrajectoryRecord)
        layout.addWidget(self.recordTrajectoryButton)
        #
        self.saveTrajectoryButton = QtGui.QPushButton('Save Trajectory')
        layout.addWidget(self.saveTrajectoryButton)
        #
        self.analyseTrajectoryButton = QtGui.QPushButton('Analyse trajectory')
        self.analyseTrajectoryButton.clicked.connect(self.analyseTrajectory)
        layout.addWidget(self.analyseTrajectoryButton)
        
        self.analyseFromFileButton = QtGui.QPushButton('Analyse from files')
        self.analyseFromFileButton.clicked.connect(self.analyseFromFile)
        layout.addWidget(self.analyseFromFileButton)
        
        self.createImageButton = QtGui.QPushButton('Create Trajectory Images')
        self.createImageButton.clicked.connect(self.createTrajectoryImages)
        layout.addWidget(self.createImageButton)
        #
        self.errorTresholdSlider = LabelledSlider('Error Treshold')
        self.errorTresholdSlider.setMaximum(100)
        self.errorTresholdSlider.setValue(50)
        self.errorTresholdSlider.valueChanged.connect(self.setErrorTheshold)
        layout.addWidget(self.errorTresholdSlider)
        
        self.speedTresholdSlider = LabelledSlider('Speed Treshold')
        self.speedTresholdSlider.setMaximum(100)
        self.speedTresholdSlider.setValue(28)
        self.speedTresholdSlider.valueChanged.connect(self.setSpeedTheshold)
        layout.addWidget(self.speedTresholdSlider)
        
        self.intervalDurationSlider = LabelledSlider('Interval Duration')
        self.intervalDurationSlider.setMaximum(500)
        self.intervalDurationSlider.setMinimum(50)
        self.intervalDurationSlider.setValue(300)
        self.intervalDurationSlider.valueChanged.connect(self.setIntervalDuration)
        layout.addWidget(self.intervalDurationSlider)
        self.setLayout(layout)
        
    def createTrajectoryImages(self):
        self.signalCreateTrajectoryImages.emit()
        
    def setTrajectoryRecord(self, checked):
        self.emit(signalWriteTrajectory, checked, self.sampleEdit.text())

    def setErrorTheshold(self, value):
        self.emit(signalErrorTheshold, value/100)
        
    def setSpeedTheshold(self, value):
        self.emit(signalSpeedTheshold, value/100)
    
    def setIntervalDuration(self, value):
        self.emit(signalIntervalDuration, value)
        
    def analyseTrajectory(self):
        '''
        '''
        # Creating formats list
        formats = ["*.%s" % unicode(videoFormat).lower() \
                   for videoFormat in ('txt', 'csv')]
        # Setting last user dir
        directory =  "."
        # Executing standard open dialog
        fname = unicode(QtGui.QFileDialog.getSaveFileName(self,
                        "Choose output file",
                        directory, "Data files (%s)" % " ".join(formats)))
        
        self.emit(signalAnalyseTrajectory, fname)
    
    def analyseFromFile(self):
        '''
        '''
        formats = ["*.%s" % unicode(videoFormat).lower() \
                   for videoFormat in ('txt', 'csv')]
        # Setting last user dir
        directory =  "."
        # Executing standard open dialog
        fname = unicode(QtGui.QFileDialog.getSaveFileName(self,
                        "Choose output file",
                        directory, "Data files (%s)" % " ".join(formats)))
        
        
    
    def trajectoryWriting(self, checked):
        self.recordTrajectoryButton.setChecked(checked)
    
    def descriptionChanged(self):
        #
        sampleName = str(self.sampleEdit.text())
        flag = (sampleName != '')
        self.recordTrajectoryButton.setEnabled(flag)
        if flag :
            self.emit(signalSampleNameChanged, sampleName)
        
    