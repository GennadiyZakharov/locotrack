'''
Created on 18.03.2011

@author: Gena
'''

from PyQt4.QtCore import SIGNAL

# Standard QT signals
signalClicked = SIGNAL("clicked()")
signalValueChanged = SIGNAL("valueChanged(int)")
signalStateChanged = SIGNAL("stateChanged(int)")
signalTriggered = SIGNAL("triggered()")
signalToggled = SIGNAL("toggled(bool)")

# ==== Custom signals ====
# ---- CvPlayer ----
signalCaptureFromFile = SIGNAL("captureFromFile")
signalCvPlayerCapturing = SIGNAL("CvPlayerCapturing")
signalNextFrame = SIGNAL("nextFrame")


signalAccumulate = SIGNAL("accumulate")

# ---- CvLabel ----
signalReady = SIGNAL("ready")
signalRegionSelected = SIGNAL("regionSelected")
signalEnableDnD = SIGNAL("enableDnD")


signalSetChamber = SIGNAL("setChamber")
signalSetScale = SIGNAL("setScale")
signalChangeSelection  = SIGNAL("changeSelection")
signalChambersUpdated = SIGNAL("chambersUpdated")
