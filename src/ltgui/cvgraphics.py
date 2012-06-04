'''
Created on 26.05.2012
@author: gena
'''
from PyQt4 import QtCore, QtGui
import cv
from ltcore.signals import *

class CvGraphics(QtGui.QGraphicsView):
    '''
    classdocs
    '''
    initialSize = (320, 200)
    chamberMove = QtCore.pyqtSignal(int, int)
    chamberResize = QtCore.pyqtSignal(int, int)

    def __init__(self,parent=None):
        '''
        Constructor
        '''
        super(CvGraphics, self).__init__(parent)
        self.frame = QtGui.QImage(320,200,QtGui.QImage.Format_RGB888)
        self.pixmap = QtGui.QPixmap(320,200)
        self.scene = QtGui.QGraphicsScene()
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setScene(self.scene)
        self.setMinimumSize(320,200) 
        self.setAcceptDrops(True)
        self.enableDnD = False
        self.selectedRect = None
        self.gPixmap = self.scene.addPixmap(self.pixmap)
        #self.setFixedSize(self.pixmap.size())
        
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
        # Display image on pixmap
        #self.scene.removeItem(self.label)
        #self.label.setPixmap(QtGui.QPixmap.fromImage(self.frame))
        if self.frame.size() != self.pixmap.size() :
            self.scene.removeItem(self.gPixmap)
            self.pixmap.convertFromImage(self.frame)
            self.gPixmap = self.scene.addPixmap(self.pixmap)
        else :
            self.pixmap.convertFromImage(self.frame)
            self.scene.update()
        
        
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
        print "mousePressed event ",event.pos()
        # If selection not enabled -- exit
        if not self.enableDnD :
            return
        # If it is left button -- store position
        if (event.button() == QtCore.Qt.LeftButton) :
            self.dragStartPosition = self.mapToScene(event.pos()).toPoint()
            

    def mouseMoveEvent(self, event) :
        '''
        Hander is called, when mouse moves
        '''
        print "MouseMove Event"
        # If selection not enabled -- exit
        if not self.enableDnD :
            return
        # If left button not pressed -- exit
        if not (event.buttons() & QtCore.Qt.LeftButton) :
            return
        # If distance between current and start point too small --exit
        if (self.mapToScene(event.pos()).toPoint() - self.dragStartPosition).manhattanLength() < QtGui.QApplication.startDragDistance() :
            return
        # Everything ok
        # Clear previous rect
        self.selectedRect = None
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
        print "dragEnter Event"
        # If selection not enabled -- exit
        if not self.enableDnD :
            return
        if event.mimeData().hasFormat("cvlabel/pos") :
            event.acceptProposedAction()
            
    def dragMoveEvent(self, event):
        '''
        Hander is called, when drag event processes
        '''
        print "DragMove event"
        # If selection not enabled -- exit
        if not self.enableDnD :
            return
        # Saving currenly selected rectangle
        #self.selectedRect = QtCore.QRect(self.dragStartPosition, event.pos())
        #self.updateImage()
    
    def dropEvent(self, event) :
        '''
        Hander is called, when drag finished
        '''
        print "dropEvent"
        # If selection not enabled -- exit
        if not self.enableDnD :
            return
        # Check if we receive drag event with coordinates
        if event.mimeData().hasFormat("cvlabel/pos") :
            # Put selection area into QRect 
            rect = QtCore.QRect(self.dragStartPosition, self.mapToScene(event.pos()).toPoint())
            # And send it via signal
            self.emit(signalRegionSelected, rect)
            event.acceptProposedAction()
            self.selectedRect = None
    '''
    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Left:
            dirX,dirY = -1,0
        elif key == QtCore.Qt.Key_Right :
            dirX,dirY = (1,0)
        elif key == QtCore.Qt.Key_Up :
            dirX,dirY = (0,-1)
        elif key == QtCore.Qt.Key_Down :
            dirX,dirY = (0,1)
        else :
            return
        if (event.modifiers() & QtCore.Qt.ShiftModifier):
            self.chamberResize.emit(dirX,dirY)
        else :
            self.chamberMove.emit(dirX,dirY)
    '''