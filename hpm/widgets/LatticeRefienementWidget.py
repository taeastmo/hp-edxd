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
import numpy as Numeric
from PyQt5 import QtWidgets, QtCore

import hpm.models.jcpds as jcpds
import copy
import functools
import math
import pyqtgraph as pg
from hpm.widgets.CustomWidgets import FlatButton, DoubleSpinBoxAlignRight, VerticalSpacerItem, NoRectDelegate, \
    HorizontalSpacerItem, ListTableWidget, VerticalLine, DoubleMultiplySpinBoxAlignRight


class mcaCalibrate2theta_widgets(object):
   """ Private class"""
   def __init__(self, nrois):
      self.use_flag             = [None]*nrois
      self.d_spacing            = [None]*nrois
      self.fwhm                 = [None]*nrois
      self.energy               = [None]*nrois
      self.label                = [None]*nrois
      self.calc_d               = [None]*nrois
      self.calc_d_diff       = [None]*nrois
      #self.two_theta_fit        = [None]*nrois

class LatticeRefinementWidget(QtWidgets.QWidget):
    widget_closed = QtCore.pyqtSignal()

    def __init__(self, roi, calibration, jcpds_directory=''):
        super().__init__()
        self.setWindowTitle("Lattice Refinement")

        self.roi = roi
        self.rois = []


        self.calibration = calibration
        
        self.jcpds_directory = jcpds_directory
        
        self._layout = QtWidgets.QVBoxLayout()  
        
        self.button_widget = QtWidgets.QWidget(self)
        self.button_widget.setObjectName('rois_control_button_widget')
        self._button_layout = QtWidgets.QHBoxLayout(self.button_widget)
        self._button_layout.setContentsMargins(0, 0, 0, 0)
        self._button_layout.setSpacing(6)
        

        
    
        self.button_widget.setLayout(self._button_layout)
        self._layout.addWidget(self.button_widget)

        self.phases_lbl=QtWidgets.QLabel('')

        
        
        self._body_layout = QtWidgets.QHBoxLayout()

        self._layout.addLayout(self._body_layout)

        
        self.init_roi_view()

        self._body_layout.addLayout(self.verticalLayout_4)
        self._layout.addWidget(self.phases_lbl)

        self.setLayout(self._layout)
        self.style_widgets()

    def set_jcpds_directory(self, jcpds_directory):
        self.jcpds_directory = jcpds_directory

    def init_roi_view(self):

        
        detector = 0
        jcpds_directory = self.jcpds_directory
        
        
        #self.data = copy.deepcopy(mca.get_data()[detector])
        self.jcpds_directory = jcpds_directory

        self.fname_label = 'Phase file not found. Please close this \nwindow and load the corresponding phase file (.jcpds) first.'
        if len(self.roi):
            roi = self.roi[0]
            label = roi.label
            temp = label.split()
            if len(temp) >= 2:
                file = temp[0]
                item = jcpds.find_fname(self.jcpds_directory, file, file+'.jcpds')
                if item is not None:
                    self.fname_label = 'Using phase file: ' + item['full_file']
                

        #self.exit_command = command
        self.nrois = len(self.roi)
        
        
        
        self.widgets     = mcaCalibrate2theta_widgets(self.nrois)
        

        
        self.initUI()


    def initUI(self):

        #### display column headings    
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.phase_file_label = QtWidgets.QLabel(self.fname_label)
        self.verticalLayout_4.addWidget(self.phase_file_label)
        self.groupBox = QtWidgets.QGroupBox(self)
        self.container = self.groupBox        
        self.gridLayout = QtWidgets.QGridLayout(self.container)
        self.gridLayout.setContentsMargins(7, 15, 7, 7)
        self.gridLayout.setSpacing(5)

        
        
        header = {'ROI':0,'Use?':1,'HKL':2,
            'E obs':3,f'E calc':4, f'E error':5
        }

        row = 0
        for key, col in header.items():
            t = QtWidgets.QLabel(self.groupBox)
            t.setText(key)
            t.setAlignment(QtCore.Qt.AlignHCenter)
            t.setMinimumSize(QtCore.QSize(60, 0))
            self.gridLayout.addWidget(t, row, col, QtCore.Qt.AlignHCenter)

        #### display rois parameters

        for i in range(self.nrois):
            row=i+1 
            
            t = QtWidgets.QLabel(self.groupBox)
            t.setText(str(i))
            t.setAlignment(QtCore.Qt.AlignHCenter)
            self.gridLayout.addWidget(t, row, 0, QtCore.Qt.AlignHCenter)  

            self.widgets.use_flag[i] = t = QtWidgets.QCheckBox(self.groupBox)
            t.setChecked(self.roi[i].use==1)
            t.toggled.connect(functools.partial(self.menu_use, i)) # lambda expression didn't work so using functools.partial instead
            self.gridLayout.addWidget(t, row, 1, QtCore.Qt.AlignHCenter)

            self.widgets.label[i] = t = QtWidgets.QLineEdit(self.groupBox)
            t.setText(self.roi[i].label.split(' ')[-1])
            t.setFixedWidth(70)
            t.setAlignment(QtCore.Qt.AlignHCenter)
            self.widgets.label[i].returnPressed.connect(functools.partial(self.menu_label, i))
            self.gridLayout.addWidget(t, row, 2, QtCore.Qt.AlignHCenter)
            
           

            # try to use the label to lookup d spacing

            '''d = jcpds.lookup_jcpds_line(self.roi[i].label,path=self.jcpds_directory)
            if (d != None): self.roi[i].d_spacing = d
            else: self.roi[i].d_spacing = 0

            self.widgets.d_spacing[i] = t = QtWidgets.QLineEdit(self.groupBox)
            t.setText('%.4f' % self.roi[i].d_spacing)
            t.setFixedWidth(70)
            t.setAlignment(QtCore.Qt.AlignHCenter)
            t.returnPressed.connect(functools.partial(self.menu_d_spacing, i))
            self.gridLayout.addWidget(t, row, 3, QtCore.Qt.AlignHCenter)'''
            
            self.widgets.energy[i] = t = QtWidgets.QLineEdit(self.groupBox)
            t.setText('%.3f' % self.roi[i].energy)
            t.setFixedWidth(70)
            t.setAlignment(QtCore.Qt.AlignHCenter)
            t.returnPressed.connect(functools.partial(self.menu_energy, i))
            self.gridLayout.addWidget(t, row, 3, QtCore.Qt.AlignHCenter)


            self.widgets.calc_d[i] = t = QtWidgets.QLineEdit(self.groupBox)
            t.setText('%.4f' % 0.0)
            t.setFixedWidth(70)
            t.setAlignment(QtCore.Qt.AlignHCenter)
            self.gridLayout.addWidget(t, row, 4, QtCore.Qt.AlignHCenter)

            self.widgets.calc_d_diff[i] = t = QtWidgets.QLineEdit(self.groupBox)
            t.setText('%.4f' % 0.0)
            t.setFixedWidth(70)
            t.setAlignment(QtCore.Qt.AlignHCenter)
            self.gridLayout.addWidget(t, row, 5, QtCore.Qt.AlignHCenter)

        self.verticalLayout_4.addWidget(self.groupBox)


        self.groupBox_2 = QtWidgets.QGroupBox(self)
        self.groupBox_2.setTitle("")

        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        
        
        # in QtDialong, setting default=False, autoDefault=False prevents button from default trigger by Enter key
        self.do_fit = t = QtWidgets.QPushButton(self.groupBox_2, default=False, autoDefault=False)
        t.setText("Refine Lattice")
        t.setFixedWidth(110)
       
        self.horizontalLayout.addWidget(t)

        self.plot_cal = t = QtWidgets.QPushButton(self.groupBox_2, default=False, autoDefault=False)
        t.setText("Plot E error")
        
        t.setFixedWidth(110)
        self.horizontalLayout.addWidget(t)

        self.lbltwo_theta = t = QtWidgets.QLabel(self.groupBox_2)
        t.setText(f'2\N{GREEK SMALL LETTER THETA}:')
        t.setFixedWidth(70)
        t.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.horizontalLayout.addWidget(t)

        self.two_theta = t = QtWidgets.QLabel(self.groupBox_2)
        t.setText('%.5f' % self.calibration.two_theta)
        self.horizontalLayout.addWidget(t)

        self.horizontalLayout.setAlignment(QtCore.Qt.AlignHCenter)

        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.verticalLayout_4.addWidget(self.groupBox_2)

        

        
        self.groupBox.setTitle("Defined regions")
        #self.setFixedSize(self._layout.sizeHint())  

        
        #self.setWindowFlags(QtCore.Qt.Tool)
        #self.setAttribute(QtCore.Qt.WA_MacAlwaysShowToolWindow)     

    def menu_use(self,  roi):
        value = self.widgets.use_flag[roi].isChecked()
        """ Private method """
        self.roi[roi].use = value 
        #print('use: '+str(value))
        #print('roi: '+str(roi))

    def menu_label(self, roi):
        """ Private method """
        label = self.widgets.label[roi].text()
        d_spacing = jcpds.lookup_jcpds_line(label,path=self.jcpds_directory)
        if (d_spacing != None):
            self.roi[roi].d_spacing = d_spacing
            self.widgets.d_spacing[roi].setText('%.3f' % d_spacing)
            
        self.roi[roi].label=label

    def menu_energy(self, roi):
        """ Private method """
        energy = float(self.widgets.energy[roi].text())
        self.roi[roi].energy = energy
        self.widgets.energy[roi].setText('%.3f' % energy)
        #print('energy: %.3f' % energy)

    def menu_d_spacing(self, roi):
        """ Private method """
        d_spacing = float(self.widgets.d_spacing[roi].text())
        self.roi[roi].d_spacing = d_spacing
        self.widgets.d_spacing[roi].setText('%.3f' % d_spacing)
        #print('d-spacing: %.3f' % d_spacing)

    

    def style_widgets(self):
        self.setStyleSheet("""
            #roi_control_button_widget QPushButton {
                min-width: 75;
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

 






