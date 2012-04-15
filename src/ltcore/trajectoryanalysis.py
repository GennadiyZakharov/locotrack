# -*- coding: utf-8 -*-
'''
Created on 07.04.2012

@author: gena
'''


from __future__ import division
from math import sqrt

from PyQt4 import QtCore

totalActivityName = "0-TotalActivity_.csv"
activityName = "1-TotalActivity.csv"
restName = "2-Rest.csv"
runName = "3-Run.csv"
graphName = ".graph.txt"

class RunRestAnalyser(QtCore.QObject):
    '''
    Classic analyser, based on run/rest periods
    '''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(RunRestAnalyser, self).__init__(parent)
        self.quantDuration = 1.0
        self.intervalDuration = 50.0
        self.speedTreshold = 0.28
        self.errorTreshold = 5.0
        
    def readPoint(self):
        line = self.trajectoryFile.readline()
        if not line :
            return None
        frameNumber, x, y = [float(n) for n in line.split()]
        return (frameNumber / self.frameRate, x / self.scale, y / self.scale)
    
    def activityString(self, interval, activity, runFreq):
        return '{0:10}; {1:5}; {2:10}; {3:5}; {4:18.6f}; {5:18.6f};\n'.format(
            self.line, self.gender, self.condition, interval, 
            activity, runFreq)
    
    def restString(self, interval, restDuration):
        return '{0:10}; {1:5}; {2:10}; {3:5}; {4:18.6f};\n'.format(
            self.line, self.gender, self.condition,
            interval, restDuration)
    
    def runString(self, interval, runDuration, runLength):
        return '{0:10}; {1:5}; {2:10}; {3:5}; {4:18.6f}; {5:18.6f}; {6:18.6f};\n'.format(
            self.line, self.gender, self.condition,interval, 
            runDuration, runLength, runLength/runDuration)
    
    def analyse(self, fileName):
        '''
        Do analysis of one track
        '''
        #
        print "Starting analysis of file"+fileName
        
        self.totalActivityFile = open(totalActivityName,'a')
        self.activityFile = open(activityName,'a')
        self.restFile = open(restName,'a')
        self.runFile = open(runName,'a')
        self.graphFile = open(fileName+graphName,'w') 
        #
        self.trajectoryFile = open(fileName, 'r')
        if self.trajectoryFile is None :
            print "Error opening file"
            return
        self.trajectoryFile.readline()
        left, top = [int(x) for x in self.trajectoryFile.readline().split()]
        width, height = [int(x) for x in self.trajectoryFile.readline().split()]
        self.scale = float(self.trajectoryFile.readline())
        self.frameRate = float(self.trajectoryFile.readline())
        self.line = self.trajectoryFile.readline()
        self.gender = self.trajectoryFile.readline()
        self.condition = self.trajectoryFile.readline()
        self.trajectoryFile.readline()
        # 
        lastState = -1 # стостяние движения личинки
        # //0 - покой, 1 - движение, -1 - не определено
        secondPoint = self.readPoint()
        
        errorCount = 0
        intervalNumber = 0
        totalRunDuration = 0.0
        totalRunCount = 0
        #
        restDuration = 0.0
        runDuration = 0.0
        runLen = 0.0
        runStart = -1
        restStart = -1
        # Main cycle -- input file
        while True : 
            # Resetting Interval Values
            intervalDuration = 0.0
            intervalRestDuration = 0.0
            intervalRunDuration = 0.0
            intervalRunCount = 0
            # interval cycle
            while True : 
                firstPoint = secondPoint
                
                intervalNumber +=1
                #print "Interval "+str(intervalNumber)
                # Reading Next Point according to quant duration
                while True :
                    secondPoint = self.readPoint()
                    QtCore.QCoreApplication.processEvents()
                    if secondPoint is None :
                        # Input File ended
                        break
                    if secondPoint[1] < 0 : # This was error 
                        errorCount += 1
                        print "Error -- no object found"
                        continue
                    quantDuration = secondPoint[0] - firstPoint[0]
                    if quantDuration >= self.quantDuration :
                        quantLen = sqrt((secondPoint[1] - firstPoint[1]) ** 2 + 
                            (secondPoint[2] - firstPoint[2]) ** 2)
                        speed = quantLen / quantDuration
                        if speed > self.errorTreshold :
                            errorCount += 1
                            print 'Error -- speed too much'
                            continue
                        else :
                            break 
                #
                if secondPoint is None :
                    break
                # Calculating speed by quant
                intervalDuration += quantDuration
                
                self.graphFile.write("{0:10.2f} {1:12.4f}\n".format(
                    secondPoint[0], quantLen / quantDuration))
                 
                if speed > self.speedTreshold :
                    #//личинка двигалась на данном кванте
                    runDuration += quantDuration #//добавляет этот квант к побежке
                    runLen += quantLen
                    if lastState == 0 :
                        #//кончился предыдущий период покоя закончился -- записываем
                        intervalRestDuration += restDuration #//суммарное время отдыха
                        #//записываем в выходной файл данные об отдыхе
                        string = self.restString(restStart, restDuration)
                        self.restFile.write(string)
                        # Обнуляем
                        restDuration = 0
                              
                    if (lastState== -1) or (lastState==0) : # начали анализировать движение
                        lastState = 1 # поставили анализируемый период
                        intervalRunCount+=1 # на данном интервале началась еще одна побежка
                        totalRunCount+=1
                        runStart = intervalNumber # запомнили, на каком интервале началась побежка
                else :
                    # личинка не двигалась
                    restDuration += quantDuration
                    if lastState == 1 :
                        # кончилась побежка - -записываем
                        intervalRunDuration += runDuration 
                        totalRunDuration += runDuration
                        # записываем в выходной файл данные о побежке
                        string = self.runString(runStart, runDuration, runLen)
                        self.runFile.write(string)
                        runDuration = 0
                        runLen = 0
                    if (lastState== -1) or (lastState==1) : # начали анализировать покой
                        lastState = 0 #; // поставили анализируемый период
                        restStart = intervalNumber #запомнили, на каком интервале начался период покоя
    
                if secondPoint[0] >= self.intervalDuration*intervalNumber : 
                    #; // закончилась обработка интервала
                    break
                # Writing interval activity index and run count
                string = self.activityString(intervalNumber, 
                         intervalRunDuration/intervalDuration, 100*intervalRunCount/intervalDuration)
                self.activityFile.write(string)
            if secondPoint is None :
                break
            
        self.trajectoryFile.close()
        self.activityFile.close()
        self.runFile.close()
        self.restFile.close()
        self.graphFile.close()
        
        self.totalActivityFile = open(totalActivityName,'w')
        string = self.activityString(-1, 
                         totalRunDuration/firstPoint[0], 100*totalRunCount/firstPoint[0])
        self.totalActivityFile.write(string)
        self.totalActivityFile.close()
        print 'Line {0}, errors:{1}'.format(fileName, errorCount)