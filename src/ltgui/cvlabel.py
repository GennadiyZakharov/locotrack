'''
Created on 18.03.2011
@author: Gena
'''

from PyQt4 import QtCore, QtGui
import cv

from ltcore.signals import *


class CvLabel(QtGui.QLabel):
    '''
    This QT class is used to display frame in
    IplImage format, used by OpenCV
    
    Also it can handle mouse drag across the frame
    this ability is uded to define chambers and scale
    '''
    # Initial size of the label
    initialCvLabelSize = (640, 480)

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(CvLabel, self).__init__(parent)
        
        self.setAcceptDrops(True)
        # This flag is used to enable selection
        self.enableDnD = False
        self.selectedRect = None
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        # Creating black rectangle
        self.putImage(cv.CreateImage(self.initialCvLabelSize, cv.IPL_DEPTH_8U, 3))
        # Creating color table to display gray image as indexed 8bit
        self.colortable = [QtGui.qRgb(i,i,i) for i in xrange(256)]
    
    def putImage(self, iplImage) :
        '''
        convert iplImage to QLabel and store it in self.frame
        '''
        if iplImage is None :
            return
        # switch between bit depths
        if iplImage.depth == cv.IPL_DEPTH_8U :
            if  iplImage.nChannels == 3:
                # Displaying color image
                cstr = iplImage.tostring()
                self.frame = QtGui.QImage(cstr, iplImage.width, iplImage.height, QtGui.QImage.Format_RGB888).rgbSwapped()
                self.updateImage()
            elif iplImage.nChannels == 1:
                # Displaying B&W image as 8bit indexed
                cstr = iplImage.tostring()
                self.frame = QtGui.QImage(cstr, iplImage.width, iplImage.height, QtGui.QImage.Format_Indexed8)
                self.frame.setColorTable(self.colortable)
                self.updateImage()
            else :
                # TODO: Make exception
                print("This number of channels is not supported")   
        else :
            # TODO: Make exception
            print("This type of IplImage is not implemented")

    def updateImage(self):
        '''
        Display frame and draw selected region
        '''
        if self.selectedRect is not None :
            # We neet to draw somethong on image
            # Creating image from stored frame
            image = QtGui.QImage(self.frame)
            # Creating pen to draw
            pen = QtGui.QPen(QtCore.Qt.blue)
            pen.setWidth(3)
            pen.setStyle(QtCore.Qt.DashLine)
            # Creating brush 
            brush = QtGui.QBrush(QtCore.Qt.blue, QtCore.Qt.Dense6Pattern)
            # Prepare for painting
            painter = QtGui.QPainter()           
            painter.begin(image)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setPen(pen)
            painter.setBrush(brush)
            # Painting rectangle
            painter.drawRect(self.selectedRect)    
            # Painting diagonal line     
            painter.drawLine(QtCore.QLine(self.selectedRect.topLeft(),
                                           self.selectedRect.bottomRight()))
            painter.end()            
        else :
            # Nothing to draw -- image is equal to stored frame
            image = self.frame
        # Display image on pixmap
        self.setPixmap(QtGui.QPixmap.fromImage(image))
            
    
    def enableSelection(self, enable):
        '''
        Enable region selection
        '''
        self.enableDnD = enable

    def mousePressEvent(self, event) :
        '''
        Hander is called, when mouse button is pressed
        '''
        # If selection not enabled -- exit
        if not self.enableDnD :
            return
        # If it is left button -- store position
        if (event.button() == QtCore.Qt.LeftButton) :
            self.dragStartPosition = event.pos()

    def mouseMoveEvent(self, event) :
        '''
        Hander is called, when mouse moves
        '''
        # If selection not enabled -- exit
        if not self.enableDnD :
            return
        # If left button not pressed -- exit
        if not (event.buttons() & QtCore.Qt.LeftButton) :
            return
        # If distance between current and start point too small --exit
        if (event.pos() - self.dragStartPosition).manhattanLength() < QtGui.QApplication.startDragDistance() :
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
        drag.start(QtCore.Qt.CopyAction)
        # Update image to draw selected region on it
        self.updateImage()
    
    def dragEnterEvent(self, event) :
        '''
        Starting drag
        '''
        # If selection not enabled -- exit
        if not self.enableDnD :
            return
        
        if event.mimeData().hasFormat("cvlabel/pos") :
            event.acceptProposedAction()
            
    def dragMoveEvent(self, event):
        '''
        Hander is called, when drag event processes
        '''
        # If selection not enabled -- exit
        if not self.enableDnD :
            return
        # Saving currenly selected rectangle
        self.selectedRect = QtCore.QRect(self.dragStartPosition, event.pos())
        self.updateImage()
    
    def dropEvent(self, event) :
        '''
        Hander is called, when drag finished
        '''
        # If selection not enabled -- exit
        if not self.enableDnD :
            return
        # Check if we receive drag event with coordinates
        if event.mimeData().hasFormat("cvlabel/pos") :
            # Put selection area into QRect 
            rect = QtCore.QRect(self.dragStartPosition, event.pos())
            # And send it via signal
            self.emit(signalRegionSelected, rect)
            event.acceptProposedAction()
            self.selectedRect = None
            