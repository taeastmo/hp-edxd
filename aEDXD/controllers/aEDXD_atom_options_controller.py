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
import copy
import pyqtgraph as pg
from hpMCA.widgets.CustomWidgets import FlatButton, DoubleSpinBoxAlignRight, VerticalSpacerItem, NoRectDelegate, \
    HorizontalSpacerItem, ListTableWidget, VerticalLine, DoubleMultiplySpinBoxAlignRight, HorizontalLine
from aEDXD.models.aEDXD_atomic_parameters import aEDXDAtomicParameters
from aEDXD.widgets.aEDXD_atom_options_widget import aEDXDAtomWidget
import numpy as np

class aEDXDAtomController(QtCore.QObject):

    
    apply_clicked_signal = QtCore.pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        
        self.atom_window = aEDXDAtomWidget()
        self.ap = aEDXDAtomicParameters()
        self.sq_pars = []
        self.make_connections()

    def make_connections(self):
        self.atom_window.apply_btn.clicked.connect(self.apply)
        self.atom_window.add_btn.clicked.connect(self.add_atom_clicked)
        self.atom_window.delete_btn.clicked.connect(self.delete_atom_clicked)
        self.atom_window.clear_btn.clicked.connect(self.clear_atom_clicked)
        self.atom_window.fract_item_changed_signal.connect(self.edit_fract)

    def show_atoms(self):
        self.atom_window.raise_widget() 

    def add_atom_clicked(self):
        fract = None
        opt_abc = None
        opt_MKL = None
        opt_abc_note =None
        opt_MKL_note =None
        atom, ok = QtWidgets.QInputDialog.getText(
                self.atom_window, 'Add atom', 'Enter atom symbol (case sensitive): ', text='')
        if ok:
            options_abc=self.ap.get_abc_options(atom)
            opts_abc = []
            for o in options_abc:
                opts_abc.append(o)
            if len(opts_abc)>1:
                choice, ok = QtWidgets.QInputDialog.getItem(
                self.atom_window, 'Scattering factor options', 
                'Choose option for scattering factor data: ', opts_abc, 0, False)
                if ok:
                    opt_abc = options_abc[choice]
                    opt_abc_note = choice
            elif len(opts_abc)==1:
                opt_abc = options_abc[opts_abc[0]]
                opt_abc_note = opts_abc[0]
            options_MKL=self.ap.get_MKL_options(atom)
            opts_MKL = []
            for o in options_MKL:
                opts_MKL.append(o)
            if len(opts_MKL)>1:
                choice, ok = QtWidgets.QInputDialog.getItem(
                self.atom_window, 'Scattering factor options', 
                'Choose option for scattering factor data: ', opts_MKL, 0, False)
                if ok:
                    opt_MKL = options_MKL[choice]
                    opt_MKL_note = choice
            elif len(opts_MKL)==1:
                opt_MKL = options_MKL[opts_MKL[0]]
                opt_MKL_note = opts_MKL[0]
            d, okPressed = QtWidgets.QInputDialog.getDouble(
                        self.atom_window, "Molar fraction","Enter molar fraction: (0 to 1)", 0.5, 0, 1, 4)
            if okPressed:
                fract = d
            if fract is not None and opt_MKL is not None and opt_abc is not None:
                sq_par = [int(opt_abc[0]), fract] + list(opt_abc[1:]) + list(opt_MKL[1:-1])
                self.set_param(sq_par)
                
    def delete_atom_clicked(self):
        ind = self.atom_window.get_selected_atom_row()
        if ind > -1:
            self.atom_window.del_atom(ind)
            del self.sq_pars[ind]

    def clear_atom_clicked(self):
        self.sq_pars= []
        self.clear_widget()

    def clear_widget(self):
        while self.atom_window.atom_tw.rowCount()>0:
            self.atom_window.del_atom(0)

    def edit_fract(self,ind,fract):
        sp= self.sq_pars[ind]
        sp[1]=fract
        self.sq_pars[ind]=sp

    def apply(self):
        par = np.asarray(self.sq_pars)
        params = {}
        params['sq_par']=par
        
        self.apply_clicked_signal.emit(params)
    
    def set_params(self,params):
        sq_par = params['sq_par']
        if sq_par is not None:
            self.sq_pars = []
            self.clear_widget()
            for sp in sq_par:
                self.set_param(sp)
            
    def set_param(self, param):
        atom, atom_abc_note, atom_MKL_note, frac= \
                            self.ap.lookup_atom_by_sq_par(param)
        self.sq_pars.append(param)
        self.atom_window.add_atom(True, atom, 
                        atom_abc_note + ' / ' + atom_MKL_note, 
                        frac, len(self.sq_pars))
