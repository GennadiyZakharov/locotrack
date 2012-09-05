'''
Created on 26.05.2012
@author: gena
'''
from PyQt4 import QtCore, QtGui
import cv
from ltcore.signals import *
from ltgui.chambergui import ChamberGui

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
        self.setMinimumSize(320, 200) 
        self.setAcceptDrops(True)
        self.enableDnD = False
        self.selectedRect = None
        #insert pixmap into (0,0)
        self.pixmapObject = self.scene.addPixmap(self.pixmap)
        #self.pixmapObject.setScale(1.0)
        self.scene.setSceneRect(self.pixmapObject.boundingRect())
        self.chambers = {}
        
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
            self.scene.setSceneRect(self.pixmapObject.boundingRect())
        else :
            self.pixmap.convertFromImage(self.frame)
            self.scene.update()
        
    def updatePixpamSize(self):
        self.setSizePolicy(QtCore.Qt.QSizePolicy)
    
    @QtCore.pyqtSlot(bool)
    def selectScale(self, checked):
        self.enableDnD = checked
    
    @QtCore.pyqtSlot(bool)
    def selectChamber(self, checked):
        self.enableDnD = checked
    
    @QtCore.pyqtSlot(bool)
    def enableSelection(self, enable):
        '''
        Enable region selection
        '''
        self.enableDnD = enable
    
    
    # TODO: deal with drag. it seems, that it is something wrong
    def mousePressEvent(self, event) :
        '''
        Hander is called, when mouse button is pressed
        '''
        # If selection not enabled -- exit
        if not self.enableDnD :
            super(CvGraphics, self).mousePressEvent(event)
            return
        print "mousePressed event ", event.pos()
        # If it is left button -- store position
        if (event.button() == QtCore.Qt.LeftButton) :
            self.dragStartPosition = self.mapToScene(event.pos()).toPoint()
            

    def mouseMoveEvent(self, event) :
        '''
        Hander is called, when mouse moves
        '''
        # If selection not enabled -- exit
        if not self.enableDnD :
            super(CvGraphics, self).mouseMoveEvent(event)
            return
        print "MouseMove Event"
        # If left button not pressed -- exit
        if not (event.buttons() & QtCore.Qt.LeftButton) :
            return
        pos = self.mapToScene(event.pos()).toPoint()
        # If distance between current and start point too small --exit
        if (pos - self.dragStartPosition).manhattanLength() < QtGui.QApplication.startDragDistance() :
            return
        # Everything ok
        pen = QtGui.QPen(QtGui.QColor(0, 0, 255))
        self.selectedRect = self.scene.addRect(QtCore.QRectF(QtCore.QRect(pos, self.dragStartPosition)), pen)
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
        print "drag start"
        drag.start(QtCore.Qt.CopyAction)
        # Update image to draw selected region on it
        self.updateImage()
    
    def dragEnterEvent(self, event) :
        '''
        Starting drag
        '''
        # If selection not enabled -- exit
        if not self.enableDnD :
            super(CvGraphics, self).dragEnterEvent(event)
            return
        print "dragEnter Event"
        if event.mimeData().hasFormat("cvlabel/pos") :
            event.acceptProposedAction()
            
    def dragMoveEvent(self, event):
        '''
        Hander is called, when drag event processes
        '''
        # If selection not enabled -- exit
        if not self.enableDnD :
            super(CvGraphics, self).dragMoveEvent(event)
            return
        print "DragMove event"
        print event.pos()
        # Saving currenly selected rectangle
        self.selectedRect.setRect(QtCore.QRectF(QtCore.QRect(self.mapToScene(event.pos()).toPoint(), self.dragStartPosition)))
        self.scene.update()
    
    def dropEvent(self, event) :
        '''
        Hander is called, when drag finished
        '''
        
        # If selection not enabled -- exit
        if not self.enableDnD :
            super(CvGraphics, self).dropEvent(event)
            return
        print "dropEvent"
        # Check if we receive drag event with coordinates
        if event.mimeData().hasFormat("cvlabel/pos") :
            # Put selection area into QRect 
            rect = QtCore.QRect(self.dragStartPosition, self.mapToScene(event.pos()).toPoint())
            # And send it via signal
            self.emit(signalRegionSelected, rect)
            event.acceptProposedAction()
            self.scene.removeItem(self.selectedRect)
            self.selectedRect = None
    
    def updateChambers(self, chambers, selected):
        print 'updating gui chambers'
        for i in range(len(chambers)) :
            if not chambers[i] in self.chambers.keys() :
                chamberGui = ChamberGui(chambers[i])
                self.scene.addItem(chamberGui)
                print 'cgambergui', chamberGui.pos()
                #chamberGui.update()
                self.chambers[chambers[i]]=chamberGui
                #chamberGui.setFocus()
            self.chambers[chambers[i]].setSelected(i==selected)
        dels = []
        for chamber in self.chambers.keys() :
            if not chamber in chambers :
                dels.append(chamber)
        print 'deleting', dels
        for chamber in dels :
            self.scene.removeItem(self.chambers[chamber])
            del self.chambers[chamber]