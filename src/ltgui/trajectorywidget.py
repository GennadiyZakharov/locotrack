'''
Created on 04.02.2012

@author: gena
'''
from __future__ import division

from PyQt4 import QtCore, QtGui
#from ltcore.actions import LtActions
from ltcore.signals import *
from ltgui.labeledwidgets import *

class TrajectoryWidget(QtGui.QWidget):
    '''
    This widget hols GUI elements for trajectory analysing
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(TrajectoryWidget, self).__init__(parent)
        #
        layout=QtGui.QVBoxLayout()
        #
        self.speciesEdit = LabelledLineEdit('Line')
        layout.addWidget(self.speciesEdit)
        self.speciesEdit.lineEdit.textChanged.connect(self.descriptionChanged)
        self.genderEdit = LabelledLineEdit('Gender')
        layout.addWidget(self.genderEdit)
        self.genderEdit.lineEdit.textChanged.connect(self.descriptionChanged)
        self.conditionEdit = LabelledLineEdit('Condition')
        layout.addWidget(self.conditionEdit)
        self.conditionEdit.lineEdit.textChanged.connect(self.descriptionChanged)
        #
        self.recordTrajectoryButton = QtGui.QPushButton('Record trajectory')
        self.recordTrajectoryButton.setCheckable(True)
        self.recordTrajectoryButton.setEnabled(False)
        self.connect(self.recordTrajectoryButton, signalToggled, self.setTrajectoryRecord)
        layout.addWidget(self.recordTrajectoryButton)
        #
        self.analyseTrajectoryButton = QtGui.QPushButton('Analyse trajectory')
        self.connect(self.analyseTrajectoryButton, signalClicked, self.analyseTrajectory)
        layout.addWidget(self.analyseTrajectoryButton)
        #
        self.errorTresholdSlider = LabelledSlider('Error Treshold')
        self.errorTresholdSlider.setMaximum(100)
        self.errorTresholdSlider.setValue(50)
        self.connect(self.errorTresholdSlider,signalValueChanged,self.setErrorTheshold)
        layout.addWidget(self.errorTresholdSlider)
        
        self.speedTresholdSlider = LabelledSlider('Speed Treshold')
        self.speedTresholdSlider.setMaximum(100)
        self.speedTresholdSlider.setValue(28)
        self.connect(self.speedTresholdSlider,signalValueChanged,self.setSpeedTheshold)
        layout.addWidget(self.speedTresholdSlider)
        
        self.intervalDurationSlider = LabelledSlider('Interval Duration')
        self.intervalDurationSlider.setMaximum(500)
        self.intervalDurationSlider.setMinimum(50)
        self.intervalDurationSlider.setValue(300)
        self.connect(self.intervalDurationSlider,signalValueChanged,self.setIntervalDuration)
        layout.addWidget(self.intervalDurationSlider)
        
        
        self.setLayout(layout)
        
        
    def setTrajectoryRecord(self, checked):
        self.emit(signalWriteTrajectory, checked,self.speciesEdit.text(),
                  self.genderEdit.text(), self.conditionEdit.text())

    def setErrorTheshold(self, value):
        self.emit(signalErrorTheshold, value/100)
        
    def setSpeedTheshold(self, value):
        self.emit(signalSpeedTheshold, value/100)
    
    def setIntervalDuration(self, value):
        self.emit(signalIntervalDuration, value)
        
    def analyseTrajectory(self):
        '''
        dir = os.path.dirname(self.cvProcessor.cvPlayer.fileName) \
            if self.cvProcessor.cvPlayer.fileName is not None else "."
         
        dialog = QtGui.QFileDialog(self,'',dir)  
        dialog.setFileMode(QtGui.QFileDialog.Di)
        '''
        # Creating formats list
        formats = ["*.%s" % unicode(format).lower() \
                   for format in ('avi', 'mpg', 'ogg')]
        # Executing standard open dialog
        fdir = unicode(QtGui.QFileDialog.getExistingDirectory(self,
                        "Open Directory"))
        
        self.emit(signalAnalyseTrajectory, fdir)
    
    
    def descriptionChanged(self):
        #
        species = str(self.speciesEdit.text())
        gender = str(self.genderEdit.text())
        condition = str(self.conditionEdit.text())
        flag = (species != '' and 
                gender != '' and
                condition != '')
        self.recordTrajectoryButton.setEnabled(flag)
        if flag :
            self.emit(signalSampleNameChanged, species, gender, condition)
        
    