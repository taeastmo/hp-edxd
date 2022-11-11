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
from hpm.widgets.MultipleDatasetsWidget import MultiSpectraWidget
from hpm.models.multipleDatasetModel import MultipleSpectraModel
from PyQt5.QtCore import pyqtSignal, QObject
import natsort
from hpm.controllers.DisplayPrefsController import DisplayPreferences

class MultipleDatasetsController(QObject):
    file_changed_signal = pyqtSignal(str)  
    element_changed_signal = pyqtSignal(int)
    channel_changed_signal = pyqtSignal(float)  

    def __init__(self, file_save_controller):
        super().__init__()
        self.file_save_controller = file_save_controller
        
        self.multi_spectra_model = MultipleSpectraModel()
        self.widget = MultiSpectraWidget()
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

        self.mca = None

        #self.phases =dict()
        self.create_signals()
        
    def create_signals(self):
       
        self.widget.widget_closed.connect(self.view_closed)
        '''self.widget.add_btn.clicked.connect(self.add_btn_click_callback)
        self.widget.add_file_btn.clicked.connect(self.add_file_btn_click_callback)'''
        self.widget.radioE.clicked.connect(partial (self.rebin_btn_callback, 'E'))
        self.widget.radioq.clicked.connect(partial (self.rebin_btn_callback, 'q'))
        self.widget.radioChannel.clicked.connect(partial (self.rebin_btn_callback, 'Channel'))
        self.widget.radioAligned.clicked.connect(partial (self.rebin_btn_callback, 'Aligned'))

        self.widget.align_btn.clicked.connect(self.align_btn_callback)
        self.widget.sum_btn.clicked.connect(self.sum_data)
        self.widget.ebg_btn.clicked.connect(self.ebg_data)
        self.widget.tth_btn.clicked.connect(partial(self.set_row_scale, 'tth'))

        self.widget.key_signal.connect(self.key_sig_callback)
        self.widget.plotMouseMoveSignal.connect(self.fastCursorMove)
        self.widget.plotMouseCursorSignal.connect(self.CursorClick)
        self.widget.file_list_view.currentRowChanged.connect(self.file_list_selection_changed_callback)
        self.widget.file_filter_refresh_btn.clicked.connect(self.file_filter_refresh_btn_callback)

        self.widget.prev_btn.clicked.connect(partial(self.key_sig_callback, 'left'))
        self.widget.next_btn.clicked.connect(partial(self.key_sig_callback, 'right'))

    def set_mca(self, mca, element=0):
        self.multi_spectra_model.set_mca(mca)
        
        self.multispectra_loaded()
    
    def set_channel_cursor(self, cursor):
        if len(cursor):
           
            channel = cursor['channel']
            pos = channel
            if self.scale == 'q' or self.scale == 'E':
                converter = self.multi_spectra_model.mca.get_calibration()[self.row].channel_to_scale
                pos = converter(channel,self.scale)
            elif self.scale == 'Aligned':
                scale = self.multi_spectra_model.calibration['slope'][self.row]
                translate = self.multi_spectra_model.calibration['offset'][self.row]
                pos = (channel - translate )/scale 
            self.widget.select_value(pos)
        

    def file_list_selection_changed_callback(self, row):
        files = self.multi_spectra_model.r['files_loaded']
        if len(files):
            file = files[row]
            self.row = row
            self.file_changed(file)
            self.widget.select_spectrum(row)

    def file_changed(self, file):
        self.file_changed_signal.emit(file)
        file_display = os.path.split(file)[-1]
        self.widget.file_name.setText(file_display)  

    def element_changed(self, element):
        self.element_changed_signal.emit(int(element))

    def fastCursorMove(self, index):
        index = int(index)
        files = self.multi_spectra_model.r['files_loaded']
        if index < len(files) and index >= 0:
            file = os.path.split(files[index])[-1]
            self.widget.file_name_fast.setText(file)

    def key_sig_callback(self, sig):
        if self.widget.file_view_tabs.currentIndex() == 0:
            row = self.row
            if sig == 'right' or sig == 'up':
                row += 1
            if sig == 'left' or sig == 'down':
                row -= 1
            pos = self.widget.cursorPoints[0][1]
            self.CursorClick([row, pos])

    '''def adjust_row(self, row):
        files = self.multi_spectra_model.r['files_loaded']
        index = row
        if len(files) == 1:
            self.widget.select_spectrum(index)
            self. element_changed(index)
            self.row = index
           
        elif len(files) >1:
            if index < len(files) and index >= 0:
                self.widget.select_file(index)
                self.widget.select_spectrum(index)
                file = files[index]
                self.file_changed(file)
                self.row = index'''

    def CursorClick(self, index):
        index, pos = int(index[0]), index[1]
        
        rows = np.shape(self.multi_spectra_model.data)[0]
        if index < rows and index >= 0:
            self.widget.select_spectrum(index)
            self. element_changed(index)
            self.row = index
            self.widget.select_value(pos)
            self.set_channel(index, pos)
            
        '''elif len(files) >1:
            if index < len(files) and index >= 0:
                self.widget.select_file(index)
                self.widget.select_spectrum(index)
                file = files[index]
                self.file_changed(file)
                self.row = index
                self.widget.select_value(pos)
                self.set_channel(index, pos)'''

    def set_channel(self, index, pos):
        channel = pos
        if self.scale == 'q' or self.scale == 'E':
            converter = self.multi_spectra_model.mca.get_calibration()[index].scale_to_channel
            channel = converter(pos,self.scale)
        elif self.scale == 'Aligned':
            scale = self.multi_spectra_model.calibration['slope'][self.row]
            translate = self.multi_spectra_model.calibration['offset'][self.row]
            channel = pos * scale + translate
        
        self.channel_changed_signal.emit(channel)

    def aligner(self):
        pass
    
    def file_filter_refresh_btn_callback(self):
        if not self.single_file:
            if self.folder != '':
                self.add_btn_click_callback(folder = self.folder)

    def align_btn_callback(self):
        if len(self.multi_spectra_model.data):
            self.multi_spectra_model.rebin_for_energy()
            scale = "Aligned"
            self.update_view(scale)

    def rebin_btn_callback(self, scale):
        if len(self.multi_spectra_model.data):
            self.scale = scale
            if scale == 'q' or scale == 'E':
                self.multi_spectra_model.rebin_scale(scale) 
            self.update_view(scale)    

    def set_row_scale(self, label='Index'):
        d = [1,0]
        row_scale = 'Spectrum index'

        if label == 'tth':
            row_scale=f'2\N{GREEK SMALL LETTER THETA}'
            d = self.multi_spectra_model.tth_scale

        self.widget.set_image_row_scale(row_scale, d)
        self.row_scale = row_scale

    def update_view (self, scale='Channel'):
        r = [1,0]
        if scale == 'Channel':
            view = self.multi_spectra_model.data
            self.widget.radioChannel.setChecked(True)
        elif scale == 'q':
            view = self.multi_spectra_model.q
            r = self.multi_spectra_model.q_scale
            self.widget.radioq.setChecked(True)
        elif scale == 'E':
            view = self.multi_spectra_model.E
            r = self.multi_spectra_model.E_scale
            self.widget.radioE.setChecked(True)
        elif scale == 'Aligned':
            view = self.multi_spectra_model.rebinned_channel_data
            self.widget.radioAligned.setChecked(True)
            #r = self.multi_spectra_model.E_scale

        self.widget.set_spectral_data(view)
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
        out = self.multi_spectra_model.flaten_data(data)
        if self.scale == 'E':
            self.multi_spectra_model.E_average = out
        x = np.arange(len(out)) * scale[0] + scale[1]
        self.widget.plot_data(x, out)

    def ebg_data(self):
        if self.scale == 'E':
            if len(self.multi_spectra_model.E_average):
                m = self.multi_spectra_model
                for i in range(np.shape(m.E)[0]):
                    m.E_normalized[i] = m.E[i] - m.E_average
                self. update_view('E')
    
    def add_file_btn_click_callback(self,  *args, **kwargs):

        filter = self.widget.file_filter.text().strip()
        if 'file' in kwargs:
            file = kwargs['file']
        else:
                file = open_file_dialog(None, "Load Multispectral File.",
                                          None)
        if file == '':
            return

        if (file.endswith('.mca')  or file.endswith('.hpmca') or file[-3:].isnumeric() ) and filter in file :
            folder = os.path.split(file)[0]
            self.load_file_sequence(folder, [file])
            self.multispectra_loaded()

    def add_btn_click_callback(self,  *args, **kwargs):
        """
        Loads a multiple spectra into 2D numpy array
        :return:
        """

        filter = self.widget.file_filter.text().strip()
        if 'folder' in kwargs:
            folder = kwargs['folder']
        else:
                folder = open_folder_dialog(None, "Load Spectra(s).",
                                          None)
        if folder == '':
            return
        paths = []
        files_filtered = []
        if os.path.exists(folder):
            files = natsort.natsorted([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and not f.startswith('.')]) 
            for f in files:
                if (f.endswith('.hpmca') or f.endswith('.chi') or f.endswith('.mca') or f.endswith('.xy') or f[-3:].isnumeric()) and filter in f :
                    file = os.path.join(folder, f) 
                    paths.append(file)  
                    files_filtered.append(f)
            filenames = paths
            self.load_file_sequence(folder, filenames)
            data = self.multi_spectra_model.data
           
            self.multispectra_loaded()

    def load_file_sequence(self, folder, filenames):
        if len(filenames):
            single_file =  len(filenames) == 1 # file sequence or single file containing multiple spectra
          
            self.folder = folder
            self.widget.file_folder.setText(folder)
            #self.directories.phase = os.path.dirname(str(filenames[0]))
            progress_dialog = QtWidgets.QProgressDialog("Loading multiple spectra.", "Abort Loading", 0, len(filenames),None)
            
            progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
            progress_dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            progress_dialog.show()
            QtWidgets.QApplication.processEvents()
            self.load_data(filenames, progress_dialog, single_file)
            progress_dialog.close()
            QtWidgets.QApplication.processEvents()
            
        else:
            self.multi_spectra_model.clear()

        
    def load_data(self, paths, progress_dialog, single_file):
        
        self.single_file = single_file
        firstfile = paths[0]
        if single_file:
            if  firstfile.endswith('.mca'):
                self.multi_spectra_model.read_mca_ascii_file_2d(paths, progress_dialog=progress_dialog)
            elif firstfile.endswith('.hpmca') :
                self.multi_spectra_model.read_ascii_file_multielement_2d(paths, progress_dialog=progress_dialog)
            else:
                ext = firstfile[-3:]
                if ext.isnumeric():
                    self.multi_spectra_model.read_ascii_file_multielement_2d(paths, progress_dialog=progress_dialog)

        else:

            if firstfile.endswith('.hpmca')or firstfile[-3:].isnumeric():
                self.multi_spectra_model.read_ascii_files_2d(paths, progress_dialog=progress_dialog)
            elif firstfile.endswith('.chi') or firstfile.endswith('.xy'):
                self.multi_spectra_model.read_chi_files_2d(paths, progress_dialog=progress_dialog)
            elif  firstfile.endswith('.mca'):
                print('mca 2d not implemented')
        
            


    def multispectra_loaded(self, scale='Channel'):
        data = self.multi_spectra_model.data
        self.multi_spectra_model.q = np.zeros(np.shape(data))
        self.multi_spectra_model.E = np.zeros(np.shape(data))
        self.multi_spectra_model.rebinned_channel_data = copy.deepcopy(data)
        self.update_view(scale)
        files_loaded = self.multi_spectra_model.r['files_loaded']
        files = []
        for f in files_loaded:
            files.append(os.path.basename(f))
        self.widget.reload_files(files)
   
  
    

    def show_view(self):
        self.active = True
        #self.update_envs()
        self.widget.raise_widget()
        
        
    def view_closed(self):
        self.active = False
       

