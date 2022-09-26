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



import os, os.path, sys, platform, copy

from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QInputDialog, QMessageBox, QErrorMessage
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from epics.clibs import *  # makes sure dlls are included in the exe

from hpm.models.mcaModel import MCA
from hpm.models.epicsMCA import epicsMCA


from hpm.widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog
from hpm.widgets.eCalWidget import mcaCalibrateEnergy
from hpm.widgets.TthCalWidget import mcaCalibrate2theta
from hpm.widgets.xrfWidget import xrfWidget
from xrda.widgets.xrdaWidget import xrdaWidget


from hpm.controllers.PhaseController import PhaseController
from hpm.controllers.mcaPlotController import plotController
from hpm.controllers.RoiController import RoiController
from hpm.controllers.OverlayController import OverlayController

from hpm.controllers.FileSaveController import FileSaveController
from hpm.controllers.DisplayPrefsController import DisplayPreferences
#from hpm.controllers.hklGenController import hklGenController

import utilities.hpMCAutilities as mcaUtil
from utilities.HelperModule import increment_filename

from epics import PV

Theme = 1   # app style 0=windows 1=dark 
from .. import style_path

class xrdaController(QObject):
    key_signal = pyqtSignal(str)
    
    def __init__(self, app):
        super().__init__()
        self.app = app  # app object
        global Theme
        self.Theme = Theme
        self.style_path = style_path
        self.setStyle(self.Theme)
        self.widget = xrdaWidget(app) 

        self.file_options = mcaUtil.restore_file_settings('hpMCA_file_settings.json')

        self.make_prefs_menu()  # for mac
        
    def create_connections(self):
        ui = self.widget
        ui.key_signal.connect(self.key_sig_callback)
        ui.actionExit.triggered.connect(self.widget.close)
        ui.actionAbout.triggered.connect(self.about_module)

    def make_prefs_menu(self):
        _platform = platform.system()
        if _platform == "Darwin":    # macOs has a 'special' way of handling preferences menu
            # TODO upgrade the preferences menu
            self.pact = QtWidgets.QAction('Preferences', self.app)
            self.pact.triggered.connect(self.preferences_module)
            self.pact.setMenuRole(QtWidgets.QAction.PreferencesRole)
            self.pmenu = QtWidgets.QMenu('Preferences')
            self.pmenu.addAction(self.pact)
            menu = self.widget.menuBar()
            menu.addMenu(self.pmenu)

    def preferences_module(self, *args, **kwargs):
        [ok, file_options] = mcaUtil.mcaFilePreferences.showDialog(self.widget, self.file_options) 
        if ok :
            self.file_options = file_options
            #if self.mca_controller.mca != None:
            #    self.mca_controller.mca.file_settings = file_options
            mcaUtil.save_file_settings(file_options)

    def about_module(self):
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Information)
        self.msg.setText('This program was written by R. Hrubiak')
        self.msg.setInformativeText('More info to come...')
        self.msg.setWindowTitle('About')
        self.msg.setDetailedText('The details are as follows:')
        self.msg.setStandardButtons(QMessageBox.Ok)
        self.msg.show()


    def key_sig_callback(self, sig):
        if sig == 'right' :
            self.roi_action('next')
        if sig == 'left' :
            self.roi_action('prev')
        if sig == 'delete' :
            self.roi_action('delete')
        if sig == 'shift_press' :
            self.zoomPan(1)
        if sig == 'shift_release' :
            self.zoomPan(0)  
            
  
    
    def closeEvent(self, QCloseEvent, *event):
        self.app.closeAllWindows()

    ########################################################################################
    ########################################################################################


    def update_titlebar(self):
        name = self.mca.name
        if name != '':
            name += ' - '
        self.widget.setWindowTitle(name + u'hpMCA')



    def envs_updated_callback(self, envs):
        #print(envs)
        pass

  
    ########################################################################################
    ########################################################################################    

    def setStyle(self, Style):
        #print('style:  ' + str(Style))
        if Style==1:
            WStyle = 'plastique'
            file = open(os.path.join(self.style_path, "stylesheet.qss"))
            stylesheet = file.read()
            self.app.setStyleSheet(stylesheet)
            file.close()
            self.app.setStyle(WStyle)
        else:
            WStyle = "windowsvista"
            self.app.setStyleSheet(" ")
            #self.app.setPalette(self.win_palette)
            self.app.setStyle(WStyle)
      
        
    ########################################################################################
    ########################################################################################
