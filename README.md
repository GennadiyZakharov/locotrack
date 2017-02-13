locotrack
=========

locotrack is a simple program to analyse locomotion behaviour of animals.

It can detect objects on video records, record trajectory for each object 
and calculate some motion statistics

Locotrack 

Installation
============

## Installing python and nesessary packages


###Linux

Since python usually installed by default in almost all linux distributions one only need to install following packages:
numpy, scipy, PyQt4, matplotlib, opencv
* For Ubuntu 14.04 and 16.04
- `sudo apt install python-numpy python-scipy python-matplotlib python-opencv python-qt4`

 

###Windows

For Windows I suggest using Anaconda distribution
 * Install Anaconda distribution for python 2.7 (32bit) from here: https://www.continuum.io/downloads#windows
 * Ensure that python is in your system path
 * Download Windows PyQt4 PyQt4‑4.11.4‑cp27‑cp27m‑win32.whl from here: http://www.lfd.uci.edu//~gohlke/pythonlibs/#pyqt4 
 * Download Windows opencv package opencv_python-2.4.13.2-cp27-cp27m-win32.whl from here: http://www.lfd.uci.edu/\~gohlke/pythonlibs/#opencv
 * Install PyQt4 and OpenCV via pip 
  - `pip install opencv_python-2.4.13.2-cp27-cp27m-win32.whl`
  - `pip install PyQt4‑4.11.4‑cp27‑cp27m‑win32.whl`
##Installing Locotrack

* download or clone from git latest locotrack code
* change directory to locorack
* run locotrack.py
