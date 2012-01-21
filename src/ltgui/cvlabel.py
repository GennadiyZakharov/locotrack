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
    
    minCvLabelSize = (640, 480)

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(CvLabel, self).__init__(parent)
        
        self.setAcceptDrops(True)
        self.enableDnD = False
        self.selectedRect = None
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        # Creating black rectangle
        self.putImage(cv.CreateImage(self.minCvLabelSize, cv.IPL_DEPTH_8U, 3))
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
                cstr = iplImage.tostring()
                self.frame = QtGui.QImage(cstr, iplImage.width, iplImage.height, QtGui.QImage.Format_RGB888).rgbSwapped()
                self.updateImage()
            elif iplImage.nChannels == 1:
                cstr = iplImage.tostring()
                self.frame = QtGui.QImage(cstr, iplImage.width, iplImage.height, QtGui.QImage.Format_Indexed8)
                self.frame.setColorTable(self.colortable)
                #self.frame = QtGui.QImage(cstr, )
                self.updateImage()
            else :
                print("This number of channels is not supported")
                    
        else :
            print("This type of IplImage is not implemented")

    def updateImage(self):
        '''
        Display frame on label and draw mouse trace
        '''
        if self.selectedRect is not None :
            image = QtGui.QImage(self.frame)
            
            pen = QtGui.QPen(QtCore.Qt.blue)
            pen.setWidth(3)
            pen.setStyle(QtCore.Qt.DashLine)
            
            brush = QtGui.QBrush(QtCore.Qt.blue, QtCore.Qt.Dense6Pattern)
            
            painter = QtGui.QPainter()           
            painter.begin(image)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setPen(pen)
            painter.setBrush(brush)
            
            painter.drawRect(self.selectedRect)         
            painter.drawLine(QtCore.QLine(self.selectedRect.topLeft(),
                                           self.selectedRect.bottomRight()))
            self.setPixmap(QtGui.QPixmap.fromImage(image))
            painter.end()
        else :
            self.setPixmap(QtGui.QPixmap.fromImage(self.frame))
            
    
    def on_EnableDnD(self, enable):
        self.enableDnD = enable

    def mousePressEvent(self, event) :
        if not self.enableDnD :
            return
        if (event.button() == QtCore.Qt.LeftButton) :
            self.dragStartPosition = event.pos()

    def mouseMoveEvent(self, event) :
        if not self.enableDnD :
            return
        if not (event.buttons() & QtCore.Qt.LeftButton) :
            return
        if (event.pos() - self.dragStartPosition).manhattanLength() < QtGui.QApplication.startDragDistance() :
            return
        
        mimeData = QtCore.QMimeData();
        data = QtCore.QByteArray()
        stream = QtCore.QDataStream(data, QtCore.QIODevice.WriteOnly)
        stream << self.dragStartPosition
        mimeData.setData("cvlabel/pos", data);
        
        drag = QtGui.QDrag(self);
        drag.setMimeData(mimeData);
        '''
        pixmap = icon.pixmap(24, 24)
        drag.setHotSpot(QtCore.QPoint(12, 12))
        drag.setPixmap(pixmap)
        '''
        drag.start(QtCore.Qt.CopyAction)
        
        self.selectedRect = None
        self.updateImage()
    
    def dragEnterEvent(self, event) :
        if not self.enableDnD :
            return
        if event.mimeData().hasFormat("cvlabel/pos") :
            event.acceptProposedAction()
            
    def dragMoveEvent(self, event):
        if not self.enableDnD :
            return
        #self.emit(signalDragging,))
        # # Drawing the main rectangle
        self.selectedRect = QtCore.QRect(self.dragStartPosition, event.pos())
        self.updateImage()
    
    def dropEvent(self, event) :
        if not self.enableDnD :
            return
        if event.mimeData().hasFormat("cvlabel/pos") :
            rect = QtCore.QRect(self.dragStartPosition, event.pos())
            self.emit(signalRegionSelected, rect)
            event.acceptProposedAction()
            
