'''
Created on 18.03.2011

@author: Gena
'''

from PyQt4 import QtGui

def createAction(target, text, shortcut=None, icon=None,    
                 tip=None, checkable=False):
    '''
    Create action with text, icon, e.t.c., owned by target
    '''
    action = QtGui.QAction(text, target)
    if shortcut is not None:
        action.setShortcut(shortcut)
    if icon is not None:
        action.setIcon(QtGui.QIcon(":/{}.png".format(icon)))
    if tip is not None:
        action.setToolTip(tip)
        action.setStatusTip(tip)
    if checkable:
        action.setCheckable(True)
    return action

def addActions(target, actions):
    '''
    Add all actions to the QObject target
    '''
    for action in actions:
        if action is None:
            target.addSeparator()
        else:
            target.addAction(action)


