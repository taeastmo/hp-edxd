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



import os, os.path, sys, platform, copy

from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtWidgets import QMainWindow

#qtCreatorFile = 'hpMCA.ui'
#Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
_platform = platform.system()

from hpm.widgets.hpMCA_ui import Ui_hpMCA

StyleSheet = '''
#dead_time_indicator {
    text-align: center;
    min-height: 19px;
    max-height: 19px;
    border-radius: 3px;
    background-color: #6F6F6F;
}
#dead_time_indicator::chunk {
    border-radius: 3px;
    background-color: #009688;
    margin: 1px;
    width: 5px; 
}
'''

class hpMCAWidget(QMainWindow, Ui_hpMCA):
    file_dragged_in_signal = pyqtSignal(str)
    key_signal = pyqtSignal(str)
    def __init__(self, app):
        QMainWindow.__init__(self)
        Ui_hpMCA.__init__(self)
        self.app = app
        self.setupUi(self)
        self.dead_time_indicator.setStyleSheet(StyleSheet)
        self.add_menu_items()
        self.setAcceptDrops(True)

    def closeEvent(self, QCloseEvent, *event):
        self.app.closeAllWindows()

    def add_menu_items(self):
        self.actionManualTth = QtWidgets.QAction(self)
        self.actionManualTth.setText("Set 2theta...")
        self.actionManualTth.setEnabled(False)
        self.menuControl.addAction(self.actionManualTth)
        self.actionPresets = QtWidgets.QAction(self)
        self.actionPresets.setText("Presets...")
        self.actionPresets.setEnabled(False)
        self.menuControl.addAction(self.actionPresets)

        self.actionhklGen = QtWidgets.QAction(self)
        self.actionhklGen.setText("hklGen")
        self.actionhklGen.setEnabled(False)
        #self.menuDisplay.addAction(self.actionhklGen)

    def menu_items_set_enabled(self, enabled):
        self.actionSave_As.setEnabled(enabled)
        self.actionExport_pattern.setEnabled(enabled)
        self.actionJCPDS.setEnabled(enabled)
        self.actionCalibrate_energy.setEnabled(enabled)
        self.actionCalibrate_2theta.setEnabled(enabled)
        self.actionROIs.setEnabled(enabled)
        self.actionOverlay.setEnabled(enabled)
        self.actionFluor.setEnabled(enabled)
        self.actionPressure.setEnabled(enabled)
        self.actionManualTth.setEnabled(enabled)
        self.actionPresets.setEnabled(enabled)
        self.actionhklGen.setEnabled(enabled)

    def keyPressEvent(self, e):
        sig = None
        if e.key() == Qt.Key_Up:
            sig = 'up'
        if e.key() == Qt.Key_Down:
            sig = 'down'                
        if e.key() == Qt.Key_Delete:
            sig = 'delete'
        if e.key() == Qt.Key_Right:
            sig = 'right'   
        if e.key() == Qt.Key_Left:
            sig = 'left'   
        if e.key() == Qt.Key_Backspace:
            sig = 'delete'  
        if e.key() == Qt.Key_Shift:
            sig = 'shift_press'     
         
        if sig is not None:
            self.key_signal.emit(sig)
        else:
            super().keyPressEvent(e)

    def keyReleaseEvent(self, e):
        sig = None
        if e.key() == Qt.Key_Shift:
            sig = 'shift_release' 
        if sig is not None:
            self.key_signal.emit(sig)
        else:
            super().keyPressEvent(e)

    ########################################################################################
    ########################################################################################

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls:
            if len(e.mimeData().urls()) != 1:
                e.ignore() 
            else:
                e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls:
            if len(e.mimeData().urls()) != 1:
                e.ignore() 
            else:
                e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        """
        If user drop files directly onto the widget
        File locations are stored in fname
        Emits file_dragged_in_signal with str arg fname
        :param e:
        :return:
        """
        if e.mimeData().hasUrls:
            e.setDropAction(QtCore.Qt.CopyAction)
            if len(e.mimeData().urls()) != 1:
                e.ignore() 
            else:
                e.accept()
                for url in e.mimeData().urls():   
                    fname = str(url.toLocalFile())
                self.file_dragged_in_signal.emit(fname)
        else:
            e.ignore()  

    

    



    

