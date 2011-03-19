'''
Created on 18.12.2010

@author: gena
'''

from PyQt4 import QtCore,QtGui
#from ltcore.actions import LtActions
#from ltcore.signals import *

class ChambersWidget(QtGui.QWidget):
    '''
    classdocs
    '''


    def __init__(self,parent=None):
        '''
        Constructor
        '''
        super(ChambersWidget, self).__init__(parent)
        layout=QtGui.QGridLayout()
        
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
        
    def on_RegionSelected(self,rect):
        print 'Region',rect
        