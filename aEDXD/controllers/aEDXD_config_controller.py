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


import os.path, sys
from PyQt5 import uic, QtWidgets,QtCore, QtGui
from  PyQt5.QtWidgets import QMainWindow, QApplication, QInputDialog, QWidget, QLabel
from PyQt5.QtCore import QObject, pyqtSignal, Qt
import numpy as np
from functools import partial
import json, h5py
import copy
from hpMCA.widgets.CustomWidgets import FlatButton, DoubleSpinBoxAlignRight, VerticalSpacerItem, NoRectDelegate, \
    HorizontalSpacerItem, ListTableWidget, VerticalLine, DoubleMultiplySpinBoxAlignRight
from pathlib import Path
from utilities.HelperModule import calculate_color
from numpy import arange
from utilities.HelperModule import getInterpolatedCounts

from aEDXD.widgets.aEDXD_options_widget import aEDXDOptionsWidget
from aEDXD.controllers.aEDXD_atom_options_controller import aEDXDAtomController
from aEDXD.controllers.aEDXD_files_controller import aEDXDFilesController
from hpMCA.widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog
from utilities.hpMCAutilities import displayErrorMessage, json_compatible_dict


############################################################

class aEDXDConfigController(QObject):
    params_changed_signal = QtCore.pyqtSignal()

    def __init__(self, model, display_window):
        super().__init__()
        self.model = model
        self.display_window = display_window
        self.gr_opts_window = aEDXDOptionsWidget(opt_fields('gr'), 'PDF options')
        self.sq_opts_window = aEDXDOptionsWidget(opt_fields('sq'), 'Structure factor options')
        self.opts_window = aEDXDOptionsWidget(opt_fields('spectra'), 'Spectra options')
        mp = self.model.params
        self.gr_opts_window.set_params(mp)
        self.sq_opts_window.set_params(mp)
        self.opts_window.set_params(mp)
        
        self.atom_controller = aEDXDAtomController()
        self.files_controller = aEDXDFilesController(self.model,self.display_window,self)
        
        self.current_tth_index = 0
        self.create_connections()
        self.colors = []

    def create_connections(self):
        self.files_controller.tth_index_changed_signal.connect(self.index_changed)
        self.files_controller.apply_clicked_signal.connect(self.apply_files_clicked_readback)
        self.gr_opts_window.apply_clicked_signal.connect(self.apply_clicked_readback) 
        self.sq_opts_window.apply_clicked_signal.connect(self.apply_clicked_readback) 
        self.opts_window.apply_clicked_signal.connect(self.apply_clicked_readback) 
        self.atom_controller.apply_clicked_signal.connect(self.apply_clicked_readback) 
       

    def apply_clicked_readback(self, params):
        if 'bin_size' in params :
            cur_bsize = self.files_controller.spectra_model.bin_size
            new_bsize = int(params['bin_size'])
            if cur_bsize != new_bsize:
                self.files_controller.spectra_model.set_bin_size(new_bsize)
                dataarray, ttharray= self.files_controller.spectra_model.get_dataarray()
                self.model.dataarray = dataarray
                self.model.ttharray = ttharray
                self.files_controller.data_changed_callback()
        self.model.set_params(params)
        self.params_changed_signal.emit()

    def apply_files_clicked_readback(self, params):
        dataarray = params['dataarray']
        ttharray = params['ttharray']
        self.model.dataarray = dataarray
        self.model.ttharray = ttharray
        self.params_changed_signal.emit()

    def save_config(self, filename):
        params_out = copy.copy(self.model.params)
        peaks = self.files_controller.spectra_model.get_cut_peaks()
        params_out['E_cut'] = peaks
        mcadata = self.files_controller.spectra_model.get_file_list()
        params_out['mcadata'] = mcadata
        options_out = json_compatible_dict(params_out)
        try:
            with open(filename, 'w') as outfile:
                json.dump(options_out, outfile,sort_keys=True, indent=4)
                outfile.close()
        except:
            displayErrorMessage( 'opt_save') 

    def save_config_file(self, *args, **kwargs):
        filename = kwargs.get('filename', None)
        if filename is None:
            filename = save_file_dialog(None, "Save config file.")
        self.save_config(filename)

    def save_hdf5(self):
        params = self.model.params
        f = h5py.File("mytestfile.hdf5", "w")
        grp = f.create_group("bar")
        arr = np.arange(100)
        dset = grp.create_dataset("init", data=arr)

    def load_config_file(self, *args, **kwargs):
        filename = kwargs.get('filename', None)
        if filename is None:
            filename = open_file_dialog(None, "Open config file.")
            if filename:
                config_file = filename
                self.model.set_config_file(config_file)
                self.model.cofigure()
                mp = self.model.params
                self.gr_opts_window.set_params(mp)
                self.sq_opts_window.set_params(mp)
                self.opts_window.set_params(mp)
                self.atom_controller.set_params(mp)
                self.files_controller.set_params(mp)

    def index_changed(self,ind):
        self.current_tth_index=ind
        #self.bin_cut_controller.index_changed(ind)

    #config
    def show_atoms(self):
        self.atom_controller.show_atoms() 
        
    def show_options(self):
        self.opts_window.raise_widget()

    def show_gr_options(self):
        self.gr_opts_window.raise_widget()  

    def show_sq_options(self):
        self.sq_opts_window.raise_widget() 

    def show_files(self):
        self.files_controller.show_files()

    def show_rois(self):
        self.files_controller.peak_cut_controller.show_rois()



def opt_fields(opt):
    opts_fields = {     'spectra':
                            {'bin_size': 
                                {'val'  : 8, 
                                 'desc' : 'data binning for better statistics',
                                 'label': 'Bin size',
                                 'step' : 1,
                                 'unit' : 'bins'},
                            'Emin': 
                                {'val'  : 33.0, 
                                 'desc' : 'minium energy range used for S(q) assessment',
                                 'label': 'E min',
                                 'step' : 0.5,
                                 'unit' : 'keV'}, 
                            'Emax':
                                {'val'  : 66.0, 
                                 'desc' : 'maxium energy range used for S(q) assessment',
                                 'label': 'E max',
                                 'step' : 0.5,
                                 'unit' : 'keV'}, 
                            'polynomial_deg': 
                                {'val'  : 4, 
                                 'desc' : 'for the primary beam model',
                                 'label': 'Polynomial',
                                 'step' : 1,
                                 'unit' : 'deg.'},
                            'itr_comp': 
                                {'val'  : 7, 
                                 'desc' : 'number of iterations for Compton background estimation',
                                 'label': 'Number of iterations',
                                 'step' : 1,
                                 'unit' : ''}
                            },
                        'sq':
                            {'sq_smoothing_factor': 
                                {'val'  : 0.7, 
                                 'desc' : 'spline smoothing factor for the final S(q)\n try <= 1.0 for more smoothening',
                                 'label': 'S(q) smooting factor',
                                 'step' : 0.05,
                                 'unit' : ''}, 
                            'q_spacing': 
                                {'val'  : 0.05, 
                                 'desc' : 'for evenly spaced S(q)',
                                 'label': 'q spacing',
                                 'step' : 0.01,
                                 'unit' : 'A^{-1}'}
                            },
                        'gr':
                            {'qmax': 
                                {'val'  : 14.0, 
                                 'desc' : 'q max cut-off, smaller than the measured q_max \n if bigger than the measured q_max, q_max=q_max_meas',
                                 'label': 'q max',
                                 'step' : 0.5,
                                 'unit' : 'A^{-1}'},                    
                            'rmax': 
                                {'val'  : 15.0, 
                                 'desc' : 'r max cut-off, if not defined by pi/q_spacing',
                                 'label': 'r max',
                                 'step' : 0.5,
                                 'unit' : 'A'},
                            'r_spacing': 
                                {'val'  : 0.05, 
                                 'desc' : 'for calculated G(r)',
                                 'label': 'r spacing',
                                 'step' : 0.01,
                                 'unit' : 'A'},
                            'hard_core_limit': 
                                {'val'  : 1.30, 
                                 'desc' : 'G(r) = -4*pi*rho*r, where r < hard_core_limit\n this is an imperical number\n 0, if no need to correct this or rho is unknown',
                                 'label': 'Hard core limit',
                                 'step' : 0.05,
                                 'unit' : 'A'},
                            'rho': 
                                {'val'  : 0.079598, 
                                 'desc' : 'Average number density \nNone, if unknown',
                                 'label': 'Density',
                                 'step' : 0.005,
                                 'unit' : 'atoms/A^3'},
                            'hard_core_limit': 
                                {'val'  : 1.30, 
                                 'desc' : 'G(r) = -4*pi*rho*r, where r < hard_sphere_limit\n this is an imperical number\n 0, if no need to correct this or rho is unknown',
                                 'label': 'Hard sphere limit',
                                 'step' : 0.05,
                                 'unit' : 'Angstrom'}
                            }

    }
    return opts_fields[opt]