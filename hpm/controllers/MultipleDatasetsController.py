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
from hpm.widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog
from hpm.widgets.MultipleDatasetsWidget import MultiSpectraWidget
from hpm.models.multipleDatasetModel import MultipleSpectraModel


from PyQt5.QtCore import pyqtSignal, QObject

class MultipleDatasetsController(QObject):

    env_updated_signal = pyqtSignal(int, str )  
    env_selection_changed_signal = pyqtSignal(int,str)
    file_changed_signal = pyqtSignal(str)  

    def __init__(self, file_save_controller):
        super().__init__()
        self.file_save_controller = file_save_controller
        
        self.multi_spectra_model = MultipleSpectraModel()
        self.widget = MultiSpectraWidget()

      
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

    def initData(self,filenames, progress_dialog):
        
        self.load_data(filenames, progress_dialog=progress_dialog)
        
        

    def load_data(self, paths, progress_dialog):
        
        self.multi_spectra_model.read_ascii_files_2d(paths, progress_dialog=progress_dialog)
        
        

    def add_btn_click_callback(self, *args, **kwargs):
        """
        Loads a multiple spectra into 2D numpy array
        :return:
        """

        filter = self.widget.file_filter.text().strip()
        
        folder = '/Users/ross/Desktop/Cell2-HT'
        files = sorted([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]) 
        paths = []
        for f in files:
            if "hpmca" in f and filter in f:
                file = os.path.join(folder, f) 
                
                paths.append(file)

        filenames = paths

        if filenames is None:
            filenames = open_files_dialog(None, "Load Spectra(s).",
                                          None)

            
        if len(filenames):
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

        data = np.log10(self.multi_spectra_model.r['data'] +.5)
        self.widget.img.setImage(data)

    def connect_click_function(self, emitter, function):
        emitter.clicked.connect(function)      

  
    def key_sig_callback(self, sig):
        if sig == 'delete' :
            self.remove_btn_click_callback()

    def set_environment(self, environment):
        self.update_env(environment)

    def env_selection_changed(self, row, **kwargs):
        cur_ind = row
        self.selectedENV = row
        
        if cur_ind >-1 and cur_ind < len(self.env): 
            out = self.env[cur_ind].description
               
        else: out = ''
        #self.update_env_cursor_lines() 
        self.env_selection_changed_signal.emit(cur_ind, out)
        #print('selected: ' + str(cur_ind))

    def show_view(self):
        self.active = True
        #self.update_envs()
        self.widget.raise_widget()
        #print('env view opened')
        
    def view_closed(self):
        self.active = False
       

    def update_env(self, environment):
        oldLen =  copy.copy(self.envLen)
        self.selectedENV_persist = copy.copy(self.selectedENV)
       
        self.env = environment
  
        newLen = len(self.env)
        self.nenvs = len(self.env)
        self.blockSignals(True)
        self.widget.blockSignals(True)
        if newLen == oldLen:
            for i, r in enumerate(self.env):
                #index = self.env.index(r)
                
                self.update_env_by_ind(r.name, r.value, r.description, i)
        else:
            while self.widget.env_tw.rowCount() > 0:
                self.widget.del_env(self.widget.env_tw.rowCount()-1,silent=True)
            for r in self.env:
             
                self.widget.add_env(r.name, r.value, r.description, silent=True)
        self.blockSignals(False)              
        self.widget.blockSignals(False)    
        self.widget.env_tw.blockSignals(False)      
        if self.selectedENV_persist<len(self.env):
            sel = np.clip(self.selectedENV_persist,0,31)
        else: 
            sel = len(self.env)-1
        self.widget.select_env(sel) 
        self.selectedENV=sel
    
        self.envLen = copy.copy(self.nenvs)
  
    def env_removed(self, ind):
        self.widget.del_env(ind)
        

    def clear_envs(self, *args, **kwargs):
        """
        Deletes all envs from the GUI
        """
        self.blockSignals(True)
        while self.widget.env_tw.rowCount() > 0:
            self.env_removed(self.widget.env_tw.rowCount()-1)
        
        self.envLen = 0
        self.blockSignals(False)
       
                
    def update_env_by_ind(self, pv, value, description, ind):
        self.widget.update_env(pv, value, description, ind)

    def env_name_changed(self, ind, name):
        self.widget.rename_env(ind, name)


