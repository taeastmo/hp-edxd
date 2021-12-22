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

class MultipleDatasetsController(QObject):
    file_changed_signal = pyqtSignal(str)  
    channel_changed_signal = pyqtSignal(float)  

    def __init__(self, file_save_controller):
        super().__init__()
        self.file_save_controller = file_save_controller
        
        self.multi_spectra_model = MultipleSpectraModel()
        self.widget = MultiSpectraWidget()

        self.folder = ''
        self.active = False
        self.selectedENV = 0
        self.selectedENV_persist = 0
        self.envLen = 0

        #self.phases =dict()
        self.create_signals()
        
    def create_signals(self):
       
        self.widget.widget_closed.connect(self.view_closed)
        self.widget.add_btn.clicked.connect(self.add_btn_click_callback)
        
        self.widget.key_signal.connect(self.key_sig_callback)
        self.widget.plotMouseMoveSignal.connect(self.fastCursorMove)
        self.widget.plotMouseCursorSignal.connect(self.CursorClick)
        self.widget.file_list_view.currentRowChanged.connect(self.file_list_selection_changed_callback)
        self.widget.file_filter_refresh_btn.clicked.connect(self.file_filter_refresh_btn_callback)

    def set_channel_cursor(self, cursor):
        if len(cursor):
            E = cursor['channel']
            self.widget.select_channel(E)
        

    def file_list_selection_changed_callback(self, row):
        files = self.multi_spectra_model.r['files_loaded']
        if len(files):
            self.file_changed_signal.emit(files[row])
            self.widget.select_spectrum(row)

    def fastCursorMove(self, index):
        index = int(index)
        files = self.multi_spectra_model.r['files_loaded']
        if index < len(files) and index >= 0:
            file = os.path.split(files[index])[-1]
            self.widget.file_name_fast.setText(file)

    def CursorClick(self, index):
        index, E = index[0], index[1]
        files = self.multi_spectra_model.r['files_loaded']
        if index < len(files) and index >= 0:
            file = files[index]
            file_display = os.path.split(file)[-1]
            self.widget.file_name.setText(file_display)    
            self.file_changed_signal.emit(file)
            self.channel_changed_signal.emit(E)

            self.widget.select_file(index)
            self.widget.select_channel(E)
    
    def initData(self,filenames, progress_dialog):
        self.load_data(filenames, progress_dialog=progress_dialog)
        
    def load_data(self, paths, progress_dialog):
        self.multi_spectra_model.read_ascii_files_2d(paths, progress_dialog=progress_dialog)
        
    def file_filter_refresh_btn_callback(self):
        if self.folder != '':
            self.add_btn_click_callback(folder = self.folder)

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
            files = sorted([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]) 
            for f in files:
                if "hpmca" in f and filter in f:
                    file = os.path.join(folder, f) 
                    paths.append(file)  
                    files_filtered.append(f)
        filenames = paths

        if len(filenames):
            self.folder = folder
            self.widget.file_folder.setText(folder)
            #self.directories.phase = os.path.dirname(str(filenames[0]))
            progress_dialog = QtWidgets.QProgressDialog("Loading multiple spectra.", "Abort Loading", 0, len(filenames),
                                                        None)
            progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
            progress_dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            progress_dialog.show()
            QtWidgets.QApplication.processEvents()
            self.initData(filenames, progress_dialog)
            progress_dialog.close()
            QtWidgets.QApplication.processEvents()
            
        else:
            self.multi_spectra_model.clear()
        data = self.multi_spectra_model.r['data']
        self.widget.set_spectral_data(data)
        self.widget.reload_files(files_filtered)

    def connect_click_function(self, emitter, function):
        emitter.clicked.connect(function)      
  
    def key_sig_callback(self, sig):
        if self.widget.file_view_tabs.currentIndex() == 0:
            row = self.widget.get_selected_row()
            if sig == 'right' :
                row += 1
            if sig == 'left' :
                row -= 1
            if row >= 0 and row < len(self.multi_spectra_model.r['files_loaded']):
                self.widget.file_list_view.setCurrentRow(row)

    def show_view(self):
        self.active = True
        #self.update_envs()
        self.widget.raise_widget()
        #print('env view opened')
        
    def view_closed(self):
        self.active = False
       

