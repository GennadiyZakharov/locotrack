'''
Created on 18.03.2011

@author: Gena
'''

from PyQt4 import QtGui
import cv

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
        tempimage = cv.CreateImage(minCvLabelSize,cv.IPL_DEPTH_8U,3)
        self.putImage(tempimage)
    
    def putImage(self,cvimage) :
        # switch between bit depths
        if cvimage.depth == cv.IPL_DEPTH_8U :
            if  cvimage.nChannels == 3:
                str = cvimage.tostring()
                image = QtGui.QImage(str,cvimage.width,cvimage.height,QtGui.QImage.Format_RGB888)
                self.setPixmap(QtGui.QPixmap.fromImage(image))
            else :
                print("This number of channels is not supported")
                    
        else :
            print("This type of IplImage is not implemented in QOpenCVWidget")
