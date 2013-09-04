'''
Created on 31.08.2012

@author: gena
'''
from __future__ import print_function
from math import sqrt
from PyQt4 import QtCore, QtGui

class ScaleGui(QtGui.QGraphicsObject):
    '''
    This class implements graphic item for scale label
    It 
    '''
    color = QtGui.QColor(0,255,255)
    defaultFont = QtGui.QFont('Arial', pointSize=16)
    signalScaleChanged = QtCore.pyqtSignal(float)

    def __init__(self, rect, parent=None):
        '''
        Constructor
        '''
        super(ScaleGui, self).__init__(parent)
        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable | 
        QtGui.QGraphicsItem.ItemIsMovable | QtGui.QGraphicsItem.ItemIsFocusable)
        self.lengthInMM = 15
        self.updateRect(rect)
           
    def updateRect(self, rect):
        self.size = rect.size()
        self.setPos(QtCore.QPointF(rect.topLeft()))
        self.update()  
        self.calculateScaleFactor()  
    
    def calculateScaleFactor(self):
        diag = sqrt(self.size.height()**2 + self.size.width()**2)
        scaleFactor = diag / self.lengthInMM
        self.signalScaleChanged.emit(scaleFactor)
    
    def mouseDoubleClickEvent(self, event):
        text, ok = QtGui.QInputDialog.getText(None, QtCore.QString('Scale label'), 
            QtCore.QString('Enter scale label actual size (mm):'))
        if ok:
            # TODO: \ check
            try :
                self.lengthInMM = float(text)
            except :
                return
            self.calculateScaleFactor()        
    
    # Painting procedures
    def boundingRect(self):
        return QtCore.QRectF(QtCore.QPointF(0,0),QtCore.QSizeF(self.size))

    def shape(self):
        path = QtGui.QPainterPath()
        stroker = QtGui.QPainterPathStroker()
        stroker.setWidth(3)
        path.moveTo(0,0)
        path.lineTo(self.size.width(), self.size.height())
        
        path.addText(self.size.width()//2,self.size.height()//2, 
                         self.defaultFont,unicode(self.lengthInMM)+' mm') 
        return stroker.createStroke(path)
    
    def paint(self, painter, option, widget=None):
        pen = QtGui.QPen(QtGui.QBrush(self.color), 3)
        painter.setPen(pen)
        painter.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        painter.drawLine(0,0,self.size.width(),self.size.height())
        
        painter.setFont(self.defaultFont)
        painter.drawText(self.size.width()//2,self.size.height()//2, 
                         unicode(self.lengthInMM)+' mm') 
        