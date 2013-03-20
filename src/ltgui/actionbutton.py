'''
Created on 11.03.2013

@author: gena
'''
from PyQt4 import QtGui

class ActionButton(QtGui.QPushButton):
    '''
    This is QPushButton subclass, associated with action
    It is something like QToolButton, but with text
    '''

    def __init__(self, action, parent=None):
        '''
        Constructor
        '''
        super(ActionButton, self).__init__(parent)
        # Setting text and icon from QAction
        self.action = action
        self.setText(action.text())
        self.setIcon(action.icon())
        action.changed.connect(self.updateStatus)
        # Making connections
        if action.isCheckable():
            self.setCheckable(True)
            action.toggled.connect(self.setChecked)
            self.toggled.connect(action.setChecked)
        else :
            self.clicked.connect(action.trigger)
            
    def updateStatus(self):
        '''
        Update button properties, when action changed
        '''
        self.setEnabled(self.action.isEnabled())