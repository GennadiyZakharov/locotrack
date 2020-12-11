locotrack
=========

locotrack is a simple program to analyse locomotion behaviour of animals.

It can detect objects on video records, record trajectory for each object 
and calculate some motion statistics

Locotrack Installation
======================

The current version is rather outdated, so installing all dependencies could be painful.
Currently, I'm working on transferring application to new versions of QT and OpenCV

## Installing python and nesessary packages

### For Linux

Both for Windows and linux I suggest using Anaconda distribution
 * Install CONDA installer for python 2.7 (32bit) from here: https://www.continuum.io/downloads#windows
 * Ensure that conda  is in your system path
 * Create environment for python2 and install all required packages
   - `conda create --name py2 python=2.7`
   - `conda activate py2`
   - `conda install numpy scipy matplotlib`
   - `conda install -c terradue pyqt4`
   - `conda install -c menpo opencv`
 * Install GTK library for OpenCV: sudo apt install libgtk2.0-dev

 
 * Download Windows PyQt4 PyQt4‑4.11.4‑cp27‑cp27m‑win_amd64.whl from here: http://www.lfd.uci.edu//~gohlke/pythonlibs/#pyqt4 
 * Download Windows OpenCV 2 package  from here: https://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv
 * Install PyQt4 and OpenCV via pip 
  - `pip install opencv_python-2.4.13.2-cp27-cp27m-win32.whl`
  - `pip install PyQt4‑4.11.4‑cp27‑cp27m‑win32.whl`

##Installing Locotrack

* download or clone from git latest locotrack code
* change directory to locorack
* run locotrack.py
