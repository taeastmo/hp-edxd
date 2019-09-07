# -*- coding: utf8 -*-
# Dioptas - GUI program for fast processing of 2D X-ray data
# Copyright (C) 2017  Clemens Prescher (clemens.prescher@gmail.com)
# Institute for Geology and Mineralogy, University of Cologne
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

import os

import numpy as np
from PyQt5 import QtWidgets, QtCore
import copy

from hpMCA.models.hklGenModel import hklGenModel_viewModel
#from utilities.HelperModule import get_base_name
#from hpMCA.controllers.JcpdsEditorController import JcpdsEditorController
#from hpMCA.widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog, CifConversionParametersDialog
#from hpMCA.models.PhaseModel import PhaseModel
from hpMCA.widgets.hklGenWidget import hklGenWidget

import utilities.hpMCAutilities as mcaUtil


class hklGenController():
    """
     
    """

    def __init__(self, plotWidget, mcaModel, plotController, roiController):

        self.model = hklGenModel_viewModel()
        self.hklGen_widget = hklGenWidget(self.model)
        self.active = False
        self.current_cell = None
        self.create_connections()

    def create_connections(self):
        self.hklGen_widget.add_btn.clicked.connect(self.add_btn_callback)
        self.hklGen_widget.delete_btn.clicked.connect(self.delete_btn_callback)
        self.hklGen_widget.clear_btn.clicked.connect(self.clear_btn_callback)
        self.hklGen_widget.rois_btn.clicked.connect(self.rois_btn_callback)

        self.hklGen_widget.symmetry_edited_signal.connect(self.symmetry_edited_callback)
        self.hklGen_widget.spgrp_tb.editingFinished.connect(self.spgrp_tb_edited_callback)
        self.hklGen_widget.lattice_parameter_edited_signal.connect(self.lattice_parameter_edited_callback)

        self.hklGen_widget.cell_selection_edited_signal.connect(self.cell_selection_edited_callback)

    def cell_selection_edited_callback(self, ind):
        try:
            self.current_cell = self.model.get_cell_by_index(ind)
            self.update_cell_view()
        except IndexError:
            pass
    
    def lattice_parameter_edited_callback(self, param):
        print(param)
        if not self.current_cell is None:
            self.current_cell.set_lattice_param(param)
            self.update_cell_view()

    def spgrp_tb_edited_callback(self, *args, **kwargs):
        spgrp = self.hklGen_widget.spgrp_tb.text()
        if not self.current_cell is None:
            self.current_cell.set_spacegroup(spgrp)
            self.update_cell_view()

    def update_cell_view(self):
        enabled_params = self.current_cell.get_params_enabled()
        lattice_params = self.current_cell.get_lattice_params()
        self.hklGen_widget.set_cell(lattice_params, enabled_params)
        hkl_reflections = self.current_cell.get_hkl_reflections()
        
        '''
        ind = self.model.get_cell_index(self.current_cell)
        name = self.current_cell.get_spacegroup()
        self.model.set_cell_name(ind,name)
        '''
        '''
        hkl_str=''
        for hkl in hkl_reflections[0]:
            hkl_str=hkl_str+str(hkl[0])+' '+str(hkl[1])+' '+str(hkl[2])+' '+str(round(hkl[3],4)) +'<br>'
        self.hklGen_widget.hkl_widget.setText(hkl_str)
        '''

    def symmetry_edited_callback(self, symmetry):
        if not self.current_cell is None:
            #self.current_cell.set_symmetry(symmetry)
            current_symmetry = self.current_cell.get_symmetry()
            if symmetry.upper() != current_symmetry.upper():
                
                default_spacegroup = self.current_cell.default_spacegroup[symmetry.upper()]
                self.current_cell.set_spacegroup(default_spacegroup)
                self.hklGen_widget.spgrp_tb.setText(str(self.current_cell.get_spacegroup()))
            self.update_cell_view()
            

    def add_btn_callback(self):
        new_cell = self.model.add_cell()
        self.current_cell = new_cell
        new_cell.set_spacegroup(str(self.hklGen_widget.spgrp_tb.text()))
        self.update_cell_view()
        
        print('add')

    def delete_btn_callback(self, *args, **kwargs):
        """
        Deletes the currently selected Cell
        """
        print('delete')
        cur_ind = self.hklGen_widget.get_selected_row()
        if cur_ind >= 0:
            self.model.remove_cell_by_index(cur_ind)
        n_cells = self.model.get_num_of_cells()
        if n_cells:
            self.current_cell = self.model.cells[-1]
        else:
            self.current_cell = None
    

    def clear_btn_callback(self):
        """
        Deletes all tth from the GUI
        """
        while self.model.rowCount() > 0:
            self.model.remove_cell_by_index(self.model.rowCount()-1)
        self.current_cell = None
        print('clear')


    def rois_btn_callback(self):
        print('rois')
    
    def show_view(self):
        self.active = True
        self.hklGen_widget.raise_widget()