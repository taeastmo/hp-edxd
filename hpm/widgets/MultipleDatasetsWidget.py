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

from functools import partial
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5 import QtWidgets, QtCore
import copy
import pyqtgraph as pg
from hpm.widgets.CustomWidgets import FlatButton, DoubleSpinBoxAlignRight, VerticalSpacerItem, NoRectDelegate, \
    HorizontalSpacerItem, ListTableWidget, VerticalLine, DoubleMultiplySpinBoxAlignRight


class MultiSpectraWidget(QtWidgets.QWidget):

    color_btn_clicked = QtCore.pyqtSignal(int, QtWidgets.QWidget)
    #env_btn_clicked = QtCore.pyqtSignal(int)
    show_cb_state_changed = QtCore.pyqtSignal(int, int)
    pv_item_changed = QtCore.pyqtSignal(int, str)
    widget_closed = QtCore.pyqtSignal()
    key_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self._layout = QtWidgets.QVBoxLayout()  
        self.setWindowTitle('Multiple spectra view')
        self.button_widget = QtWidgets.QWidget(self)
        self.button_widget.setObjectName('multispectra_control_button_widget')
        self._button_layout = QtWidgets.QHBoxLayout()
        self._button_layout.setContentsMargins(0, 0, 0, 0)
        self._button_layout.setSpacing(6)
        self.add_btn = FlatButton('Add')
        self.edit_btn = FlatButton('Edit')
        self.delete_btn = FlatButton('Delete')
        self.clear_btn = FlatButton('Clear')
        self.show_fit_btn = FlatButton('Show fit')
        self.pressure_btn = FlatButton('Pressure')
        self.save_peaks_btn = FlatButton('Save List')

        self._button_layout.addWidget(self.add_btn)
        self._button_layout.addWidget(self.edit_btn)
        self._button_layout.addWidget(self.delete_btn)
        self._button_layout.addWidget(self.clear_btn)
        self._button_layout.addWidget(self.show_fit_btn)
        self._button_layout.addWidget(self.pressure_btn)
        self._button_layout.addWidget(self.save_peaks_btn)

        self.button_widget.setLayout(self._button_layout)
        self._layout.addWidget(self.button_widget)
        self._body_layout = QtWidgets.QHBoxLayout()
        self.make_img_plot()
        self.plot_widget = self.win
        self._body_layout.addWidget(self.plot_widget)
        self._layout.addLayout(self._body_layout)

        

        self.setLayout(self._layout)

        self.style_widgets()
        self.env_show_cbs = []
        self.pv_items = []
        self.index_items = []
        self.resize(300,615)
      
    def make_img_plot(self):
        ## Create window with GraphicsView widget
        self.win = pg.GraphicsLayoutWidget(self)
        self.view = self.win.addViewBox()
        ## lock the aspect ratio so pixels are always square
        self.view.setAspectLocked(False)
        ## Create image item
        self.img = pg.ImageItem(border='w')
        self.img.setScaledMode()
        self.view.addItem(self.img)

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
        if sig is not None:
            self.key_signal.emit(sig)
        else:
            super().keyPressEvent(e)

    

    def style_widgets(self):
    
        self.setStyleSheet("""
            #env_control_button_widget FlatButton {
                min-width: 90;
            }
        """)


    def closeEvent(self, event):
        # Overrides close event to let controller know that widget was closed by user
        self.widget_closed.emit()
        


    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.raise_()

  
