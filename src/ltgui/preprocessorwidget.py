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

        self.removeBarrelChechBox.stateChanged.connect(self.setRemoveBarrel)
        # 
        self.removeBarrelSpinbox = QtGui.QDoubleSpinBox()
        removeBarrelValLabel = QtGui.QLabel('Distortion coefficient')
        self.removeBarrelSpinbox.setRange(-10,10)

        self.removeBarrelSpinbox.setSingleStep(0.2)
        self.removeBarrelSpinbox.setSuffix('E-5')
        layout.addWidget(removeBarrelValLabel)
        layout.addWidget(self.removeBarrelSpinbox)
        self.removeBarrelSpinbox.valueChanged.connect(self.preprocessor.setRemoveBarrelCoef)

        self.removeBarrelFocal = QtGui.QDoubleSpinBox()
        removeBarrelFocalLabel = QtGui.QLabel('Focal length')
        self.removeBarrelFocal.setRange(2,50)
        self.removeBarrelFocal.setSingleStep(0.2)
        layout.addWidget(removeBarrelFocalLabel)
        layout.addWidget(self.removeBarrelFocal)  
        self.removeBarrelFocal.valueChanged.connect(self.preprocessor.setRemoveBarrelFocal)

        self.centerXSpinBox = QtGui.QSpinBox()
        centerXLabel = QtGui.QLabel('Camera position, X')
        self.centerXSpinBox.setMaximum(1280)
        self.centerXSpinBox.setSingleStep(10)
        layout.addWidget(centerXLabel)
        layout.addWidget(self.centerXSpinBox)
        self.centerXSpinBox.valueChanged.connect(self.preprocessor.setCenterX)

        self.centerYSpinBox = QtGui.QSpinBox()
        centerYLabel = QtGui.QLabel('Camera position, Y')
        self.centerYSpinBox.setMaximum(1024)
        self.centerYSpinBox.setSingleStep(10)
        layout.addWidget(centerYLabel)
        layout.addWidget(self.centerYSpinBox)
        self.centerYSpinBox.valueChanged.connect(self.preprocessor.setCenterY)

        accumulateBackgroundLabel = QtGui.QLabel('Background frames')
        layout.addWidget(accumulateBackgroundLabel)
        self.accumulateBackgroundSpinBox = QtGui.QSpinBox()
        self.accumulateBackgroundSpinBox.setMaximum(1000)
        self.accumulateBackgroundSpinBox.setMinimum(50)
        layout.addWidget(self.accumulateBackgroundSpinBox)
        self.accumulateBackgroundSpinBox.valueChanged.connect(self.preprocessor.setBackgroundFrames)

        self.accumulateBackgroundButton = QtGui.QPushButton('Accumulate background')
        layout.addWidget(self.accumulateBackgroundButton)
        self.accumulateBackgroundButton.clicked.connect(preprocessor.collectBackground)

        # Layout
        self.setLayout(layout)
        self.loadState()
        
    @QtCore.pyqtSlot(int)  
    def setInvertImage(self, state):
        self.preprocessor.setInvertImage(state == QtCore.Qt.Checked)    
        
        
    @QtCore.pyqtSlot(int)  
    def setRemoveBarrel(self, state):
        value = (state == QtCore.Qt.Checked)
        self.removeBarrelFocal.setEnabled(value)
        self.removeBarrelSpinbox.setEnabled(value)
        self.preprocessor.setRemoveBarrel(value)
        
    def loadState(self):
        self.negativeChechBox.setChecked(self.preprocessor.invertImage)
        self.removeBarrelChechBox.setChecked(self.preprocessor.removeBarrel)
        self.removeBarrelSpinbox.setValue(self.preprocessor.removeBarrelCoef)
        self.removeBarrelFocal.setValue(self.preprocessor.removeBarrelFocal)
        self.centerXSpinBox.setValue(self.preprocessor.centerX)
        self.centerYSpinBox.setValue(self.preprocessor.centerY)
        self.accumulateBackgroundSpinBox.setValue(self.preprocessor.nBackgroundFrames)



        