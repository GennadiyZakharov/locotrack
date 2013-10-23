'''
Created on 09.10.2013

@author: gena
'''
from __future__ import division

from PyQt4 import QtCore, QtGui
from ltcore.consts import presets

class PresetsWidget(QtGui.QDialog):
    '''
    
        
    '''

    signalSetPreset = QtCore.pyqtSignal(int)
    
    def __init__(self, analyser, parent=None):
        '''
        Constructor
        '''
        super(PresetsWidget, self).__init__(parent)
        
        layout = QtGui.QVBoxLayout()
        presetsLabel = QtGui.QLabel('Set default Parameters for:')
        layout.addWidget(presetsLabel)
        presetsComboBox = QtGui.QComboBox() 
        presetsLabel.setBuddy(presetsComboBox)
        layout.addWidget(presetsComboBox)
        presetsComboBox.addItems(presets)
        presetsComboBox.currentIndexChanged.connect(self.setPreset)
        # Ok/Close buttonbox
        self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Close,
                                           rejected=self.reject)
        
        self.setLayout(layout)
        
    def setPreset(self, index):
        self.signalSetPreset.emit(index)