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

""" 
    Ross Hrubiak
"""

from functools import partial

from PyQt5 import QtWidgets, QtCore
from hpMCA.models.pressure.LatticeRefinement import latticeRefinement
import copy
import pyqtgraph as pg
from hpMCA.widgets.CustomWidgets import FlatButton, DoubleSpinBoxAlignRight, VerticalSpacerItem, NoRectDelegate, \
    HorizontalSpacerItem, ListTableWidget, VerticalLine, DoubleMultiplySpinBoxAlignRight


class PressureWidget(QtWidgets.QWidget):
    widget_closed = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.rois = []
        self.phases=dict()
        self._layout = QtWidgets.QVBoxLayout()  
        self.setWindowTitle('Unit cell')
        self.button_widget = QtWidgets.QWidget(self)
        self.button_widget.setObjectName('rois_control_button_widget')
        self._button_layout = QtWidgets.QHBoxLayout()
        self._button_layout.setContentsMargins(0, 0, 0, 0)
        self._button_layout.setSpacing(6)
        #self.ok_btn = FlatButton('Ok')
        #self.ok_btn.clicked.connect(self.update_phases)


        self.phases_lbl=QtWidgets.QLabel('')

        #self._button_layout.addWidget(self.ok_btn)
        
    
        self.button_widget.setLayout(self._button_layout)

        self._layout.addWidget(self.phases_lbl)
        self._layout.addWidget(self.button_widget)
        self._body_layout = QtWidgets.QHBoxLayout()

        self._layout.addLayout(self._body_layout)
        self.setLayout(self._layout)
        self.style_widgets()

    def set_rois_phases(self, rois, phases):
        self.rois = rois
        self.phases = phases
        self.update_phases()

    def update_phases(self):
        
        rois = self.rois
        if len(rois)>0:
            roi_groups = {}     # separate rois into groups based on name 
            for r in rois:
                l = r.label.split(' ')[0]
                if len(l)>1:
                    if not l in roi_groups.keys():
                        roi_groups[l]=[r]
                    else:
                        roi_groups[l].append(r)
            lbl=''
            for p in roi_groups:
                if p !='':
                    curr_phase = None
                    original_rois = None
                    
                    if p in self.phases.keys():
                        curr_phase = self.phases[p][1]
                        original_rois = self.phases[p][0]
                    else: 
                        lbl += 'phase not recognized'
                        break
                    lbl += p + ': '
                    DHKL = []
                    phase = roi_groups[p]
                    for r in phase:
                        d = r.d_spacing
                        hkl = r.label.split(' ')[1]
                        if not len(hkl)==3 or not hkl.isdigit():
                            break
                        h = int(hkl[0])
                        k = int(hkl[1])
                        l = int(hkl[2])
                        dhkl = [d,h,k,l]
                        DHKL.append(dhkl)
                    if len(dhkl)>0:
                        lattice = latticeRefinement()
                        lattice.set_dhkl(DHKL)
                        symmetry = curr_phase.params['symmetry']
                        lattice.set_symmetry(symmetry.lower())
                        lattice.refine()
                        v = lattice.get_volume()
                        l = lattice.get_lattice()
                        v0 = curr_phase.params['v0']
                        v_over_v0 = v/v0
                        v0_v = 1/v_over_v0
                        curr_phase.compute_pressure(volume = v)
                        P = curr_phase.params['pressure']
                        T = curr_phase.params['temperature']
                        #print(str(DHKL))
                        lbl +='volume = ' + '%.3f'%(v)+' A^3; v/v0 = '+ '%.3f'%(v_over_v0)
                        lbl += '; P = '+ '%.2f'%(P)+ ' GPa; T = '+ '%.2f'%(T)
                        #print('lattice: '+ str(l))
            self.phases_lbl.setText(lbl)

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

 






