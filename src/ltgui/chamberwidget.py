'''
Created on 12.08.2012

@author: gena
'''
from __future__ import division

from PyQt4 import QtGui

class ChamberWidget(QtGui.QWidget):
    '''
    classdocs
    '''

    def __init__(self, chamber, parent=None):
        '''
        Constructor
        '''
        super(ChamberWidget, self).__init__(parent)
        self.chamber = chamber
        layout = QtGui.QHBoxLayout()
        self.sampleNameEdit = QtGui.QLineEdit()
        self.sampleNameEdit.textChanged.connect(self.chamber.setSampleName)
        layout.addWidget(self.sampleNameEdit)
        thresholdLabel = QtGui.QLabel('Threshold')
        self.thresholdSlider = QtGui.QSpinBox()
        self.thresholdSlider.valueChanged.connect(self.chamber.setThreshold)
        thresholdLabel.setBuddy(self.thresholdSlider)
        layout.addWidget(thresholdLabel)
        layout.addWidget(self.thresholdSlider)
        self.showTrajectoryCheckBox = QtGui.QCheckBox()
        self.showTrajectoryCheckBox.setText('Show Trajectory')
        self.showTrajectoryCheckBox.setChecked(chamber.showTrajectory)
        self.showTrajectoryCheckBox.toggled.connect(self.chamber.setTrajectoryShow)
        layout.addWidget(self.showTrajectoryCheckBox)
        self.setLayout(layout)
        chamber.signalGuiDataUpdated.connect(self.update)
        self.update()
        
    def update(self):
        self.sampleNameEdit.setText(self.chamber.sampleName)
        self.thresholdSlider.setValue(self.chamber.threshold)
        
        