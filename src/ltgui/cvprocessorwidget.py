'''
Created on 20.03.2011

@author: Gena
'''
from PyQt4 import QtCore,QtGui
#from ltcore.actions import LtActions
from ltcore.signals import *
from ltgui.labeledwidgets import *

class CvProcessorWidget(QtGui.QWidget):
    '''
    classdocs
    '''


    def __init__(self,parent=None):
        '''
        Constructor
        '''
        super(CvProcessorWidget, self).__init__(parent)
        
        layout = QtGui.QVBoxLayout()
        
        self.tresholdSlider = LabelledSlider('Treshold')
        self.tresholdSlider.setMaximum(100)
        layout.addWidget(self.tresholdSlider)
        
        accumulateLabel = QtGui.QLabel("&Frames number")
        self.accumulateSpinBox = QtGui.QSpinBox()
        self.accumulateSpinBox.setMaximum(200)
        self.accumulateSpinBox.setValue(100)
        accumulateLabel.setBuddy(self.accumulateSpinBox)
        self.accumulateButton=QtGui.QPushButton("Accumulate")
        self.connect(self.accumulateButton,signalClicked,self.on_Accumulate)
        
        layout2 = QtGui.QHBoxLayout()
        layout2.addWidget(accumulateLabel)
        layout2.addWidget(self.accumulateSpinBox)
        layout2.addWidget(self.accumulateButton)
        layout.addLayout(layout2)
        
        self.setLayout(layout)
        
    def on_Accumulate(self):
        self.emit(signalAccumulate,self.accumulateSpinBox.value())
        