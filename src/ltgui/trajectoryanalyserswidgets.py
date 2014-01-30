'''
Created on 10.10.2013

@author: gena
'''
from __future__ import division

from PyQt4 import QtCore, QtGui

class RunRestAnalyserWidget(QtGui.QWidget):
    '''
    classdocs
    '''


    def __init__(self, runRestAnalyser, parent=None):
        '''
        Constructor
        '''
        super(RunRestAnalyserWidget, self).__init__(parent)
        self.runRestAnalyser = runRestAnalyser
        
        layout=QtGui.QGridLayout()
        self.speedThresholdSpinBox = QtGui.QDoubleSpinBox()
        speedThresholdLabel = QtGui.QLabel('Run Speed threshold:')
        speedThresholdLabel.setBuddy(self.speedThresholdSpinBox)
        self.speedThresholdSpinBox.setMaximum(200)
        self.speedThresholdSpinBox.setSuffix(' mm/s')
        self.speedThresholdSpinBox.setValue(runRestAnalyser.runRestSpeedThreshold)
        self.speedThresholdSpinBox.valueChanged.connect(runRestAnalyser.setRunRestSpeedThreshold)
        layout.addWidget(speedThresholdLabel,0,0)
        layout.addWidget(self.speedThresholdSpinBox,0,1)
        #
        self.intervalDurationSpinBox = QtGui.QSpinBox()
        intervalDurationLabel = QtGui.QLabel('Interval Duration:')
        intervalDurationLabel.setBuddy(self.intervalDurationSpinBox)
        self.intervalDurationSpinBox.setRange(50, 1000)
        self.intervalDurationSpinBox.setSuffix(' s')
        self.intervalDurationSpinBox.setValue(runRestAnalyser.intervalDuration)
        self.intervalDurationSpinBox.valueChanged.connect(runRestAnalyser.setIntervalDuration)
        layout.addWidget(intervalDurationLabel)
        layout.addWidget(self.intervalDurationSpinBox)
        #
        self.quantDurationSpinBox = QtGui.QDoubleSpinBox()
        quantDurationLabel = QtGui.QLabel('Quant Duration:')
        quantDurationLabel.setBuddy(self.intervalDurationSpinBox)
        self.quantDurationSpinBox.setRange(0,5)
        self.quantDurationSpinBox.setSuffix(' s')
        self.quantDurationSpinBox.setValue(runRestAnalyser.quantDuration)
        self.quantDurationSpinBox.valueChanged.connect(runRestAnalyser.setQuantDuration)
        layout.addWidget(quantDurationLabel)
        layout.addWidget(self.quantDurationSpinBox)
        
        self.setLayout(layout)
        
    def setPreset(self, index):
        if index == 1 :
            # Larva
            self.speedThresholdSpinBox.setValue(0.4)
        elif index == 0 :
            # Imago
            self.speedThresholdSpinBox.setValue(5.0)
        elif index == 2 :
            # Rat
            self.speedThresholdSpinBox.setValue(40.0)
    
    
class RatRunAnalyserWidget(QtGui.QWidget):
    '''
    classdocs
    '''
    def __init__(self, ratRunAnalyser, parent=None):
        '''
        Constructor
        '''
        super(RatRunAnalyserWidget, self).__init__(parent)    
        self.ratRunAnalyser = ratRunAnalyser
    
    def setPreset(self, index):
        pass