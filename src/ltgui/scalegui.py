'''
Created on 31.08.2012

@author: gena
'''
from PyQt4 import QtCore, QtGui

class ScaleGui(QtGui.QGraphicsObject):
    '''
    classdocs
    '''
    color = QtGui.QColor(0,255,0)
    signalScaleChanged = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(ScaleGui, self).__init__(parent)
        self.lengthInMM = 15
        self.lengthInPixels = 100
        self.signalScaleChanged.emit(-1)
        
    # Painting procedures
    def boundingRect(self):
        return QtCore.QRectF(QtCore.QPointF(0,0),QtCore.QSizeF(self.chamber.size()))

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(QtCore.QRectF(QtCore.QPointF(0,0),QtCore.QSizeF(self.chamber.size())))
        return path
    
    def paint(self, painter, option, widget=None):
        pen = QtGui.QPen(QtGui.QBrush(self.color), 3)
        painter.setPen(pen)
        painter.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        painter.drawRect(QtCore.QRectF(QtCore.QPointF(0,0),QtCore.QSizeF(self.chamber.size())))
        painter.drawEllipse(QtCore.QRectF(QtCore.QPointF(0,0),QtCore.QSizeF(self.chamber.size())))
        '''
        painter.setFont(QtGui.QFont('Arial', pointSize=16))
        painter.drawText(self.NameRect, QtCore.Qt.AlignCenter, self.node.name) 
        painter.setFont(QtGui.QFont('Arial', pointSize=12))
        if self.currentPlayer in self.node.viewers:
            infoText = 'Storage: {0}/{1}\n '.format(len(self.node.storage),self.node.storageCapacity)
            demandsText = []
            demandsDict = self.node.getDemands()
            if demandsDict != {} :
                for name,count in demandsDict.items() :
                    demandsText.append('{0} - {1} '.format(name, count))
                infoText+='\nDemands:\n'+'\n'.join(demandsText)
            painter.drawText(self.InfoRect, QtCore.Qt.AlignCenter, infoText)
            if len(self.node.entered) != 0 :
                painter.setBrush(QtGui.QBrush(self.SelectColor))
                painter.setPen(QtGui.QPen(QtGui.QBrush(self.SelectColor), 3))
                painter.drawEllipse(self.Rect.bottomRight()-QtCore.QPointF(15, 15),10,10)
        if self.hasFocus() :
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.setPen(QtGui.QPen(QtGui.QBrush(self.SelectColor), 3))
            painter.drawRect(self.Rect.adjusted(2, 2, -2, -2))
        if self.node.owner != self.currentPlayer:
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.setPen(QtGui.QPen(QtGui.QBrush(self.InactiveColor), 3))
            painter.drawRect(self.Rect.adjusted(2, 2, -2, -2))
        '''