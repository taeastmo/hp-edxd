"""aEDXD.py:
   A python script program for amorphous EDXD data analysis"""

###############################################################################
#   v1.1.1:
#       1. Multi-file input at a 2Th angle is allowed
#   v1.1.2:
#       1. The spectrum normalization is done directly to be S(q),
#          not to be an I(q) profile, hence no I(q) data is saved.
#       2. Change the way to smooth the S(q) for UnivariateSpline parameter.
#          The sq_smoothing_factor is multiplied to the weight factor:
#          scipy.interploate.UnivariateSpline(x,y,w=sq_smoothing_factor*weight,
#          bbox=[None,None],k=3,s=None), where weight = 1/y_err.
#   v1.2a:
#       1. The version convention changed: Version.Revision+a:alphaa or b:beta    
#       2. Read aEDXD_input.cfg file: python dictionary syntax
#       3. aEDXD_class is separated from aEDXD_functions
#       4. Verbose analysis using aEDXD methods
#   v1.2b:
#       1. Automatically save the structure factor segments
#   v1.3:
#       1. Work with:
#               Python 2.7.9
#               Numpy 1.9.2
#               Scipy 0.15.1
#               matplotlib 1.4.3
#       2. Add new option to choose input file format
#       3. Fix a but that did not sum intensities from multiple input files
#   v2.0b:  Author: R. Hrubiak, ANL
#       1. Upgraded to Python 3.7
#       2. Changed GUI to PyQt5 and pyqtgraph
#       3. Visual peak removal via interactive plot
#       4. Improved interpolation under removed peaks 
#       4. GUI options editing / operation possible without a config file
#       6. Options/project saving  
#       7. TODO Hdf5 compatible
#       8. TODO self consistency of S(q) check
#       9. TODO Angle dispersive I(q) input
#       10.TODO plot errors
#       11. TODO in-valid config file loading crashes program
#       
#        
###############################################################################

from aEDXD.controllers.aEDXD_controller import aEDXD
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
import sys

def run():
   QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
   app = QApplication(sys.argv)
   app.aboutToQuit.connect(app.deleteLater)
   controller = aEDXD(app,1)
   return app.exec_()

if __name__ == '__main__':
   sys.exit(run())
    

