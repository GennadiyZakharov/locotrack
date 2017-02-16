'''
Created on 29 jan. 2015

@author: Gena
'''
from PyQt4 import QtCore, QtGui


class PreprocessorWidget(QtGui.QWidget):
    '''
    classdocs
    '''


    def __init__(self, preprocessor, parent=None):
        '''
        Constructor
        '''
        super(PreprocessorWidget, self).__init__(parent)
        self.preprocessor = preprocessor
        layout = QtGui.QGridLayout()
        # 
        
        #
        self.negativeChechBox = QtGui.QCheckBox()
        negativeLabel = QtGui.QLabel("Negative image")
        layout.addWidget(negativeLabel,0,0)
        layout.addWidget(self.negativeChechBox,0,1)
        self.negativeChechBox.stateChanged.connect(self.setInvertImage)
        
        #
        self.removeBarrelChechBox = QtGui.QCheckBox()
        removeBarrelLabel = QtGui.QLabel("Remove barrel distortion")
        layout.addWidget(removeBarrelLabel)
        layout.addWidget(self.removeBarrelChechBox)
        self.removeBarrelChechBox.setCheckState(QtCore.Qt.Checked)
        self.removeBarrelChechBox.stateChanged.connect(self.setRemoveBarrel)
        # 
        self.removeBarrelSpinbox = QtGui.QDoubleSpinBox()
        removeBarrelValLabel = QtGui.QLabel('Distortion coefficient')
        self.removeBarrelSpinbox.setMaximum(10)
        self.removeBarrelSpinbox.setValue(1)


        layout.addWidget(removeBarrelValLabel)
        layout.addWidget(self.removeBarrelSpinbox)
        self.removeBarrelSpinbox.valueChanged.connect(self.setRemoveBarrelValue)    
        
        self.removeBarrelFocal = QtGui.QSpinBox()
        removeBarrelFocalLabel = QtGui.QLabel('Focal length')
        self.removeBarrelFocal.setMaximum(50)
        self.removeBarrelFocal.setMinimum(2)
        self.removeBarrelFocal.setValue(10)

        layout.addWidget(removeBarrelFocalLabel)
        layout.addWidget(self.removeBarrelFocal)  
        self.removeBarrelFocal.valueChanged.connect(self.preprocessor.setRemoveBarrelFocal)

        accumulateBackgroundLabel = QtGui.QLabel('Background frames')
        layout.addWidget(accumulateBackgroundLabel)

        accumulateBackgroundSpinBox = QtGui.QSpinBox()
        accumulateBackgroundSpinBox.setMaximum(1000)
        accumulateBackgroundSpinBox.setMinimum(50)
        accumulateBackgroundSpinBox.setValue(self.preprocessor.nBackgroundFrames)
        layout.addWidget(accumulateBackgroundSpinBox)
        accumulateBackgroundSpinBox.valueChanged.connect(self.preprocessor.setBackgroundFrames)

        self.accumulateBackgroundButton = QtGui.QPushButton('Accumulate background')
        layout.addWidget(self.accumulateBackgroundButton)
        self.accumulateBackgroundButton.clicked.connect(preprocessor.collectBackground)

        # Layout
        self.setLayout(layout)
        
    @QtCore.pyqtSlot(int)  
    def setInvertImage(self, state):
        self.preprocessor.setInvertImage(state == QtCore.Qt.Checked)    
        
        
    @QtCore.pyqtSlot(int)  
    def setRemoveBarrel(self, state):
        value = (state == QtCore.Qt.Checked)
        self.removeBarrelFocal.setEnabled(value)
        self.removeBarrelSpinbox.setEnabled(value)
        self.preprocessor.setRemoveBarrel(value)    
        
    @QtCore.pyqtSlot(int)
    def setRemoveBarrelValue(self, value):
        self.preprocessor.setRemoveBarrelCoef(-value*1e-5)
        
        

        