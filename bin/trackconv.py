#!/usr/bin/env python
"""
This program is used to convert
tracks from old format to new one
"""

import sys,os
from PyQt4 import QtCore,QtGui

class MyWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(MyWindow, self).__init__(parent)
        # Setting last user dir
        self.openButton = QtGui.QPushButton('Open Directory')
        self.openButton.clicked.connect(self.convertDir)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.openButton)
        self.setLayout(layout)
        
    def convertDir(self):
        dirName = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
        if dirName == '' :
            return
        dirList = os.listdir(dirName)
        dirList.sort()
        for fileName in dirList :
            fullName = os.path.join(dirName, fileName)
            if not os.path.isdir(fullName) and fileName[-3:] == 'lt1' :
                self.convertFile(fullName,fullName[:-3]+'conv.lt1')
        
    def convertFile(self, input,output):
        if '.conv.' in input :
            return
        print 'Converting',input,output
        inputFile = open(input)
        outputFile = open(output,'w')
        for i in range(6) :
            outputFile.write(inputFile.readline())
        outputFile.write('60\n')
        outputFile.write('Trajectory:\n')
        inputFile.readline()
        inputFile.readline()
        trajectory = [elem for elem in inputFile.read().split('\n') if elem.strip() !='']
        first = trajectory[0].split()[0]
        last =  trajectory[-1].split()[0]
        outputFile.write('{} {}\n'.format(first, last))
        outputFile.write('     Frame                  X                  Y\n')
        for line in trajectory :
            outputFile.write(line)

def main():
    
    # Executing standard open dialog
    app = QtGui.QApplication(sys.argv)
    app.setOrganizationName("I.P. Pavlov Physiology Institute")
    app.setOrganizationDomain("infran.ru")
    app.setApplicationName("LocoTrack")
    #app.setWindowIcon(QIcon(":/icon.png"))
    w = MyWindow()
    w.resize(250, 150)
    w.move(300, 300)
    w.setWindowTitle('LtTraj converter')
    w.show()
    return app.exec_()
    
if __name__ == '__main__':
    main()
