#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 13.12.2010
@author: gena
'''

'''
This is main run file for locotrack program
'''
import sys
from PyQt4.QtGui import QApplication, QIcon
from os.path import join, abspath, pardir
# Add src and resources to python path
sys.path.append(abspath(join(pardir, 'src')))
sys.path.append(abspath(join(pardir, 'resources')))
# Import locotrack modules
from ltcore.consts import applicationName, applicationVersion, \
    organizationName, organizationDomain
from ltgui.ltmainwindow import LtMainWindow

def main():
    app = QApplication(sys.argv)
    app.setOrganizationName(organizationName)
    app.setOrganizationDomain(organizationDomain)
    app.setApplicationName(applicationName + ' ' + applicationVersion)
    app.setWindowIcon(QIcon(":/icon.png"))
    mainWindow = LtMainWindow()
    mainWindow.show()
    return app.exec_()

if __name__ == '__main__':
    main()
