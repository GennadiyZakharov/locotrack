'''
Created on 26.05.2012

@author: gena
'''
from PyQt4 import QtCore, QtGui

class GChamber(QtGui.QGraphicsObject):
    '''
    classdocs
    '''
    color = QtGui.QColor(0,255,0)
    chamberMove = QtCore.pyqtSignal(int, int)
    chamberResize = QtCore.pyqtSignal(int, int)

    def __init__(self,chamber,parent=None):
        '''
        Constructor
        '''
        super(GChamber, self).__init__(parent)
        self.chamber = chamber
        self.
    
    # Event handling
    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Left:
            dirX,dirY = (-1,0)
        elif key == QtCore.Qt.Key_Right :
            dirX,dirY = (1,0)
        elif key == QtCore.Qt.Key_Up :
            dirX,dirY = (0,-1)
        elif key == QtCore.Qt.Key_Down :
            dirX,dirY = (0,1)
        else :
            return
        if (event.modifiers() & QtCore.Qt.ShiftModifier):
            self.chamber.resize.emit(dirX,dirY)
        else :
            self.chamber.move.emit(dirX,dirY)
    
    
    
    
    
    # Painting procedures
    def boundingRect(self):
        return self.chamber.getRect()

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(self.chamber.getRect())
        return path
    
    def paint(self, painter, option, widget=None):
        painter.setPen(QtCore.Qt.SolidLine)
        #painter.setBrush(QtGui.QBrush(self.node.color))
        painter.drawRect(self.chamber.getRect())
        painter.drawEllipse(self.chamber.getRect())
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