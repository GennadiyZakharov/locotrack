'''
Created on 10.10.2013

@author: gena
'''
from __future__ import division

from PyQt4 import QtCore, QtGui
from ltgui.actionbutton import ActionButton
from ltcore.ltactions import createAction

class ErrorDetectorWidget(QtGui.QWidget):
    '''
    classdocs
    '''

    def __init__(self, errorDetector, parent=None):
        '''
        Constructor
        '''
        super(ErrorDetectorWidget, self).__init__(parent)
        layout = QtGui.QGridLayout()
        
        self.errorTresholdSpinBox = QtGui.QDoubleSpinBox()
        errorTresholdLabel = QtGui.QLabel('Error threshold:')
        errorTresholdLabel.setBuddy(self.errorTresholdSpinBox)
        self.errorTresholdSpinBox.setMaximum(1000)
        self.errorTresholdSpinBox.setSuffix(' mm/s')
        self.errorTresholdSpinBox.setValue(errorDetector.errorSpeedThreshold)
        self.errorTresholdSpinBox.valueChanged.connect(errorDetector.setErrorSpeedThreshold)
        layout.addWidget(errorTresholdLabel,0,0)
        layout.addWidget(self.errorTresholdSpinBox,0,1)
        
        self.objectLengthTresholdSpinBox = QtGui.QDoubleSpinBox()
        objectLengthTresholdLabel = QtGui.QLabel('Object length threshold:')
        objectLengthTresholdLabel.setBuddy(self.errorTresholdSpinBox)
        self.objectLengthTresholdSpinBox.setSuffix(' mm')
        self.objectLengthTresholdSpinBox.setValue(errorDetector.objectLengthThreshold)
        self.objectLengthTresholdSpinBox.valueChanged.connect(errorDetector.setObjectLengthThreshold)
        layout.addWidget(objectLengthTresholdLabel)
        layout.addWidget(self.objectLengthTresholdSpinBox)
        #
        maxMissedIntervalCountLabel = QtGui.QLabel('Max missed count')
        maxMissedIntervalCountSpinBox = QtGui.QSpinBox()
        maxMissedIntervalCountLabel.setBuddy(maxMissedIntervalCountSpinBox)
        maxMissedIntervalCountSpinBox.setMaximum(50)
        maxMissedIntervalCountSpinBox.setValue(errorDetector.maxMissedIntervalCount)
        maxMissedIntervalCountSpinBox.valueChanged.connect(errorDetector.setMaxMissedIntervalCount)
        layout.addWidget(maxMissedIntervalCountLabel)
        layout.addWidget(maxMissedIntervalCountSpinBox)
        #
        maxMissedIntervalDurationLabel = QtGui.QLabel('Max missed duration ')
        maxMissedIntervalDurationSpinBox = QtGui.QDoubleSpinBox()
        maxMissedIntervalDurationSpinBox.setSuffix(' s')
        maxMissedIntervalDurationLabel.setBuddy(maxMissedIntervalDurationSpinBox)
        maxMissedIntervalDurationSpinBox.setMaximum(10.0)
        maxMissedIntervalDurationSpinBox.setValue(errorDetector.maxMissedIntervalDuration)
        maxMissedIntervalDurationSpinBox.valueChanged.connect(errorDetector.setMaxMissedIntervalDuration)
        layout.addWidget(maxMissedIntervalDurationLabel)
        layout.addWidget(maxMissedIntervalDurationSpinBox)
        self.setLayout(layout)
        #
    def setPreset(self, index):
        if index == 1 :
            # Larva
            self.errorTresholdSpinBox.setValue(4.0)
        elif index == 0 :
            # Imago
            self.errorTresholdSpinBox.setValue(50)
        elif index == 2 :
            # Rat
            self.errorTresholdSpinBox.setValue(500)