'''
Created on 20.03.2011

@author: Gena
'''
from PyQt4 import QtCore, QtGui

class CvProcessorWidget(QtGui.QWidget):
    '''
    This widget is connected to cvProcessor and has GUI to
    manipulate processing properties
    '''
    def __init__(self, cvProcessor, parent=None):
        '''
        Constructor
        '''
        super(CvProcessorWidget, self).__init__(parent)
        self.cvProcessor = cvProcessor
        layout = QtGui.QGridLayout()
        # 
        showProcessedLabel = QtGui.QLabel("Show processed")
        self.showProcessedChechBox = QtGui.QCheckBox()
        self.showProcessedChechBox.setChecked(True)
        layout.addWidget(showProcessedLabel, 0, 0)
        layout.addWidget(self.showProcessedChechBox, 0, 1)
        #
        self.showContourChechBox = QtGui.QCheckBox()
        showContoursLabel = QtGui.QLabel("Show Contour")
        layout.addWidget(showContoursLabel)
        layout.addWidget(self.showContourChechBox)
        self.showContourChechBox.setCheckState(QtCore.Qt.Checked)
        self.ellipseCropCheckBox = QtGui.QCheckBox()
        cropLabel = QtGui.QLabel("Crop Central Ellipse")
        layout.addWidget(cropLabel)
        self.ellipseCropCheckBox.setCheckState(QtCore.Qt.Checked)
        layout.addWidget(self.ellipseCropCheckBox)
        #
        objectDetectorLabel = QtGui.QLabel('Detection method:')
        self.ObjectDetectorsComboBox = QtGui.QComboBox()
        objectDetectorLabel.setBuddy(self.ObjectDetectorsComboBox)
        self.ObjectDetectorsComboBox.addItems(
            [detector.name for detector in self.cvProcessor.objectDetectors])
        self.ObjectDetectorsComboBox.currentIndexChanged.connect(
            self.cvProcessor.setObjectDetector)
        self.ObjectDetectorsComboBox.currentIndexChanged.connect(
            self.enableThreshold)
        layout.addWidget(objectDetectorLabel)
        layout.addWidget(self.ObjectDetectorsComboBox)   
        # Threshold slider
        self.thresholdSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        thresholdLabel = QtGui.QLabel('Image threshold (%)')
        self.thresholdSlider.setMaximum(100)
        self.thresholdSlider.setValue(60)
        self.thresholdSlider.setEnabled(False)
        layout.addWidget(thresholdLabel)
        layout.addWidget(self.thresholdSlider)    
        # Layout
        self.setLayout(layout)
        
        
    def enableThreshold(self, index):
        self.thresholdSlider.setEnabled(index == 1)
        
    @QtCore.pyqtSlot(int)
    def setPreset(self, index):
        if index == 1 :
            # Larva
            self.ObjectDetectorsComboBox.setCurrentIndex(1)
        elif index == 0 :
            # Imago
            self.ObjectDetectorsComboBox.setCurrentIndex(0)
        elif index == 2 :
            # Rat
            self.ObjectDetectorsComboBox.setCurrentIndex(1)
        
