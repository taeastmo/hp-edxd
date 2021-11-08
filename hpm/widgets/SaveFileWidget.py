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


class SaveFileWidget(QtWidgets.QWidget):

    
    def __init__(self):
        super().__init__()
        self._layout = QtWidgets.QVBoxLayout()  
        self.setWindowTitle('Save File')
        self.resize(550,300)
        
        self.grid_layout = QtWidgets.QGridLayout()

        # Field Names
        self.grid_layout.addWidget(QtWidgets.QLabel('File path'),1,0)

        self.grid_layout.addWidget(QtWidgets.QLabel('File name'),3,0)
        self.grid_layout.addWidget(QtWidgets.QLabel('Next file #'),4,0)
        self.grid_layout.addWidget(QtWidgets.QLabel('Auto Increment'),5,0)

        self.grid_layout.addWidget(QtWidgets.QLabel('Filename format'),6,0)
        self.grid_layout.addWidget(QtWidgets.QLabel('Last filename'),7,0)

        self.grid_layout.addWidget(QtWidgets.QLabel('Save file'),9,0)
    

        # Field Values
        self.path_rbv_widget = QtWidgets.QWidget()
        self.path_rbv_widget_layout = QtWidgets.QHBoxLayout()
        self.path_rbv_widget_layout.setContentsMargins(0,0,0,0)
        self.path_rbv_widget_layout.addWidget(QtWidgets.QLabel('/home/epics/scratch/'))
        self.path_rbv_widget_layout.addSpacerItem(HorizontalSpacerItem())
        self.path_rbv_widget_layout.addWidget(QtWidgets.QLabel('Exists: '))
        self.path_rbv_widget_layout.addWidget(QtWidgets.QLabel('Yes'))
        self.path_rbv_widget.setLayout(self.path_rbv_widget_layout)
        self.grid_layout.addWidget(self.path_rbv_widget,0,1)

        self.grid_layout.addWidget(QtWidgets.QLineEdit('/home/epics/scratch'),1,1)
        self.grid_layout.addWidget(QtWidgets.QLabel('test'),2,1)
        self.grid_layout.addWidget(QtWidgets.QLineEdit('test'),3,1)
        
        

        self._layout.addLayout(self.grid_layout)
        self._layout.addSpacerItem(VerticalSpacerItem())

        self.setLayout(self._layout)

        self.style_widgets()
       
    

    def style_widgets(self):
       
        self.setStyleSheet("""
            #roi_control_button_widget FlatButton {
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



