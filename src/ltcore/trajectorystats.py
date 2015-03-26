'''
Created on 31 aug. 2014

@author: gena
'''

from __future__ import division,print_function
from PyQt4 import QtCore
import numpy as np

class IntervalStats(object):
    def __init__(self):
        self.center = (-1,-1)
        self.totalDuration = 0.0
        self.totalLength = 0.0
        self.runDuration = 0.0
        self.RunCount = 0
        
        self.RunLength = 0.0
        

class TrajectoryStats(object):
    '''
    classdocs
    '''
    # Activity  RinFreq, TotalSpeed, RunSpeed Quadrants
    formatString='{:>8.3f}; {:>8.3f}; {}; {}; {};'
    reportString = \
    '''
    Total trajectory duration: {:>8.3f}
    Total trajectory length: {:>8.3f}
    Activity Index {:>8.3f}
    Run length {:>8.3f}
    Run frequency {:>8.3f} 
    Activity on quadrants:
    {:>8.3f}; {:>8.3f};
    {:>8.3f}; {:>8.3f};
    
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        self.size = QtCore.QSize
        self.totalDuration = 0.0
        self.totalLength = 0.0
        self.runDuration = 0.0
        self.runLength = 0.0
        self.runCount = 0
        self.quadrantTotalDuration = [[0,0],[0,0]]
        self.quadrantTotalLength = [[0,0],[0,0]]
        self.quadrantRunDuration = [[0,0],[0,0]]
        self.quadrantRunLength = [[0,0],[0,0]]
        self.intervals = []
        self.hystogram = None
        
        
    def isEmpty(self):
        return self.size.isEmpty()
    
    def setBounds(self, bounds):
        self.size = QtCore.QSize(bounds)
        
    def activityIndex(self):
        return self.runDuration / self.totalDuration
    
    def runFrequency(self):
        return (self.runCount / self.totalDuration )*100
    
    def quandrantActivity(self):
        quandantActivityArr=[[0,0],[0,0]]
        for x in range(2):
            for y in range(2):
                if self.quadrantTotalDuration[x][y] > 0 :
                    quandantActivityArr[x][y]=self.quadrantRunDuration[x][y]/self.quadrantTotalDuration[x][y]
        return quandantActivityArr
        
    def setCenter(self, x,y):
        self.center = (x,y)
        
    def totalSpeedTxt(self):
        return '{:>8.3f}'.format(self.totalLength/self.totalDuration) if self.totalDuration >0 else '{:>8s}'.format('N/A')
        
    def runSpeedTxt(self):
        return '{:>8.3f}'.format(self.runLength/self.runDuration) if self.runDuration >0 else '{:>8s}'.format('N/A')
    
    def totalInfo(self):
        return self.formatString.format(self.activityIndex(),self.runFrequency(),
                                        self.totalSpeedTxt(),
                                        self.runSpeedTxt(),
                                        self.quandrantActivity()) 
        
    def totalReport(self):
        qA = self.quandrantActivity()
        return self.reportString.format(self.totalDuration,self.totalLength,self.activityIndex(),self.runLength,self.runFrequency(),
               qA[0][0],qA[1][0],qA[0][1],qA[1][1])
               
    