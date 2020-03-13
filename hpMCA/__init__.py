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

# Based on code from Dioptas - GUI program for fast processing of 2D X-ray diffraction data

from __future__ import absolute_import

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

if __version__ == "0+unknown":
    __version__ = "0.1.0"

import sys
import os
import time

import PyQt5
from PyQt5 import QtCore
import pyqtgraph
from PyQt5 import QtWidgets

resources_path = os.path.join(os.path.dirname(__file__), 'resources')
#calibrants_path = os.path.join(resources_path, 'calibrants')
icons_path = os.path.join(resources_path, 'icons')
#data_path = os.path.join(resources_path, 'data')
#style_path = os.path.join(resources_path, 'style')



def main():
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
      PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    app = QtWidgets.QApplication([])

    from hpMCA.controllers.hpmca_controller import hpMCA
    app.aboutToQuit.connect(app.deleteLater)

    controller = hpMCA(app)
    controller.widget.show()

    # autoload a file, using for debugging
    #controller.openFile(filename='resources/20181010-Au-wire-50um-15deg.hpmca')
    #controller.phase_controller.add_btn_click_callback(filenames=['JCPDS/Metals/au.jcpds'])
    #controller.phase_controller.show_view()
    #controller.phase_controller.add_btn_click_callback(filenames=['JCPDS/Oxides/mgo.jcpds'])

    return app.exec_()