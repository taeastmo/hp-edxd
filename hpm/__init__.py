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

# Reuses a lot of code from Dioptas https://github.com/Dioptas/Dioptas



__version__ = "0.6.2"



import os


import PyQt5
import pyqtgraph
from PyQt5 import QtCore

from PyQt5 import QtWidgets




resources_path = os.path.join(os.path.dirname(__file__), 'resources')
calibrants_path = os.path.join(resources_path, 'calibrants')
icons_path = os.path.join(resources_path, 'icons')
data_path = os.path.join(resources_path, 'data')
style_path = os.path.join(resources_path, 'style')

from pathlib import Path
home_path = str(Path.home())

def main():
  
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
    au_pattern = os.path.join(resources_path,'20181010-Au-wire-50um-15deg.hpmca')
    au_jcpds = os.path.join(resources_path,'au.jcpds')
    
    controller.file_save_controller.openFile(filename=au_pattern)
    #controller.multiple_datasets_controller.show_view()
    #controller.multiple_datasets_controller.widget.file_filter.setText('2nd-8000psi-500C')
    #controller.multiple_datasets_controller.add_btn_click_callback(folder='/Users/hrubiak/Desktop/Guoyin/Cell2-HT')
    
    #controller.phase_controller.add_btn_click_callback(filenames=[au_jcpds])

    #controller.phase_controller.show_view()
    #controller.phase_controller.add_btn_click_callback(filenames=['JCPDS/Oxides/mgo.jcpds'])

    return app.exec_()
