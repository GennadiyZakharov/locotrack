'''
Created on 19.03.2011

@author: Gena
'''

from __future__ import division
from __future__ import unicode_literals
from future_builtins import *

from PyQt4.QtCore import QString,Qt
from PyQt4.QtGui import (QBoxLayout,
        QLabel, QLineEdit, QTextEdit, QSlider,
        QWidget,QCheckBox)

LEFT, ABOVE = range(2)

class LabelledLineEdit(QWidget):
    '''
    This class holds QLineEdit, budded to QLabel
    This is used only to simplify GUI creation 
    '''
    def __init__(self, labelText=QString(), leftTopPos=LEFT,parent=None):
        super(LabelledLineEdit, self).__init__(parent)
        self.label = QLabel(labelText)
        self.lineEdit = QLineEdit()
        self.label.setBuddy(self.lineEdit)
        layout = QBoxLayout(QBoxLayout.LeftToRight
                if leftTopPos == LEFT else QBoxLayout.TopToBottom)
        layout.addWidget(self.label)
        layout.addWidget(self.lineEdit)
        self.setLayout(layout)
        self.text = self.lineEdit.text

class LabelledTextEdit(QWidget):
    '''
    This class holds QTextEdit, budded to QLabel
    This is used only to simplify GUI creation 
    '''
    def __init__(self, labelText=QString(), leftTopPos=LEFT,parent=None):
        super(LabelledTextEdit, self).__init__(parent)
        self.label = QLabel(labelText)
        self.textEdit = QTextEdit()
        self.label.setBuddy(self.textEdit)
        layout = QBoxLayout(QBoxLayout.LeftToRight
                if leftTopPos == LEFT else QBoxLayout.TopToBottom)
        layout.addWidget(self.label)
        layout.addWidget(self.textEdit)
        self.setLayout(layout)
        
class LabelledSlider(QWidget):
    '''
    This class holds QSlider, budded to QLabel
    This is used only to simplify GUI creation 
    '''
    def __init__(self, labelText=QString(),orientation=Qt.Horizontal,
                 leftTopPos=LEFT,parent=None):
        super(LabelledSlider, self).__init__(parent)
        
        self.labelText = labelText
        self.slider = QSlider(orientation)
        self.valueChanged = self.slider.valueChanged
        self.label = QLabel(self.labelText+' '+str(self.slider.value()))
        self.label.setBuddy(self.slider)
        self.slider.valueChanged.connect(self.sliderMove)
        layout = QBoxLayout(QBoxLayout.LeftToRight
                if leftTopPos == LEFT else QBoxLayout.TopToBottom)
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        self.setLayout(layout)
        # Creating links to functions
        self.value = self.slider.value
        self.setValue = self.slider.setValue
        self.setMaximum = self.slider.setMaximum
        self.setMinimum = self.slider.setMinimum
        self.setText = self.label.setText
        self.text = self.label.text
    
    def sliderMove(self,value):
        self.label.setText(self.labelText+' '+str(value))
        
class LabelledCheckBox(QWidget):
    '''
    This class holds QCheckBox, budded to QLabel
    This is used only to simplify GUI creation 
    '''
    def __init__(self, labelText=QString(),leftTopPos=LEFT,checked=False,parent=None):
        super(LabelledCheckBox, self).__init__(parent)
        
        self.checkBox = QCheckBox()
        self.label = QLabel(labelText)
        self.label.setBuddy(self.checkBox)
        layout = QBoxLayout(QBoxLayout.LeftToRight
                if leftTopPos == LEFT else QBoxLayout.TopToBottom)
        layout.addWidget(self.label)
        layout.addWidget(self.checkBox)
        self.setLayout(layout)
        # Creating links to functions
        self.checkState = self.checkBox.checkState    
        self.setCheckState = self.checkBox.setCheckState    
        self.setText = self.label.setText
        self.text = self.label.text
        self.stateChanged = self.checkBox.stateChanged
    
