'''
Created on 19.03.2011

@author: Gena
'''

from __future__ import division
from __future__ import unicode_literals
from future_builtins import *
from ltcore.signals import *

from PyQt4.QtCore import QString,Qt
from PyQt4.QtGui import (QBoxLayout,
        QLabel, QLineEdit, QTextEdit, QSlider,
        QWidget)

LEFT, ABOVE = range(2)

class LabelledLineEdit(QWidget):

    def __init__(self, labelText=QString(), position=LEFT,parent=None):
        super(LabelledLineEdit, self).__init__(parent)
        self.label = QLabel(labelText)
        self.lineEdit = QLineEdit()
        self.label.setBuddy(self.lineEdit)
        layout = QBoxLayout(QBoxLayout.LeftToRight
                if position == LEFT else QBoxLayout.TopToBottom)
        layout.addWidget(self.label)
        layout.addWidget(self.lineEdit)
        self.setLayout(layout)

class LabelledTextEdit(QWidget):

    def __init__(self, labelText=QString(), position=LEFT,parent=None):
        super(LabelledTextEdit, self).__init__(parent)
        self.label = QLabel(labelText)
        self.textEdit = QTextEdit()
        self.label.setBuddy(self.textEdit)
        layout = QBoxLayout(QBoxLayout.LeftToRight
                if position == LEFT else QBoxLayout.TopToBottom)
        layout.addWidget(self.label)
        layout.addWidget(self.textEdit)
        self.setLayout(layout)
        
class LabelledSlider(QWidget):

    def __init__(self, labelText=QString(),orientation=Qt.Horizontal,
                 position=LEFT,parent=None):
        super(LabelledSlider, self).__init__(parent)
        
        self.labelText = labelText
        self.slider = QSlider(orientation)
        self.label = QLabel(self.labelText+' '+str(self.slider.value()))
        self.label.setBuddy(self.slider)
        self.connect(self.slider,signalValueChanged, self.on_sliderMove)
        layout = QBoxLayout(QBoxLayout.LeftToRight
                if position == LEFT else QBoxLayout.TopToBottom)
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        self.setLayout(layout)
        
        # Creating links to functions
        self.value = self.slider.value
        self.setMaximum = self.slider.setMaximum
        self.setMinimum = self.slider.setMinimum
        
        self.setText = self.label.setText
        self.text = self.label.text
    
    def on_sliderMove(self,value):
        self.label.setText(self.labelText+' '+str(value))
        self.emit(signalValueChanged,value)