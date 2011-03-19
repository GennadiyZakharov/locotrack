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

# ==== Custom signals ====
# ---- CvPlayer ----
signalCaptureFromFile = SIGNAL("captureFromFile")
signalCvPlayerCapturing = SIGNAL("CvPlayerCapturing")
signalNextFrame = SIGNAL("nextFrame")
signalAccumulate = SIGNAL("accumulate")

# ---- CvLabel ----
signalRegionSelected = SIGNAL("regionSelected")