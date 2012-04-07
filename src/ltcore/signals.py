'''
Created on 18.03.2011

@author: Gena

This module holds collection of all signals, used in project
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
signalClearChamber = SIGNAL("clearChamber")
signalSetScale = SIGNAL("setScale")
signalChangeSelection  = SIGNAL("changeSelection")
signalChambersUpdated = SIGNAL("chambersUpdated")

signalWriteTrajectory = SIGNAL("writeTrajectory")
signalAnalyseTrajectory = SIGNAL("analyseTrajectory")