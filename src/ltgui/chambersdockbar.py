'''
Created on 18.12.2010

@author: gena
'''

from PyQt4 import QtCore,QtGui
#from ltcore.actions import LtActions
#from ltcore.signals import *

class ChambersDockBar(QtGui.QWidget):
    '''
    classdocs
    '''


    def __init__(self,parent=None):
        '''
        Constructor
        '''
        super(ChambersDockBar, self).__init__(parent)
        layout=QtGui.QGridLayout()
        
        brightnessLabel = QtGui.QLabel("&Brightness")
        self.brighnessSlider=QtGui.QSlider(QtCore.Qt.Horizontal)
        brightnessLabel.setBuddy(self.brighnessSlider)
        layout.addWidget(brightnessLabel,0,0)
        layout.addWidget(self.brighnessSlider,0,1,1,2)
        
        contrastLabel = QtGui.QLabel("&Contrast")
        self.contrastSlider=QtGui.QSlider(QtCore.Qt.Horizontal)
        contrastLabel.setBuddy(self.contrastSlider)
        layout.addWidget(contrastLabel,1,0)
        layout.addWidget(self.contrastSlider,1,1,1,2)
        
        negativeLabel = QtGui.QLabel("Negative")
        self.negativeChechBox = QtGui.QCheckBox()
        negativeLabel.setBuddy(self.negativeChechBox)
        layout.addWidget(negativeLabel,2,0)
        layout.addWidget(self.negativeChechBox,2,1)
        
        accumulateLabel = QtGui.QLabel("&Frames number")
        self.accumulateSpinBox = QtGui.QSpinBox()
        self.accumulateSpinBox.setMaximum(200)
        self.accumulateSpinBox.setValue(100)
        accumulateLabel.setBuddy(self.accumulateSpinBox)
        self.accumulateButt=QtGui.QPushButton("Accumulate")
        layout.addWidget(accumulateLabel,3,0)
        layout.addWidget(self.accumulateSpinBox,3,1)
        layout.addWidget(self.accumulateButt,3,2)
        
        
        self.setLayout(layout)
        
        