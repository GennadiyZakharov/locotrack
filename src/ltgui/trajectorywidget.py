'''
Created on 04.02.2012

@author: gena
'''

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
        self.recordTrajectoryButton = QtGui.QPushButton('Record trajectory')
        self.recordTrajectoryButton.setCheckable(True)
        self.connect(self.recordTrajectoryButton, signalToggled, self.setTrajectoryRecord)
        layout.addWidget(self.recordTrajectoryButton)
        #
        self.analyseTrajectoryButton = QtGui.QPushButton('Analyse trajectory')
        self.connect(self.analyseTrajectoryButton, signalClicked, self.analyseTrajectory)
        layout.addWidget(self.analyseTrajectoryButton)
        #
        self.setLayout(layout)
        
        
    def setTrajectoryRecord(self, checked):
        self.emit(signalWriteTrajectory, checked)
        
    def analyseTrajectory(self):
        self.emit(signalAnalyseTrajectory)
        
    