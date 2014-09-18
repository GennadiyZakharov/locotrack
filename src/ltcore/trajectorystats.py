'''
Created on 31 aug. 2014

@author: gena
'''
from __future__ import division,print_function
from PyQt4 import QtCore

class IntervalStats(object):
    def __init__(self):
        self.center = (-1,-1)
        self.totalDuration = 0.0
        self.runDuration = 0.0
        self.RunCount = 0
        self.Length = 0.0
        self.RunLength = 0.0
        

class TrajectoryStats(object):
    '''
    classdocs
    '''
    formatString='{} {} {} {} {}'
    
    def __init__(self):
        '''
        Constructor
        '''
        self.size = QtCore.QSize
        self.totalDuration = 0.0
        self.runDuration = 0.0
        self.totalLength = 0.0
        self.runLength = 0.0
        self.runCount = 0
        self.quadrantTotalDuration = [[0,0],[0,0]]
        self.quadrantTotalLength = [[0,0],[0,0]]
        self.quadrantRunDuration = [[0,0],[0,0]]
        self.quadrantRunLength = [[0,0],[0,0]]
        self.intervals = []
        
        
    def isEmpty(self):
        return self.size.isEmpty()
    
    def setBounds(self, bounds):
        self.size = QtCore.QSize(bounds)
        
    def activityIndex(self):
        return self.runDuration / self.totalDuration
    
    def runFrequency(self):
        return (self.runCount / self.totalDuration )*100
    
    def quandrantActivity(self):
        quandantActivity=[[0,0],[0,0]]
        for x in range(1):
            for y in range(1):
                print(x,y)
                quandantActivity[x][y]=self.quadrantRunDuration[x][y]/self.quadrantTotalDuration[x][y]
        return quandantActivity
        
    def setCenter(self, x,y):
        self.center = (x,y)
        
    def totalInfo(self):
        return self.formatString.format(self.activityIndex(),self.runFrequency(),self.quandrantActivity(),
                                        self.totalLength/self.totalDuration if self.totalDuration >0 else 'N/A',
                                        self.runLength/self.runDuration if self.runDuration >0 else 'N/A') 
               
    