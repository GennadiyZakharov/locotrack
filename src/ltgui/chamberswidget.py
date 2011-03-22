'''
Created on 18.12.2010

@author: gena
'''

from PyQt4 import QtCore,QtGui
#from ltcore.actions import LtActions
from ltcore.signals import *

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
        
        chambersLabel = QtGui.QLabel('Chambers')
        self.chambersList = QtGui.QListWidget()
        chambersLabel.setBuddy(self.chambersList)
        layout.addWidget(chambersLabel,0,0,1,2)
        layout.addWidget(self.chambersList,1,0,1,2)
        
        negativeLabel = QtGui.QLabel("Negative")
        self.negativeChechBox = QtGui.QCheckBox()
        negativeLabel.setBuddy(self.negativeChechBox)
        layout.addWidget(negativeLabel,2,0)
        layout.addWidget(self.negativeChechBox,2,1)
        
        self.scaleButt = QtGui.QPushButton('Set Scale')
        self.scaleButt.setCheckable(True)
        layout.addWidget(self.scaleButt)      
        self.connect(self.scaleButt, signalToggled,self.on_ScaleOrChamberSet)
        
        self.chamberButt = QtGui.QPushButton('Set Chamber')
        self.chamberButt.setCheckable(True)
        layout.addWidget(self.chamberButt)
        self.connect(self.chamberButt, signalToggled,self.on_ScaleOrChamberSet)
          
        self.setLayout(layout)
        
    def on_RegionSelected(self,rect):
        if self.scaleButt.isChecked() :
            self.scaleButt.setChecked(False)
            print 'scale',rect
        elif self.chamberButt.isChecked() :
            self.chamberButt.setChecked(False)
            print 'chamber',rect
    '''        
    def on_cvDragging(self,rect):
        print 'dragging',rect
        self.emit(,rect)
    '''
    def on_ScaleOrChamberSet(self,checked):
        self.emit(signalEnableDnD,checked)
        
    def on_chamberListUpdated(self):
        pass
        
        