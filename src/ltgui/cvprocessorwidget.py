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
    This widget is connected to cvProcessor and has GUI to
    manipulate processing properties
    '''
    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(CvProcessorWidget, self).__init__(parent)
        
        layout = QtGui.QGridLayout()
        # Some checkboxes
        self.showProcessedChechBox = LabelledCheckBox("Show processed image")
        layout.addWidget(self.showProcessedChechBox, 2, 0)
        self.negativeChechBox = LabelledCheckBox("Negative")
        layout.addWidget(self.negativeChechBox, 2, 1)
        self.showContourChechBox = LabelledCheckBox("Show Contour")
        layout.addWidget(self.showContourChechBox, 3, 0)
        self.showContourChechBox.setCheckState(QtCore.Qt.Checked)
        self.ellipseCropCheckBox = LabelledCheckBox("Crop Central Ellipse")
        self.ellipseCropCheckBox.setCheckState(QtCore.Qt.Checked)
        layout.addWidget(self.ellipseCropCheckBox, 3, 1)
        # Treshold slider
        self.tresholdSlider = LabelledSlider('Treshold')
        self.tresholdSlider.setMaximum(100)
        self.tresholdSlider.setValue(60)
        layout.addWidget(self.tresholdSlider, 4, 0, 1, 2)
        self.detectionMethodComboBox = QtGui.QComboBox()
        
        # Layout
        self.setLayout(layout)
        
    def accumulate(self):
        self.emit(signalAccumulate, self.accumulateSpinBox.value())
        
    def resetBackground(self):
        '''
        Clear accumulated background
        '''
        self.emit(signalAccumulate, None)
        
