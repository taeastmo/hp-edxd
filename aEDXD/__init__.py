# -*- coding: utf8 -*-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''
from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

if __version__ == "0+unknown":

'''
__version__ = "0.5.0"

from aEDXD.controllers.aEDXD_controller import aEDXD_controller
import PyQt5
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
import sys

print ('__init__.py OK')
def main():


    print ('start main')
    
    print("aEDXD {}".format(__version__))
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    print('controller')
    controller = aEDXD_controller(app,1)

    app.exec_()
    del app
    