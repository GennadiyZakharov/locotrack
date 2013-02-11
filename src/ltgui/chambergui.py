'''
Created on 26.05.2012

@author: gena
'''
from PyQt4 import QtCore, QtGui

class ChamberGui(QtGui.QGraphicsObject):
    '''
    This is graphic for chamber representation on qgraphicsscene
    '''
    normalColor = QtGui.QColor(0,255,0)
    selectedColor = QtGui.QColor(255,0,0)
    chamberMove = QtCore.pyqtSignal(int, int)
    chamberResize = QtCore.pyqtSignal(int, int)
    signalSelected = QtCore.pyqtSignal(object)

    def __init__(self,chamber,parent=None):
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
            self.chamber.resize(dirX,dirY)
            self.update()
        else :
            self.moveBy(dirX,dirY)
            self.onMove()
    
    def setSelected(self, flag):
        print 'selecting', flag
        if flag :
            self.color = self.selectedColor
        else :
            self.color = self.normalColor
        self.update()
    
    def onMove(self):
        # graph widget was moved to new pos()
        pos = self.pos()
        self.chamber.moveTo(QtCore.QPoint(pos.x(),pos.y()))
    
    def focusInEvent(self, event):
        self.signalSelected.emit(self.chamber)
        return QtGui.QGraphicsObject.focusInEvent(self, event)  
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
        painter.drawText(QtCore.QPointF(0,0), str(self.chamber.number))
        painter.drawEllipse(QtCore.QRectF(QtCore.QPointF(0,0),QtCore.QSizeF(self.chamber.size())))
        
        if self.chamber.showTrajectory and (self.chamber.trajectoryImage is not None):
            painter.drawImage(QtCore.QPointF(0,0),self.chamber.trajectoryImage)
        
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