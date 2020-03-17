# -*- coding: utf8 -*-

__version__ = "0.5.0"

import sys
import os
import time

import PyQt5
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets



resources_path = os.path.join(os.path.dirname(__file__), 'resources')
calibrants_path = os.path.join(resources_path, 'calibrants')
icons_path = os.path.join(resources_path, 'icons')
data_path = os.path.join(resources_path, 'data')
style_path = os.path.join(resources_path, 'style')

def main():
    
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    from axd.controllers.aEDXD_controller import aEDXDController
    controller = aEDXDController(app,1)

    app.exec_()
    del app
    