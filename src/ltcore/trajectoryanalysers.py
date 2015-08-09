'''
Created on 10.10.2013

@author: gena
'''
from __future__ import division
from math import sqrt
from PyQt4 import QtCore, QtGui
from ltcore.trajectorystats import TrajectoryStats,IntervalStats
import numpy as np
from matplotlib.colors import LogNorm
import math

import matplotlib as mpl
from numpy import uint32, float32



class RunRestAnalyser(QtCore.QObject):
    #            sampleName activity  speed  freq file name
    outString = '{:>25}; {:10.4f}; {:10.4f};  {:10.4f}; {:10.4f}; {:6.2f}; {:6.2f}; {:6.2f}; {:6.2f};  {:10.2f}; {:10.2f}; {:10.2f}; {:10.2f}; {};\n'
    #               sample int  run time  run speed      file name
    outStringRuns = '{:>25}; {:5}; {:18.6f}; {:18.6f};   {};\n'
    #sample, interval, activity, speed, fileName

    
    def __init__(self, errorDetector, parent=None):
        '''
        Constructor
        '''
        super(RunRestAnalyser, self).__init__(parent)
        self.intervalDuration = 300.0 # Interval 5 minutes
        self.quantDuration = 1.0      # Length of quant 
        self.runRestSpeedThreshold = 5.0 # For imago
        self.runLengthThreshold = 0.6 # mm
        #self.runRestSpeedThreshold = 0.4 # For larva
        '''
        Speed run/rest threshold 
            0.4 mm/s for imago (smoothed trajectory)
            5.0 mm/s for imago (raw trajectory)
        '''
    
    @QtCore.pyqtSlot(float)
    def setRunRestSpeedThreshold(self, value):
        self.runRestSpeedThreshold = value
        
    @QtCore.pyqtSlot(float)
    def setRunLengthThreshold(self, value):
        self.runLengthThreshold = value
        
    @QtCore.pyqtSlot(float)
    def setIntervalDuration(self, value):
        self.intervalDuration = value
        
    @QtCore.pyqtSlot(float)
    def setQuantDuration(self, value):
        self.quantDuration = value
    
    def analyseChamber(self, chamber, scale, frameRate):
        '''
        Analysing chamber using Run-Rest and frequency 
        Don-t use interval statistics -- output all intervals as is
        Mean speed is printed twice -- mean for all time nd mean run time (using RunRest threshold)
        '''
        def frameToTime(frame):
            return frame/frameRate
        
        trajectoryStats = TrajectoryStats()
        trajectoryStats.setBounds(chamber.rect.size())
        width,height = chamber.width(), chamber.height()
        
        meanX, meanY = width/2, height/2
        trajectoryStats.setCenter(meanX, meanY)
        
        trajectory = chamber.trajectory
        startFrame, endFrame = trajectory.bounds()
        # Total values
        trajectoryStats.totalDuration = frameToTime(endFrame - startFrame) # total time in seconds
        #trajectoryStats.intervalDuration = self.intervalDuration
        # Value to form run periods
        runStartTime = 0
        runLength = 0
        runDuration = 0
        lastState = 1  #1- rest, 2 - run
        
        runs=[] # List to store all runs: duration,length
        ltObject1 = None
        frame1 = None
        for frame2 in xrange(startFrame, endFrame): # Cycle for all points
            # Check for emergency abort
            # TODO: Do this
            # trying to find positive coordinates
            ltObject2 = trajectory[frame2]
            if ltObject2 is None :
                # Dismiss error frame and go to next one
                continue
            
            if ltObject1 is None : # no previous point -- store and continue
                ltObject1 = ltObject2
                frame1 = frame2
                continue
            time = frameToTime(frame2-frame1)
            if time < self.quantDuration : # Wait for quant end
                continue
            # If we are here -- we have all needed to calculate speed
            x1, y1 = ltObject1.center
            x2, y2 = ltObject2.center
            
            #hystogram[int(x2)//hystogramLevel][int(y2)//hystogramLevel]+=1
            
            length = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / scale
            speed = length / time
            # Assign current point to quadrant
            if x2 < meanX :
                xQuadrant=0
            else :
                xQuadrant=1
            if y2 < meanY :
                yQuadrant =0
            else :
                yQuadrant=1
            # Updating data
            trajectoryStats.totalLength += length
            trajectoryStats.quadrantTotalDuration[xQuadrant][yQuadrant] +=time
            trajectoryStats.quadrantTotalLength[xQuadrant][yQuadrant] +=length
            if speed >= self.runRestSpeedThreshold :
                # This is Activity
                trajectoryStats.runDuration+=time
                trajectoryStats.runLength += length
                trajectoryStats.quadrantRunDuration[xQuadrant][yQuadrant] +=time
                trajectoryStats.quadrantRunLength[xQuadrant][yQuadrant] +=length
                if lastState == 1 : # Starting new activity period
                    lastState = 2
                    runStartTime = frameToTime(frame1)
                    runLength = length  
                    runDuration = time
                    trajectoryStats.runCount +=1
                    
                else : # Previous quant was activity
                    runLength+=length
                    runDuration+=time
            else :
                # This is Rest
                if lastState == 2 : # Finished activity period
                    # Reset run
                    lastState = 1
                    #
                    # Recording information about previous run
                    runs.append([runStartTime,runDuration,runLength])
                    runStartTime = -1
                    
                    '''
                    currentTime = frameToTime(frame2-startFrame)
                    interval = int(currentTime/self.intervalDuration)+1
                    intervalStats = IntervalStats()
                    intervalStats.totalDuration = time
                    intervalStats.runDuration = runDuration
                    intervalStats.runLength = runLength
                    trajectoryStats.intervals.append(intervalStats)
                    '''
                            
            ltObject1 = ltObject2
            frame1 = frame2
            QtGui.QApplication.processEvents()
        # total output
        
        if runStartTime >=0 :
            runs.append([runStartTime,runDuration,runLength])
            
        trajectoryStats.runs = np.array(runs) # Converting to numpy array to save memory
        
        H,xedges,yedges,image=mpl.pyplot.hist2d(
            np.array(filter(lambda x: x >= 0, trajectory.cpX)),
            np.array(filter(lambda x: x >= 0, trajectory.cpY)),
            bins=40, norm=LogNorm())
        
        intensity=H.sum()
        H = H / intensity
        #print image
        #print 'H:',H
        
        
        mpl.pyplot.colorbar()
        #mpl.pyplot.show()
        mpl.pyplot.clf()
        '''
        dx=trajectory.cpX[startFrame+1:endFrame]-trajectory.cpX[startFrame:endFrame-1]
        dy=trajectory.cpY[startFrame+1:endFrame]-trajectory.cpY[startFrame:endFrame-1]
        
        mpl.pyplot.hist2d(dx,dy,
            bins=40,norm=LogNorm())
        mpl.pyplot.colorbar()
        #mpl.pyplot.show()
        mpl.pyplot.clf()
        
        sFrame=1
        dx=trajectory.cpX[startFrame+1:endFrame:sFrame]-trajectory.cpX[startFrame:endFrame-1:sFrame]
        dy=trajectory.cpY[startFrame+1:endFrame:sFrame]-trajectory.cpY[startFrame:endFrame-1:sFrame]
        
        for i in range(len(dx)-1) :
            dx0=dx[i]
            dy0=dy[i]
            
            r=np.hypot(dx0,dy0)
            if r>0.1 :
                cosPhi=dx0/r
                sinPhi=dy0/r
            
                rot=np.array([[ cosPhi,sinPhi],
                         [ -sinPhi,cosPhi]]   )
            
                dx[i],dy[i] = np.dot(rot,np.array([dx[i+1],dy[i+1]]) )
            else:
                dx[i]=0;
                dy[i]=0
            
        dx[len(dx)-1]=0
        dy[len(dy)-1]=0
            
        print dx
        print dy
            
        #mpl.pyplot.hist2d(dx,dy,bins=200,norm=LogNorm())
        binwidth=0.2
        minData=min(np.min(dx),np.min(dy))
        maxData=max(np.max(dx),np.max(dy))
        counts, xedges, yedges, Image = mpl.pyplot.hist2d(-dy,dx,bins=np.linspace(minData, maxData, int((maxData-minData)/binwidth) ),norm=LogNorm())
        
        mpl.pyplot.axes().set_aspect('equal', 'datalim')
        mpl.pyplot.ylim([-10,10])
        mpl.pyplot.xlim([-15,15])
        mpl.pyplot.colorbar()
        #mpl.pyplot.show()
        mpl.pyplot.clf()
        
        pca =PCA(n_components=10)
        #pca.fit(hist)   
        #print('Histogram:')
        #print(H)
        '''
        #print(hystogram)
        return trajectoryStats,H


#===========================================================================================================================
        
class RatRunAnalyser(QtCore.QObject):
    #            sample name 
    outString = '{:>25}; {:18.6f}; {:18.6f};  {:6.2f}; {:6.2f}; {:6.2f}; {:6.2f};  {:10.2f}; {:10.2f}; {:10.2f}; {:10.2f}; {};\n'
    #
    
    def __init__(self, errorDetector, parent=None):
        '''
        Constructor
        '''
        super(RatRunAnalyser, self).__init__(parent)    
    
    @QtCore.pyqtSlot(QtCore.QString)
    def prepareFiles(self, resultsFileName):
        self.resultsFile = open(unicode(resultsFileName), 'w')
        captionString = '                  Sample ;Record total time,s; Avg run speed,mm/s;Time:[0,0]; [0,1];  [1,0];  [1,1]; Length:[0,0];     [0,1];      [1,0];      [1,1];    FileName;\n'
        self.resultsFile.write(captionString)

      
    def closeFiles(self):
        self.resultsFile.close()
        self.resultsFile = None

    def analyseChamber(self, trajectory, sampleName, sizeX, sizeY, scale, frameRate, aviName):
        '''
        Analysing chamber
        '''
        
        def frameToTime(frame):
            return frame/frameRate
        
        startFrame, endFrame = trajectory.bounds()
        meanX = sizeX/2
        meanY = sizeY/2
        # Total values
        totalTime = frameToTime(endFrame - startFrame) # total time in seconds
        totalLength = 0 # Summary length
        
        quadrantTime = [[0,0],
                          [0,0]]  # counts in each quadrant
        quadrantLength = [[0,0],
                          [0,0]]  # counts in each quadrant
        # Interval values
        ltObject1 = None
        for frame2 in xrange(startFrame, endFrame): # Cycle for all points
            # Check for emergency abort
            '''
            if not self.analyseFromFilesRunning :
                resultsFile.write('Analysis aborted')
                return
            '''
            # trying to find positive coordinates
            ltObject2 = trajectory[frame2]
            if ltObject2 is None :
                # Dismiss error frame and go to next one
                continue
            if ltObject1 is None : # no previous point -- store and continue
                ltObject1 = ltObject2
                continue
            x1, y1 = ltObject1.center
            x2, y2 = ltObject2.center
            if x2 < meanX :
                xQuadrant=0
            else :
                xQuadrant=1
            if y2 < meanY :
                yQuadrant =0
            else :
                yQuadrant=1
            quadrantTime[xQuadrant][yQuadrant] +=1
            length = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / scale
            totalLength += length
            quadrantLength[xQuadrant][yQuadrant] +=length
            ltObject1 = ltObject2
            QtGui.QApplication.processEvents()
        # total output
        totalFrames=(endFrame - startFrame)
        quadrantTime[0][0]= quadrantTime[0][0]/totalFrames
        quadrantTime[0][1]= quadrantTime[0][1]/totalFrames
        quadrantTime[1][0]= quadrantTime[1][0]/totalFrames
        quadrantTime[1][1]= quadrantTime[1][1]/totalFrames      
        # total output
        self.resultsFile.write(self.outString.format(sampleName, totalTime, totalLength/totalTime,
             quadrantTime[0][0],quadrantTime[0][1],quadrantTime[1][0], quadrantTime[1][1], 
             quadrantLength[0][0], quadrantLength[0][1], quadrantLength[1][0], quadrantLength[1][1],aviName))
        
        
