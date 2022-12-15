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


from functools import partial
#from platform import java_ver
import pyqtgraph as pg
import copy
import numpy as np
import os
from PyQt5 import QtWidgets, QtCore
from hpm.widgets.CustomWidgets import FlatButton, DoubleSpinBoxAlignRight, VerticalSpacerItem, NoRectDelegate, \
    HorizontalSpacerItem, ListTableWidget, VerticalLine, DoubleMultiplySpinBoxAlignRight
from hpm.widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog, open_folder_dialog
from hpm.widgets.AmorphousAnalysisWidget import AmorphousAnalysisWidget
from hpm.models.AmorphousAnalysisModel import AmorphousAnalysisModel
from PyQt5.QtCore import pyqtSignal, QObject
import natsort
from hpm.controllers.DisplayPrefsController import DisplayPreferences
from hpm.models.mcaModel import MCA
from hpm.controllers.MaskController import MaskController
from hpm.models.MaskModel import MaskModel


class AmorphousAnalysisController(QObject):
    file_changed_signal = pyqtSignal(str)  
    element_changed_signal = pyqtSignal(int)
    channel_changed_signal = pyqtSignal(float)  
    add_rois_signal = pyqtSignal(list)

    def __init__(self,multi_spectra_model, file_save_controller, directories):
        super().__init__()
        self.file_save_controller = file_save_controller
        self.directories = directories
        self.multi_spectra_model = multi_spectra_model
        
        
        self.mask_model = MaskModel()
        self.model = AmorphousAnalysisModel( self.mask_model)
        self.widget = AmorphousAnalysisWidget()

        for step in self.model.steps:
            s = self.model.steps[step]
            dims = s.get_data_out_dims()
            name = s.name
            mask = s.mask
            plot = self.widget.add_scratch_plot(name, dims, mask)
            s.updated.connect(plot.plot_image)
            
        plots_keys = list(self.widget.scratch_plots.keys())
        self.widget.scratch_widget = self.widget.scratch_plots[plots_keys[0]]
        
        self.displayPrefs = DisplayPreferences(self.widget.line_plot_widget) 

        self.folder = ''
        self.active = False
        self.selectedENV = 0
        self.selectedENV_persist = 0
        self.envLen = 0
        self.single_file = False

        self.scale = 'Channel'
        self.row_scale = 'Index'
        self.file = ''
        self.row = 0
        self.mask_controller = MaskController(self.mask_model, self.widget.mask_widget, directories)

        self.create_signals()
        
    def create_signals(self):
       
        self.widget.widget_closed.connect(self.view_closed)


        self.widget.sum_btn.clicked.connect(self.sum_data)
        self.widget.sum_scratch_btn.clicked.connect(self.sum_scratch_callback)
        self.widget.ebg_btn.clicked.connect(self.ebg_data)
        self.widget.transpose_btn.clicked.connect(self.transpose_E_2theta)
      


    def HorzScaleRadioToggle(self,horzScale):
        
        self.set_unit(horzScale)

    

    

    def set_row_scale(self, label='Index'):
        d = [1,0]
        row_scale = 'Spectrum index'

        if label == 'tth':
            row_scale=f'2\N{GREEK SMALL LETTER THETA}'
            d = self.multi_spectra_model.tth_scale

        self.widget.set_image_row_scale(row_scale, d)
        self.row_scale = row_scale

    def transpose_E_2theta(self):
        self.multi_spectra_model.energy_to_2theta()

    def update_view (self, scale='Channel'):
        r = [1,0]
        scratch_view = []
        if scale == 'Channel':
            view = self.multi_spectra_model.data
            
            self.widget.radioChannel.setChecked(True)
        elif scale == 'q':
            view = self.multi_spectra_model.q
            r = self.multi_spectra_model.q_scale
            scratch_view = self.multi_spectra_model.scratch_q
            self.widget.radioq.setChecked(True)
        elif scale == 'E':
            view = self.multi_spectra_model.E
            r = self.multi_spectra_model.E_scale
            scratch_view = self.multi_spectra_model.scratch_E
            self.widget.radioE.setChecked(True)
        elif scale == 'Aligned':
            view = self.multi_spectra_model.rebinned_channel_data
            self.widget.radioAligned.setChecked(True)
            #r = self.multi_spectra_model.E_scale

        self.widget.set_spectral_data(view)
        if len(scratch_view):
            self.widget.scratch_widget.plot_image(scratch_view)
        self.mask_controller.mask_model._img_data = view
        self.mask_controller.update_mask_dimension()
        self.widget.set_image_scale(scale, r)
        
        self.scale = scale

    def sum_data(self):

        if self.scale == 'E':
            data = self.multi_spectra_model.E
            scale = self.multi_spectra_model.E_scale
        elif self.scale == 'q':
            data = self.multi_spectra_model.q
            scale = self.multi_spectra_model.q_scale
        elif self.scale == 'Channel':
            data = self.multi_spectra_model.data
            scale = [1,0]
        elif self.scale == 'Aligned':
            data = self.multi_spectra_model.rebinned_channel_data
            scale = [1,0]
        mask = self.mask_model.get_mask()
        out = self.multi_spectra_model.flaten_data(data, mask)
        self.multi_spectra_model.scratch_E_average = out
        x = np.arange(len(out)) * scale[0] + scale[1]
        self.widget.plot_data(x, out)

    def sum_scratch_callback(self):

        if self.scale == 'E':
            data = self.multi_spectra_model.scratch_E
            scale = self.multi_spectra_model.E_scale
        elif self.scale == 'q':
            data = self.multi_spectra_model.scratch_q
            scale = self.multi_spectra_model.q_scale
        elif self.scale == 'Channel':
            data = self.multi_spectra_model.data
            scale = [1,0]
        elif self.scale == 'Aligned':
            data = self.multi_spectra_model.rebinned_channel_data
            scale = [1,0]
        mask = self.mask_model.get_mask()
        out = self.multi_spectra_model.flaten_data(data, mask)
        self.multi_spectra_model.scratch_q_average = out
        x = np.arange(len(out)) * scale[0] + scale[1]
        self.widget.plot_data(x, out)
    

    def ebg_data(self):
        if self.scale == 'E':
            if len(self.multi_spectra_model.scratch_E_average):
                m = self.multi_spectra_model
                for i in range(np.shape(m.E)[0]):
                    m.scratch_E[i] = m.E[i] / m.scratch_E_average
                #self. update_view('E')
                self.widget.scratch_widget.plot_image(m.scratch_E)
        if self.scale == 'q':
            if len(self.multi_spectra_model.scratch_q_average):
                m = self.multi_spectra_model
                for i in range(np.shape(m.q)[0]):
                    m.scratch_q[i] = m.q[i] / m.scratch_q_average
                #self. update_view('q')
    
                self.widget.scratch_widget.plot_image(m.scratch_q)

    def multispectra_loaded(self, scale='Channel'):
        data = self.multi_spectra_model.data
        self.multi_spectra_model.q = np.zeros(np.shape(data))
        self.multi_spectra_model.E = np.zeros(np.shape(data))
        self.multi_spectra_model.scratch_E = np.zeros(np.shape(data))
        self.multi_spectra_model.scratch_q = np.zeros(np.shape(data))
        self.multi_spectra_model.rebinned_channel_data = copy.deepcopy(data)
       
        


    def show_view(self):
        self.active = True
        #self.update_envs()
        self.widget.raise_widget()
        
        
    def view_closed(self):
        self.active = False
       

