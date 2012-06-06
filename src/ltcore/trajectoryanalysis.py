# -*- coding: utf-8 -*-
'''
Created on 07.04.2012

@author: gena
'''


from __future__ import division
from math import sqrt
import os

from PyQt4 import QtCore, QtGui

totalActivityName = "0-TotalActivity.csv"
activityName = "1-Activity.csv"
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
        self.intervalDuration = 300.0
        self.speedTreshold = 0.28
        self.errorTreshold = 5.0
        
    def readPoint(self):
        line = self.trajectoryFile.readline()
        if not line :
            print line
            return None
        frameNumber, x, y = [float(n) for n in line.split()]
        self.trackImage.setPixel(int(x), int(y), 0)
        return (frameNumber / self.frameRate, x / self.scale, y / self.scale)
    
    def activityString(self, interval, activity, runFreq, runSpeed):
        return '{0:>25}; {1:5}; {2:18.6f}; {3:18.6f}; {4:18.6f};\n'.format(
            self.sampleName, interval,
            activity, runFreq, runSpeed)
    
    def restString(self, interval, restDuration):
        return '{0:>25}; {1:5}; {2:18.6f};\n'.format(
            self.sampleName,
            interval, restDuration)
    
    def runString(self, interval, runDuration, runLength):
        return '{0:>25}; {1:5}; {2:18.6f}; {3:18.6f}; {4:18.6f};\n'.format(
            self.sampleName, interval,
            runDuration, runLength, runLength / runDuration)
        
    def setErrorTreshold(self, value):
        self.errorTreshold = value
        
    def setRunRestTreshold(self, value):
        self.speedTreshold = value
    def setIntervalDuration(self, value):
        self.intervalDuration = value
    
    def analyseDir(self, dirName):
        dirList = os.listdir(dirName)
        dirList.sort()
        for fileName in dirList :
            fullName = os.path.join(dirName, fileName)
            if not os.path.isdir(fullName) and fileName[-3:] == 'lt1' :
                self.analyseFile(fullName, dirName)
        '''
        for dir, dirnames, filenames in os.walk(dirName):
            for filename in filenames:
                print filename
                if filename[-3:] == 'lt1' :
                    self.analyseFile(os.path.join(dirName, filename), dirName)
        '''
    def openOutputFile(self, name, captionString):
        if os.path.isfile(name) :
            mode = 'a'
        else :
            mode = 'w'
        outFile = open(name, mode)
        if mode == 'w' :
            outFile.write(captionString)
        return outFile

    def analyseFile(self, fileName, dirName):
        '''
        Do analysis of one track
        '''
        #
        print "Starting analysis of file " + fileName
        baseName = os.path.splitext(fileName)[0]

        print baseName
        self.totalActivityFile = self.openOutputFile(os.path.join(dirName, totalActivityName),
            '                   Sample;   None;           Activity;            RunFreq(1/min);    RunSpeed;\n')                          
        self.activityFile = self.openOutputFile(os.path.join(dirName, activityName),
            '                   Sample;   Int;           Activity;            RunFreq(1/min);    RunSpeed;\n')
        self.restFile = self.openOutputFile(os.path.join(dirName, restName),
            '                   Sample;   Int;           RestTime;\n')
        self.runFile = self.openOutputFile(os.path.join(dirName, runName),
            '                   Sample;   Int;            RunTime;             RunLen;           RunSpeed;\n')
        #self.graphFile = open(fileName + graphName, 'w')
        self.errorFile = open(baseName + '.err', 'w') 
        #
        self.trajectoryFile = open(fileName, 'r')
        if self.trajectoryFile is None :
            print "Error opening file"
            return
        self.trajectoryFile.readline()
        self.left, self.top = [int(x) for x in self.trajectoryFile.readline().split()]
        width, height = [int(x) for x in self.trajectoryFile.readline().split()]
        self.scale = float(self.trajectoryFile.readline())
        self.frameRate = float(self.trajectoryFile.readline())
        self.sampleName = self.trajectoryFile.readline().rstrip()
        self.trajectoryFile.readline()
        self.trajectoryFile.readline()
        #
        self.trackImage = QtGui.QImage(width, height, QtGui.QImage.Format_Indexed8)
        colorTable = [QtGui.qRgb(i, i, i) for i in xrange(256)]
        self.trackImage.setColorTable(colorTable)
        self.trackImage.fill(255)
        # 
        lastState = -1 # стостяние движения личинки
        # //0 - покой, 1 - движение, -1 - не определено
        secondPoint = self.readPoint()
        # Store start time
        startTime = secondPoint[0]
        
        errorCount = 0
        intervalNumber = 1
        # Total parameters by all record length
        totalRunDuration = 0.0
        totalRunCount = 0
        totalRunLen = 0.0
        # This is variables to calculate run/rest 
        restDuration = 0.0
        runDuration = 0.0
        runLen = 0.0
        runStart = -1
        restStart = -1
        # Main cycle -- input file
        while True : 
            # Resetting Interval Values
            intervalDuration = 0.0
            intervalRunDuration = 0.0
            intervalRunCount = 0
            intervalRunLen = 0.0
            print "interval started " + str(intervalNumber)
            # interval cycle
            while True : 
                firstPoint = secondPoint
                
                # Reading Next Point according to quant duration
                while True :
                    secondPoint = self.readPoint()
                    QtCore.QCoreApplication.processEvents()
                    if secondPoint is None :
                        # Input File ended
                        break
                    quantDuration = secondPoint[0] - firstPoint[0]
                    # Checking if it is enough to quant 
                    if quantDuration < self.quantDuration :
                        continue
                    if secondPoint[1] < 0 : # This was error 
                        errorCount += 1
                        self.errorFile.write("{0:5} Error {1:3} -- no object found\n".format(secondPoint[0], errorCount))
                        continue
                    quantLen = sqrt((secondPoint[1] - firstPoint[1]) ** 2 + 
                            (secondPoint[2] - firstPoint[2]) ** 2)
                    
                    speed = quantLen / quantDuration
                    if speed > self.errorTreshold :
                        errorCount += 1
                        self.errorFile.write('{0:5} Error {1:3} -- speed too much\n'.format(secondPoint[0], errorCount))
                        continue
                    else :
                        break 
                #
                if secondPoint is None :
                    break
                #print 'readed quant '+str(quantDuration)
                # Calculating speed by quant
                intervalDuration += quantDuration
                totalRunLen += quantLen
                #print 'intduration',intervalDuration
                '''
                self.graphFile.write("{0:10.2f} {1:12.4f}\n".format(
                    secondPoint[0], quantLen / quantDuration))
                '''
                if speed > self.speedTreshold :
                    #//личинка двигалась на данном кванте
                    runDuration += quantDuration #//добавляет этот квант к побежке
                    intervalRunDuration += quantDuration
                    totalRunDuration += quantDuration
                    runLen += quantLen
                    intervalRunLen += quantLen
                    if lastState == 0 :
                        #//кончился предыдущий период покоя закончился -- записываем
                        #//записываем в выходной файл данные об отдыхе
                        string = self.restString(restStart, restDuration)
                        self.restFile.write(string)
                        # Обнуляем
                        restDuration = 0
                              
                    if (lastState == -1) or (lastState == 0) : # начали анализировать движение
                        lastState = 1 # поставили анализируемый период
                        intervalRunCount += 1 # на данном интервале началась еще одна побежка
                        totalRunCount += 1
                        runStart = intervalNumber # запомнили, на каком интервале началась побежка
                else :
                    # личинка не двигалась
                    restDuration += quantDuration
                    if lastState == 1 :
                        # кончилась побежка - -записываем 
                        # записываем в выходной файл данные о побежке
                        string = self.runString(runStart, runDuration, runLen)
                        self.runFile.write(string)
                        runDuration = 0
                        runLen = 0
                    if (lastState == -1) or (lastState == 1) : # начали анализировать покой
                        lastState = 0 #; // поставили анализируемый период
                        restStart = intervalNumber #запомнили, на каком интервале начался период покоя
    
                if intervalDuration >= self.intervalDuration : 
                    #; // закончилась обработка интервала
                    print 'time {0}, int {1} dur {2} ended'.format(secondPoint[0], intervalNumber, intervalDuration)
                    string = self.activityString(intervalNumber,
                            intervalRunDuration / intervalDuration, 60 * intervalRunCount / intervalDuration,
                            intervalRunLen / intervalRunDuration if intervalRunDuration > 0.1 else 0)
                    self.activityFile.write(string)
                    intervalNumber += 1 
                    break
            # Writing interval activity index and run count
            if secondPoint is None :
                break
        
        self.trajectoryFile.close()
        self.activityFile.close()
        self.runFile.close()
        self.restFile.close()
        #self.graphFile.close()
        self.errorFile.close()
        if errorCount == 0 :
            os.remove(baseName + '.err')
        self.trackImage.save(baseName + '.png', format='PNG')
        #self.totalActivityFile = open(totalActivityName,'w')
        totalTime = firstPoint[0] - startTime
        string = self.activityString(-1,
                         totalRunDuration / totalTime, 60 * totalRunCount / totalTime,
                         totalRunLen / totalTime)
        self.totalActivityFile.write(string)
        self.totalActivityFile.close()
        print 'file {}, length:{}, errors:{}'.format(fileName, totalTime, errorCount)
        
