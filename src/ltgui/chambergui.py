'''
Created on 26.05.2012
@author: gena
'''
from __future__ import print_function
from __future__ import division
from PyQt4 import QtCore, QtGui

class ltObjectGui((QtGui.QGraphicsObject)):
    def __init__(self, chamber, parent=None):
        super(ltObjectGui, self).__init__(parent)
        self.chamber = chamber

class ChamberGui(QtGui.QGraphicsObject):
    '''
    This is graphic for chamber representation on qgraphicsscene
    '''
    normalColor = QtGui.QColor(0, 255, 0)
    selectedColor = QtGui.QColor(255, 0, 0)
    chamberMove = QtCore.pyqtSignal(int, int)
    chamberResize = QtCore.pyqtSignal(int, int)
    signalSelected = QtCore.pyqtSignal(object)        

    def __init__(self, chamber, parent=None):
        '''
        Constructor
        '''
        super(ChamberGui, self).__init__(parent)
        self.chamber = chamber
        pos = self.mapFromScene(QtCore.QPointF(self.chamber.topLeft()))
        self.setPos(pos)
        self.size = QtCore.QSizeF(self.chamber.size())
        self.chamber.signalPositionUpdated.connect(self.update)
        self.chamberMove.connect(self.chamber.move)
        self.chamberResize.connect(self.chamber.resize)
        self.color = self.normalColor
        #self.acceptDrops()
        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable | 
        QtGui.QGraphicsItem.ItemIsMovable | QtGui.QGraphicsItem.ItemIsFocusable)
        self.xChanged.connect(self.onMove)
        self.yChanged.connect(self.onMove)
    
    # Event handling
    
    def isMoveAllowed(self, rect):
        return self.allowedRect.contains(rect, True)
    
    def setAllowedRect(self, rect):
        self.allowedRect = rect
    
    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Left:
            dirX, dirY = (-1, 0)
        elif key == QtCore.Qt.Key_Right :
            dirX, dirY = (1, 0)
        elif key == QtCore.Qt.Key_Up :
            dirX, dirY = (0, -1)
        elif key == QtCore.Qt.Key_Down :
            dirX, dirY = (0, 1)
        else :
            return
        if (event.modifiers() & QtCore.Qt.ShiftModifier):
            rect = QtCore.QRect(self.chamber.rect)
            rect.setWidth(rect.width() + dirX)
            rect.setHeight(rect.height() + dirY)
            # TODO: minimum chamber size: remove magic number
            if (rect.height() < 5) or (rect.width() < 5) :
                return
            if self.isMoveAllowed(rect) :
                self.chamber.resize(dirX, dirY)
                self.update()
        else :
            self.moveBy(dirX, dirY)
            self.onMove()
    
    def setSelected(self, flag):
        if flag :
            self.color = self.selectedColor
        else :
            self.color = self.normalColor
        self.update()
    
    def onMove(self):
        # graph widget was moved to new pos()
        pos = QtCore.QPoint(int(self.pos().x()), int(self.pos().y()))
        rect = QtCore.QRect(self.chamber.rect)
        rect.moveTo(pos)
        if self.isMoveAllowed(rect) :
            self.chamber.moveTo(QtCore.QPoint(pos.x(), pos.y()))
        else :
            self.setPos(QtCore.QPointF(self.chamber.rect.topLeft()))
    
    def focusInEvent(self, event):
        print('selecting', self.chamber)
        self.signalSelected.emit(self.chamber)
        return QtGui.QGraphicsObject.focusInEvent(self, event)  
    # Painting procedures
    def boundingRect(self):
        return QtCore.QRectF(QtCore.QPointF(0, 0), QtCore.QSizeF(self.chamber.size()))

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(QtCore.QRectF(QtCore.QPointF(0, 0), QtCore.QSizeF(self.chamber.size())))
        stroker = QtGui.QPainterPathStroker()
        stroker.setWidth(3)
        return stroker.createStroke(path);
    
    def paint(self, painter, option, widget=None):
        pen = QtGui.QPen(QtGui.QBrush(self.color), 3)
        painter.setPen(pen)
        painter.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        sizeX,sizeY = self.chamber.size().width(),self.chamber.size().height()
        painter.drawRect(QtCore.QRectF(QtCore.QPointF(0, 0), QtCore.QSizeF(self.chamber.size())))
        painter.drawEllipse(QtCore.QRectF(QtCore.QPointF(0, 0), QtCore.QSizeF(self.chamber.size())))
        pen = QtGui.QPen(QtGui.QBrush(self.selectedColor), 3)
        painter.setPen(pen)
        painter.setFont(QtGui.QFont('Times', 15, QtGui.QFont.DemiBold))
        rect = QtCore.QRectF(0, 0, 15, 20)
        painter.drawText(rect, QtCore.Qt.AlignCenter, str(self.chamber.number));
        if self.chamber.showTrajectory and (self.chamber.trajectoryImage is not None):
            painter.drawImage(QtCore.QPointF(0, 0), self.chamber.trajectoryImage)
        pen = QtGui.QPen(QtGui.QBrush(self.color), 1)
        painter.setPen(pen)
        painter.drawLine(0,sizeY//2,sizeX,sizeY//2)
        painter.drawLine(sizeX//2,0,sizeX//2,sizeY)
