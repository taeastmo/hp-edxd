# -*- coding: utf8 -*-

# DISCLAIMER
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Principal author: R. Hrubiak (hrubiak@anl.gov)
# Copyright (C) 2018-2019 ANL, Lemont, USA



__version__ = "0.7.0"



import os

import PyQt5
import pyqtgraph as pg
from PyQt5 import QtCore

from PyQt5 import QtWidgets

import platform

import pathlib

desktop = pathlib.Path.home() / 'Desktop'


resources_path = os.path.join(os.path.dirname(__file__), 'resources')
calibrants_path = os.path.join(resources_path, 'calibrants')
icons_path = os.path.join(resources_path, 'icons')
data_path = os.path.join(resources_path, 'data')
style_path = os.path.join(resources_path, 'style')

file_settings_file = 'hpMCA_file_settings.json'
folder_settings_file='hpMCA_folder_settings.json'
defaults_settings_file='hpMCA_defaults.json'
file_naming_settings_file = 'hpMCA_file_naming_settings.json'

epics_sync = False

from pathlib import Path
home_path = str(Path.home())

def make_dpi_aware():
    _platform = platform.system()
    if _platform == 'Windows':
      if int(platform.release()) >= 8:
          import ctypes
          ctypes.windll.shcore.SetProcessDpiAwareness(True)

def main():
  
    make_dpi_aware()
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
      PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
   
    app = QtWidgets.QApplication([])

    from hpm.controllers.hpmca_controller import hpmcaController
    app.aboutToQuit.connect(app.deleteLater)

    controller = hpmcaController(app)
    controller.widget.show()

    # autoload a file, using for debugging
    pattern = os.path.normpath(os.path.join(resources_path,'20181010-Au-wire-50um-15deg.hpmca'))
    jcpds1 = os.path.normpath(os.path.join(resources_path,'au.jcpds'))
    jcpds2 = os.path.normpath(os.path.join(resources_path,'mgo.jcpds'))
    multi_spectra =  os.path.normpath( os.path.join(desktop,'dt/Guoyin/Cell2-HT/5000psi-800C'))

    #pattern = os.path.join(resources_path,'LaB6_40keV_MarCCD.chi')
    #jcpds = os.path.join(resources_path,'LaB6.jcpds')
    
    controller.file_save_controller.openFile(filename=pattern)
    #controller.multiple_datasets_controller.show_view()
    #controller.multiple_datasets_controller.widget.file_filter.setText('2nd-8000psi-500C')
    #controller.multiple_datasets_controller.add_btn_click_callback(folder=multi_spectra)
    
    #controller.phase_controller.add_btn_click_callback(filenames=[jcpds1])

    #controller.phase_controller.show_view()
    #controller.phase_controller.add_btn_click_callback(filenames=['JCPDS/Oxides/mgo.jcpds'])

    return app.exec_()


def mdc():
  
    make_dpi_aware()
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
      PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
   
    app = QtWidgets.QApplication([])

    from hpm.controllers.MultipleDatasetsController import MultipleDatasetsController
    app.aboutToQuit.connect(app.deleteLater)

    controller = MultipleDatasetsController(None)
    controller.widget.show()

    # autoload a file, using for debugging
    pattern = os.path.join(resources_path,'20181010-Au-wire-50um-15deg.hpmca')
    jcpds = os.path.join(resources_path,'au.jcpds')

    #pattern = os.path.join(resources_path,'LaB6_40keV_MarCCD.chi')
    #jcpds = os.path.join(resources_path,'LaB6.jcpds')
    
    #controller.file_save_controller.openFile(filename=pattern)
    #controller.multiple_datasets_controller.show_view()
    #controller.multiple_datasets_controller.widget.file_filter.setText('2nd-8000psi-500C')
    #controller.multiple_datasets_controller.add_btn_click_callback(folder='/Users/hrubiak/Desktop/Guoyin/Cell2-HT')
    
    #controller.phase_controller.add_btn_click_callback(filenames=[jcpds])

    #controller.phase_controller.show_view()
    #controller.phase_controller.add_btn_click_callback(filenames=['JCPDS/Oxides/mgo.jcpds'])

    return app.exec_()