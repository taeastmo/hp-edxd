"""multiangle.py:
   A python script program for multiangle EDXD data collection """

###############################################################################
#   v1.1.1:
#       
#        
###############################################################################

from multiangle.controllers.multiangle_controller import multiangleController
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
import sys

def run():
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    controller = multiangleController(app,1)
    return app.exec_()

if __name__ == '__main__':
    sys.exit(run())
    


