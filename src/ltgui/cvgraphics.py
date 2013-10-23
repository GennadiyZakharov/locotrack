'''
Created on 26.05.2012
@author: gena
'''
from PyQt4 import QtCore, QtGui
import cv
from ltgui.chambergui import ChamberGui
from ltgui.scalegui import ScaleGui

class CvGraphics(QtGui.QGraphicsView):
    '''
    This is main class for all video GUI:
    -video frame
    -chamber objects
    -scale objects
    '''
    initialSize = (320, 200)
    chamberMove = QtCore.pyqtSignal(int, int)
    chamberResize = QtCore.pyqtSignal(int, int)
    signalChamberSetted = QtCore.pyqtSignal(QtCore.QRect)
    signalScaleSetted = QtCore.pyqtSignal(float)  
    
    signalChamberSelected = QtCore.pyqtSignal(object)  
    
    selectingScale = 1
    selectingChamber = 2

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(CvGraphics, self).__init__(parent)
        self.frame = QtGui.QImage(320, 200, QtGui.QImage.Format_RGB888)
        self.pixmap = QtGui.QPixmap(320, 200)
        self.scene = QtGui.QGraphicsScene()
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setScene(self.scene)
        self.setAcceptDrops(True)
        self.selecting = None
        self.selectedRect = None
        #insert pixmap into (0,0)
        self.pixmapObject = self.scene.addPixmap(self.pixmap)
        self.scene.setSceneRect(self.pixmapObject.boundingRect())
        self.chambersGui = {} # dict to store gui for cahmbers
        self.scaleGui = None  # May be only one gui for scale label
        self.selectedChamber = None
        self.dragStartPosition = None
        
    @QtCore.pyqtSlot(object)
    def putImage(self, iplImage) :
        '''
        convert iplImage to QPixMap and store it in self.frame
        '''
        if iplImage is None :
            return
        # checking bit depths
        if iplImage.depth != cv.IPL_DEPTH_8U :
            # TODO: Make exception
            print("This type of IplImage is not implemented")
        cstr = iplImage.tostring()
        if  iplImage.nChannels == 3:
            # Displaying color image
            self.frame = QtGui.QImage(cstr, iplImage.width, iplImage.height, QtGui.QImage.Format_RGB888).rgbSwapped()        
        elif iplImage.nChannels == 1:
            # Displaying B&W image as 8bit indexed
            self.frame = QtGui.QImage(cstr, iplImage.width, iplImage.height, QtGui.QImage.Format_Indexed8)
            self.frame.setColorTable(self.colorTable)
        else :
            # TODO: Make exception
            print("This number of channels is not supported")
            return 
        self.updateImage()
    
    def updateImage(self):
        '''
        Display frame and draw selected region
        '''
        if self.frame.size() != self.pixmap.size() :
            self.scene.removeItem(self.pixmapObject)
            self.pixmap.convertFromImage(self.frame)
            self.pixmapObject = self.scene.addPixmap(self.pixmap)
            self.pixmapObject.setZValue(-1)
            self.scene.setSceneRect(self.pixmapObject.boundingRect())

        else :
            self.pixmap.convertFromImage(self.frame)
            self.scene.update()
    
    @QtCore.pyqtSlot(object)
    def selectChamberGui(self, chamber):
        if chamber is self.selectedChamber :
            return
        if self.selectedChamber is not None :
            self.chambersGui[self.selectedChamber].setSelected(False)
        self.selectedChamber = chamber
        if chamber is not None : 
            self.chambersGui[chamber].setSelected(True)
        self.signalChamberSelected.emit(chamber)
    
    @QtCore.pyqtSlot(object)
    def addChamberGui(self, chamber):
        '''
        new chamber was created
        '''
        chamberGui = ChamberGui(chamber)
        chamberGui.setAllowedRect(self.pixmap.rect())
        self.scene.addItem(chamberGui)
        self.chambersGui[chamber] = chamberGui 
        chamberGui.signalSelected.connect(self.selectChamberGui)
    
    @QtCore.pyqtSlot(object)
    def delChamberGui(self, chamber):
        '''
        chamber is schelded for remove -- must remove gui for it
        '''
        self.selectChamberGui(None)
        chambeGui = self.chambersGui[chamber]
        self.scene.removeItem(chambeGui)
        del chambeGui
        del self.chambersGui[chamber]
    
    @QtCore.pyqtSlot(QtCore.QRect)
    def setScaleGui(self, rect):
        if self.scaleGui is None:
            self.scaleGui = ScaleGui(rect)
            self.scaleGui.signalScaleChanged.connect(self.signalScaleSetted.emit)
            self.scene.addItem(self.scaleGui)
            self.scaleGui.calculateScaleFactor()
        else :
            self.scaleGui.updateRect(rect)
    
    @QtCore.pyqtSlot()
    def delScaleGui(self):
        if self.scaleGui is not None :
            self.scene.removeItem(self.scaleGui)
            self.scaleGui = None
    
    @QtCore.pyqtSlot(bool)
    def selectScale(self, checked):
        self.selecting = self.selectingScale if checked else None
    
    @QtCore.pyqtSlot(bool)
    def selectChamber(self, checked):
        self.selecting = self.selectingChamber if checked else None
    
    def isPointAllowed(self, point):
        return self.pixmapObject.boundingRect().contains(point)
    
    def mousePressEvent(self, event) :
        # If selection not enabled -- exit
        if self.selecting is None :
            super(CvGraphics, self).mousePressEvent(event)
            return
        if not (event.buttons() & QtCore.Qt.LeftButton) :
            return
        pos = self.mapToScene(event.pos())
        if not self.isPointAllowed(pos) :
            return
        self.dragStartPosition = pos

    def mouseMoveEvent(self, event) :
        if self.selecting is None :
            super(CvGraphics, self).mouseMoveEvent(event)
            return
        if self.dragStartPosition is None :
            return
        # If left button not pressed -- exit
        if not (event.buttons() & QtCore.Qt.LeftButton) :
            return
        pos = self.mapToScene(event.pos())
        if not self.isPointAllowed(pos) :
            return
        # If distance between current and start point too small --exit
        if (pos - self.dragStartPosition).manhattanLength() < QtGui.QApplication.startDragDistance() :
            return
        # Everything ok
        pen = QtGui.QPen(QtGui.QColor(0, 0, 255))
        # Creating line or rect according to task
        if self.selecting == self.selectingScale :
            self.selectedRect = self.scene.addLine(QtCore.QLineF(pos, self.dragStartPosition), pen)
        else :
            self.selectedRect = self.scene.addRect(QtCore.QRectF(pos, self.dragStartPosition), pen)
        # Constructing data with start pos 
        mimeData = QtCore.QMimeData();
        data = QtCore.QByteArray()
        stream = QtCore.QDataStream(data, QtCore.QIODevice.WriteOnly)
        stream << self.dragStartPosition
        mimeData.setData("cvlabel/pos", data);
        # Creating drag event
        drag = QtGui.QDrag(self);
        drag.setMimeData(mimeData);
        '''
        # Set icon
        pixmap = icon.pixmap(24, 24)
        drag.setHotSpot(QtCore.QPoint(12, 12))
        drag.setPixmap(pixmap)
        '''
        # Starting drag
        drag.start()
        # Update image to draw selected region on it
        # self.updateImage()
    
    def dragEnterEvent(self, event) :
        if self.selecting is None :
            super(CvGraphics, self).dragEnterEvent(event)
            return
        if event.mimeData().hasFormat("cvlabel/pos") :
            event.acceptProposedAction()
            
    def dragMoveEvent(self, event):
        # If selection not enabled -- exit
        if self.selecting is None :
            super(CvGraphics, self).dragMoveEvent(event)
            return
        pos = self.mapToScene(event.pos())
        if not self.isPointAllowed(pos):
            return
        # Saving currenly selected rectangle
        if self.selecting == self.selectingScale :
            self.selectedRect.setLine(QtCore.QLineF(self.dragStartPosition, pos))
        elif self.selecting == self.selectingChamber :
            self.selectedRect.setRect(QtCore.QRectF(self.dragStartPosition, pos).normalized())
        #self.scene.update()
    
    def dropEvent(self, event) :
        if self.selecting is None :
            super(CvGraphics, self).dropEvent(event)
            return
        # Check if we receive drag event with coordinates
        if event.mimeData().hasFormat("cvlabel/pos") :
            # Put selection area into QRect 
            pos = self.mapToScene(event.pos())
            rect = QtCore.QRect(self.dragStartPosition.toPoint(), pos.toPoint())
            # And send it via signal
            self.scene.removeItem(self.selectedRect)
            self.selectedRect = None
            self.dragStartPosition = None
            event.acceptProposedAction()
            if self.selecting == self.selectingChamber :
                self.signalChamberSetted.emit(rect)
            elif self.selecting == self.selectingScale :
                self.setScaleGui(rect)
            
