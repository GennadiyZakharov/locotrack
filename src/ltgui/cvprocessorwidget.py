'''
Created on 20.03.2011

@author: Gena
'''
from PyQt4 import QtCore, QtGui
#from ltcore.actions import LtActions
from ltcore.signals import *
from ltgui.labeledwidgets import *

class CvProcessorWidget(QtGui.QWidget):
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(CvProcessorWidget, self).__init__(parent)
        
        layout = QtGui.QGridLayout()
        
        accumulateLabel = QtGui.QLabel("&Frames number")
        self.accumulateSpinBox = QtGui.QSpinBox()
        self.accumulateSpinBox.setMaximum(200)
        self.accumulateSpinBox.setValue(100)
        accumulateLabel.setBuddy(self.accumulateSpinBox)
        self.accumulateButton = QtGui.QPushButton("Accumulate background")
        self.connect(self.accumulateButton, signalClicked, self.on_Accumulate)
        self.resetBackgroundButton = QtGui.QPushButton("Reset background")
        self.connect(self.resetBackgroundButton, signalClicked, self.on_resetBackground)
        
        layout.addWidget(accumulateLabel, 0, 0)        
        layout.addWidget(self.accumulateSpinBox, 0, 1)
        layout.addWidget(self.accumulateButton, 1, 0)        
        layout.addWidget(self.resetBackgroundButton, 1, 1)
        
        self.showProcessedChechBox = LabelledCheckBox("Show processed image")
        layout.addWidget(self.showProcessedChechBox, 2, 0)
        self.negativeChechBox = LabelledCheckBox("Negative")
        layout.addWidget(self.negativeChechBox, 2, 1)
        self.showContourChechBox = LabelledCheckBox("Show Contour")
        layout.addWidget(self.showContourChechBox, 3, 0)
        self.showContourChechBox.setCheckState(QtCore.Qt.Checked)
        
        
        self.tresholdSlider = LabelledSlider('Treshold')
        self.tresholdSlider.setMaximum(100)
        self.tresholdSlider.setValue(60)
        layout.addWidget(self.tresholdSlider, 4, 0, 1, 2)
        
        
        self.setLayout(layout)
        
    def on_Accumulate(self):
        self.emit(signalAccumulate, self.accumulateSpinBox.value())
        
    def on_resetBackground(self):
        self.emit(signalAccumulate, None)
        
