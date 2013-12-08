'''
Created on 27.02.2013

@author: gena
'''
from __future__ import division
from PyQt4 import QtCore, QtGui
from os.path import basename


class AnalyseDialog(QtGui.QDialog):
    '''
    This is a simple dialog, used to select files for analysis:
      filename to store analysis results
      and list of files to analyse
    '''
    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(AnalyseDialog, self).__init__(parent)
        self.analyseFileName = QtCore.QString() # File name to save results
        self.lastDirectory = QtCore.QString('.')
        self.ltFilesList = None   # List to store input lt files
        layout = QtGui.QGridLayout()
        # analyseFile elements
        self.analyseFileEdit = QtGui.QLineEdit()
        analyseFileLabel = QtGui.QLabel('Result file name')
        layout.addWidget(analyseFileLabel,0,0)
        layout.addWidget(self.analyseFileEdit,0,1)
        browseButton = QtGui.QPushButton('Browse...')
        browseButton.clicked.connect(self.browseAnalyseFile)
        layout.addWidget(browseButton,0,2)
        # ltFileList Elements
        ltFileListLabel = QtGui.QLabel('Files to analyse:')
        layout.addWidget(ltFileListLabel,1,0)
        self.ltFilesList = QtGui.QListView()
        self.model = QtGui.QStringListModel()
        self.ltFilesList.setModel(self.model)
        layout.addWidget(self.ltFilesList,2,0,1,3)
        ltBrowseButton = QtGui.QPushButton('Browse...')
        ltBrowseButton.clicked.connect(self.ltFilesOpen)
        layout.addWidget(ltBrowseButton,3,2)
        # Ok/Close buttonbox
        self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Close | QtGui.QDialogButtonBox.Ok,
                                           accepted=self.accept,
                                           rejected=self.reject)
        
        self.validate() # 
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
    
    def clearData(self):
        self.analyseFileEdit.clear()
        self.ltFilesList = None
        self.validate()
    
    def browseAnalyseFile(self):
        '''
        Select one file to save analyse results
        '''
        formats = ["*.%s" % unicode(videoFormat).lower() \
                   for videoFormat in ('txt', 'csv')]
        # Setting last user dir
        # Executing standard open dialog
        self.analyseFileName = QtGui.QFileDialog.getSaveFileName(self,
                        "Choose file to save results",
                        self.lastDirectory, "Data files (%s)" % " ".join(formats))
        if not self.analyseFileName.isEmpty() :
            fileInfo = QtCore.QFileInfo(self.analyseFileName)
            self.lastDirectory = fileInfo.absolutePath()
        self.analyseFileEdit.setText(self.analyseFileName)
        self.validate()
        
    def ltFilesOpen(self):
        '''
        Select list of lt files to analyse
        '''
        dialog = QtGui.QFileDialog(self, 'Open input Files', 
                                   self.lastDirectory)
        dialog.setFileMode(QtGui.QFileDialog.ExistingFiles);
        dialog.setNameFilter("Locotrack chamber (*.lt1)")          
        if dialog.exec_() :
            # Display selected list
            self.ltFilesList = dialog.selectedFiles()
            baseNames = [basename(unicode(fileName)) for fileName in self.ltFilesList]
            self.model.setStringList(baseNames)
            self.lastDirectory = dialog.directory().absolutePath ()
        else :
            self.ltFilesList = None
        self.validate() 
        
    def validate(self):
        '''
        Validate input data and enable Ok button if all fine
        '''
        flag = (self.ltFilesList is not None) and (not self.analyseFileName.isEmpty())
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(flag)