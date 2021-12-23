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


import os
from posixpath import basename
from typing import TextIO
from PyQt5.QtGui import QFontMetrics
import numpy as np
from PyQt5 import QtWidgets, QtCore
from datetime import datetime

import time
import copy
from hpm.models.PhaseModel import PhaseLoadError
from utilities.HelperModule import get_base_name, increment_filename
from hpm.widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog, CifConversionParametersDialog, open_folder_dialog
import utilities.hpMCAutilities as mcaUtil
from hpm.widgets.SaveFileWidget import SaveFileWidget

from epics import caput, caget, PV

class FileSaveController(object):
    """
    IntegrationPhaseController handles all the interaction between the phase controls in the IntegrationView and the
    PhaseData object. It needs the PatternData object to properly handle the rescaling of the phase intensities in
    the pattern plot and it needs the calibration data to have access to the currently used wavelength.
    """

    def __init__(self, hpmcaController, **kwargs):
        """
        
        """
        defaults_options = kwargs['defaults_options']
        
        self.pvs_file = {}
        record_name_file = defaults_options.file_record
        self.record_name_file = record_name_file 
        
        if record_name_file != None:
            self.pvs_file ={'FilePath': None,
                            'FilePath_RBV': None,
                            'FileName': None,
                            'FileName_RBV': None,
                            'FullFileName_RBV': None,
                            'FileTemplate': None,
                            'FileTemplate_RBV': None,
                            'WriteMessage': None,
                            'FileNumber': None,
                            'FileNumber_RBV': None,
                            'AutoIncrement': None,
                            'AutoIncrement_RBV': None,
                            'WriteStatus': None,
                            'FilePathExists_RBV': None,
                            'AutoSave': None,
                            'AutoSave_RBV': None,
                            'WriteFile': None,
                            'WriteFile_RBV': None}
            for pv_file in self.pvs_file.keys():
                name = self.record_name_file + ':' + pv_file
                self.pvs_file[pv_file] = PV(name)
        
        self.mca_controller = hpmcaController
        self.widget = hpmcaController.widget
        #self.file_widget = SaveFileWidget()
        
      
        self.file_options = mcaUtil.restore_file_settings()
        self.file_naming_options = mcaUtil.restore_file_naming_settings()
        self.widget.set_file_naming_settings(self.file_naming_options)
        self.McaFileNameHolder = ''
        self.McaFileName = ''

        lbl = self.mca_controller.widget.folder_lbl
        lbl.setText(self.mca_controller.working_directories.savedata)
        self.create_signals()

    def file_dragged_in_signal(self, f):
        self.openFile(filename=f)

    def preferences_module(self, *args, **kwargs):
        [ok, file_options] = mcaUtil.mcaFilePreferences.showDialog(self.widget, self.file_options) 
        if ok :
            self.file_options = file_options
            if self.mca_controller.mca != None:
                self.mca_controller.mca.file_settings = file_options
            mcaUtil.save_file_settings(file_options)
        

    def show_view(self):
        pass

        
    def create_signals(self):
        ui = self.widget
       
        ui.actionSave_next.setEnabled(False)
        ui.actionSave_next.triggered.connect(lambda:self.ClickedSaveNextFile(ui.actionSave_next.text()))
        ui.actionSave_As.triggered.connect(self.ClickedSaveFile)
        ui.file_dragged_in_signal.connect(self.file_dragged_in_signal)
        ui.actionExport_pattern.triggered.connect(self.export_pattern)
        ui.actionOpen_file.triggered.connect(self.openFile)
        ui.actionPreferences.triggered.connect(self.preferences_module)
        ui.folder_browse_btn.clicked.connect(self.folder_browse_btn_callback)

        
        ui.increment_file_name_cbx.clicked.         connect(self.file_naming_option_changed_callback)
        ui.starting_num_int.       textChanged.     connect(self.file_naming_option_changed_callback)
        ui.min_digits_int.         currentIndexChanged.    connect(self.file_naming_option_changed_callback)
        ui.add_date_cbx.           stateChanged.         connect(self.file_naming_option_changed_callback)
        ui.add_time_cbx.           stateChanged.         connect(self.file_naming_option_changed_callback)
        ui.date_format_cmb.        currentIndexChanged.    connect(self.file_naming_option_changed_callback)
        ui.time_format_cmb.        currentIndexChanged.    connect(self.file_naming_option_changed_callback)
        ui.prefix_rad.             toggled.         connect(self.file_naming_option_changed_callback)
        ui.suffix_rad.             toggled.         connect(self.file_naming_option_changed_callback)
        
        ui.save_file_btn.clicked.connect(self.save_file_btn_callback)

    def acq_stopped(self):
        #print('stopped (acq_stopped)')
        if self.file_options.autosave:
            if self.mca_controller.mca.file_name != '':
                new_file = increment_filename(self.mca_controller.mca.file_name)
                if new_file != self.mca_controller.mca.file_name:
                    self.saveFile(new_file)
                    #print('save: ' + new_file)
                    
        if self.file_options.autorestart:
            # Important: this will only run if the mca is of epics type, the regular mca does not have the acq_erase_method
            self.mca_controller.mca.acq_erase_start()

    def save_file_btn_callback(self, *args):
        ext = '.hpmca'
        basename = self.get_next_filename()
        print(basename)
        folder = self.mca_controller.working_directories.savedata
        filepath = os.path.join(folder,basename + ext)
        print(filepath)
        self.saveFile(filepath)
        self.increment_file_number()

    def increment_file_number(self):
        next_n = int(self.widget.starting_num_int.text()) + 1
        self.file_naming_options.starting_number = next_n
        mcaUtil.save_file_naming_settings(self.file_naming_options)
        self.widget.starting_num_int.setText(str(next_n))

    def get_next_filename(self):
        delimiter = '_'
        s = self.file_naming_options
        base_name = self.widget.file_name_ebx.text()
        filename = ''
        if s.dt_append_possition == 0:
            filename = self.add_date(s,filename, delimiter)
            filename = self.add_time(s, filename, delimiter)
        if len(filename):
            filename += delimiter
        filename += base_name
        filename = self.add_number(s, filename, delimiter)
        if s.dt_append_possition == 1:
            filename = self.add_date(s,filename, delimiter)
            filename = self.add_time(s, filename, delimiter)
        return filename

    def add_number(self, s, text_in, delimiter=' '):    
        if s.increment_file_name:

            digits = s.minimum_digits +1 
            next_n = int(self.widget.starting_num_int.text())
            num_str = delimiter +str(next_n).zfill(digits)
            text_in += num_str
        return text_in
        

    def add_date(self, s, text_in, delimiter=' '):
        if s.add_date:
            d_format = s.d_format
            df = ''
            if d_format == 0:
                df = '%Y%m%d'
            if d_format == 1:
                df = '%Y-%m-%d'
            
            dstr = datetime.today().strftime(df)
            if len(text_in):
                text_in += delimiter
            text_in += dstr 
        return text_in

    def add_time(self, s, text_in, delimiter=' '):
        if s.add_time:
            t_format = s.t_format
            tf = ''
            if t_format == 0:
                tf = '%H:%M:%S'
            if t_format == 1:
                tf = '%I:%M:%S %p'
            tstr = datetime.today().strftime(tf)
            if len(text_in):
                text_in += delimiter
            text_in += tstr 
        return text_in

    def file_naming_option_changed_callback(self, *args):

        settings = self.widget.get_file_naming_settings()
        for s in settings:
            setattr( self.file_naming_options, s, settings[s])
        mcaUtil.save_file_naming_settings(self.file_naming_options)


    def ClickedSaveFile(self):  # handles Save As...
        if self.mca_controller.mca != None:
            #self.file_widget.raise_widget()
            filename =  save_file_dialog(self.widget, "Save spectrum file.",
                                    self.mca_controller.working_directories .savedata,
                                    'Spectrum (*.hpmca)', False)
            if filename != None:
                if len(filename)>0:
                    self.saveFile(filename)

    def ClickedSaveNextFile(self, menu_text):
        if self.mca_controller.mca != None:
            filename = menu_text.split(': ')[1]
            filename = os.path.join(self.mca_controller.working_directories .savedata, filename)
            self.saveFile(filename)



    def saveFile(self, filename):
        if self.mca_controller.mca != None:
            exists = os.path.isfile(filename)
            if not exists:
                write = True
            else:
                if  os.access(filename, os.R_OK):
                    base = os.path.basename(filename)
                    if self.file_options.warn_overwrite:
                        choice = QtWidgets.QMessageBox.question(None, 'Confirm Save As',
                                                    base+" already exists. \nDo you want to replace it?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                        write = choice == QtWidgets.QMessageBox.Yes                              
                    else: write = True
                else: write = False
            if write:
                fileout, success = self.mca_controller.mca.write_file(
                    file=filename, netcdf=0)
                if success:
                    #self.update_titlebar()
                    self.update_epics_filename(fileout)
                    
                    self.update_saveDataDir (os.path.dirname( str(fileout)) ) # working directory xrd files
                    self.widget.last_saved_lbl.setText(fileout)
                    # new_file = increment_filename(filename) # old way of incrementing
                    '''if new_file != filename:
                        self.widget.actionSave_next.setText(
                            'Save next: ' + os.path.basename(new_file))
                        self.widget.actionSave_next.setEnabled(True)
                    else:
                        self.widget.actionSave_next.setText('Save next')
                        self.widget.actionSave_next.setEnabled(False)'''
                else:
                    mcaUtil.displayErrorMessage('fs')
            else: 
                mcaUtil.displayErrorMessage('fs')

    def folder_browse_btn_callback(self):
        open_folder_dialog
        folder = open_folder_dialog(self.widget, "Select folder for saving data.")
        if folder != '' and folder is not None:
            self.update_saveDataDir(folder)

    def update_readDataDir(self, dir):
        self.mca_controller.working_directories.readdata = dir
        mcaUtil.save_folder_settings(self.mca_controller.working_directories )
        

    def update_saveDataDir(self, dir):
        self.mca_controller.working_directories.savedata = dir
        mcaUtil.save_folder_settings(self.mca_controller.working_directories )
        lbl = self.mca_controller.widget.folder_lbl
        
        lbl.setText(self.mca_controller.working_directories.savedata)

    def update_epics_filename(self, filename):
        if self.mca_controller.mca is not None:
            try:
                if 'FullFileName_RBV' in self.pvs_file:
                    self.pvs_file['FullFileName_RBV'].put(filename)
            except:
                pass

    def openFile(self, *args, **kwargs):
        filename = kwargs.get('filename', None)
        if filename is None:
            filename = open_file_dialog(self.widget, "Open spectrum file.",
                                    self.mca_controller.working_directories .readdata)
        if filename != '' and filename is not None:
            if os.path.isfile(filename):
                if self.mca_controller.Foreground != 'file':
                    success = self.mca_controller.initMCA('file',filename) == 0
                else:
                    #start_time = time.time()
                    [filename, success] = self.mca_controller.mca.read_file(file=filename, netcdf=0, detector=0)
                    #print("--- %s seconds ---" % (time.time() - start_time))
                if success:
                    self.McaFileName = filename
                    self.update_readDataDir (os.path.dirname(str(filename)) )#working directory xrd files
                    
                    # best to initialize controllers only once per session
                    if not self.mca_controller.controllers_initialized:  
                        self.mca_controller.initControllers()
                    self.mca_controller.data_updated()
                else:
                    mcaUtil.displayErrorMessage( 'fr')
            else:
                mcaUtil.displayErrorMessage( 'fr')

    def export_pattern(self):
        if self.mca_controller.mca is not None:
            img_filename, _ = os.path.splitext(os.path.basename(self.mca_controller.mca.file_name))
            filename = save_file_dialog(
                self.widget, "Save Pattern Data.",
                os.path.join(self.mca_controller.working_directories.savedata,
                            img_filename + self.mca_controller.working_directories .export_ext),
                ('Data (*.xy);;Data (*.chi);;Data (*.dat);;GSAS (*.fxye);;png (*.png)'))
            if filename != '':
                if filename.endswith('.png'):
                    self.widget.pg.export_plot_png(filename)
                #elif filename.endswith('.svg'):
                #    self.widget.pg.export_plot_svg(filename)
                else:
                    self.mca_controller.mca.export_pattern(filename, self.mca_controller.unit, self.mca_controller.plotController.units[self.mca_controller.unit])


    def epics_connections(self):

        

        pass

        # these may get implemented in the future to be in line with area detector file saving workflow
        '''self.pvs_file ={'FilePath': None,
                        'FilePath_RBV': None,
                        'FileName': None,
                        'FileName_RBV': None,
                        'FullFileName_RBV': None,
                        'FileTemplate': None,
                        'FileTemplate_RBV': None,
                        'WriteMessage': None,
                        'FileNumber': None,
                        'FileNumber_RBV': None,
                        'AutoIncrement': None,
                        'AutoIncrement_RBV': None,
                        'WriteStatus': None,
                        'FilePathExists_RBV': None,
                        'AutoSave': None,
                        'AutoSave_RBV': None,
                        'WriteFile': None,
                        'WriteFile_RBV': None}'''

        # filenames are written by hpMCA to this PV to be grabbed by an external data logger.
        ''' EPICS record should be created as follows:
            record(waveform,"16bmb:mca_file:FullFileName_RBV"){
                field(DESC,"FullFileName")
                field(DTYP,"Soft Channel")
                field(DESC,"file name")
                field(NELM,"256")
                field(FTVL,"CHAR")
            } 
        '''