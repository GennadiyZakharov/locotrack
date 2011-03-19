'''
Created on 18.03.2011

@author: Gena
'''

from PyQt4 import QtCore,QtGui
import cv

from ltcore.signals import *

minCvLabelSize=(200,200)

class CvLabel(QtGui.QLabel):
    '''
    classdocs
    '''
    

    def __init__(self,parent=None):
        '''
        Constructor
        '''
        super(CvLabel, self).__init__(parent)
        self.setAcceptDrops(True)
        self.enableDnD = False
        tempimage = cv.CreateImage(minCvLabelSize,cv.IPL_DEPTH_8U,3)
        self.putImage(tempimage)
    
    def putImage(self,cvimage) :
        # switch between bit depths
        if cvimage.depth == cv.IPL_DEPTH_8U :
            if  cvimage.nChannels == 3:
                str = cvimage.tostring()
                image = QtGui.QImage(str,cvimage.width,cvimage.height,QtGui.QImage.Format_RGB888)
                self.setPixmap(QtGui.QPixmap.fromImage(image.rgbSwapped()))
            else :
                print("This number of channels is not supported")
                    
        else :
            print("This type of IplImage is not implemented")

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
    
    def dragEnterEvent(self, event) :
        if not self.enableDnD :
            return
        if event.mimeData().hasFormat("cvlabel/pos") :
            event.acceptProposedAction()
    
    
    def dropEvent(self, event) :
        if not self.enableDnD :
            return
        if event.mimeData().hasFormat("cvlabel/pos") :
            rect = QtCore.QRect(self.dragStartPosition,event.pos())
            
            self.emit(signalRegionSelected,rect)
            event.acceptProposedAction()
            