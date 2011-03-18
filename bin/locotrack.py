#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 13.12.2010

@author: gena
'''
import sys

from PyQt4.QtGui import QApplication,QIcon

from os.path import join, abspath, pardir
sys.path.append(abspath(join(pardir, 'src')))
sys.path.append(abspath(join(pardir, 'resources')))

from ltgui.ltmainwindow import LtMainWindow


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("Qtrac Ltd.")
    app.setOrganizationDomain("qtrac.eu")
    app.setApplicationName("LocoTrack")
    app.setWindowIcon(QIcon(":/icon.png"))
    #mainWindow = LtMainWindow()
    #mainWindow.show()
    return app.exec_()

if __name__ == '__main__':
    main()