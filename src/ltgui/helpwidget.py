'''
Created on 09.03.2013

@author: gena
'''
    
from PyQt4.QtCore import (QUrl, Qt, SIGNAL, SLOT)
from PyQt4.QtGui import (QAction, QApplication, QDialog, QIcon,
        QKeySequence, QLabel, QTextBrowser, QToolBar, QVBoxLayout)
import imagercc


class HelpWidget(QDialog):

    def __init__(self, page, parent=None):
        super(HelpWidget, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setAttribute(Qt.WA_GroupLeader)

        backAction = QAction(QIcon(":/back.png"), "&Back", self)
        backAction.setShortcut(QKeySequence.Back)
        homeAction = QAction(QIcon(":/home.png"), "&Home", self)
        homeAction.setShortcut("Home")
        self.pageLabel = QLabel()

        toolBar = QToolBar()
        toolBar.addAction(backAction)
        toolBar.addAction(homeAction)
        toolBar.addWidget(self.pageLabel)
        self.textBrowser = QTextBrowser()

        layout = QVBoxLayout()
        layout.addWidget(toolBar)
        layout.addWidget(self.textBrowser, 1)
        self.setLayout(layout)

        backAction.triggered.connect(self.textBrowser.backward)
        homeAction.triggered.connect(self.textBrowser.home)
        self.textBrowser.sourceChanged.connect(self.updatePageTitle)

        self.textBrowser.setSearchPaths([":/help"])
        self.textBrowser.setSource(QUrl(page))
        self.resize(400, 600)
        self.setWindowTitle("{0} Help".format(
                QApplication.applicationName()))


    def updatePageTitle(self):
        self.pageLabel.setText(self.textBrowser.documentTitle())


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = HelpWidget("index.html")
    form.show()
    app.exec_() 