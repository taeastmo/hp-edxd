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
import numpy as np
from PyQt5 import QtWidgets, QtCore

import copy
from hpm.models.PhaseModel import PhaseLoadError
from utilities.HelperModule import get_base_name, increment_filename
from hpm.widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog, CifConversionParametersDialog
import utilities.hpMCAutilities as mcaUtil

class FileSaveController(object):
    """
    IntegrationPhaseController handles all the interaction between the phase controls in the IntegrationView and the
    PhaseData object. It needs the PatternData object to properly handle the rescaling of the phase intensities in
    the pattern plot and it needs the calibration data to have access to the currently used wavelength.
    """

    def __init__(self, mcaController):
        """
        
        """
        
        
        self.mca_controller = mcaController
        self.widget = mcaController.widget
        
      
        self.file_options = mcaUtil.restore_file_settings('hpMCA_file_settings.json')

        self.McaFilename = None
        self.McaFileNameHolder = None
        self.McaFilename_PV = '16bmb:mca_file:FilePath'

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

    def ClickedSaveFile(self):  # handles Save As...
        if self.mca_controller.mca != None:
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
                    self.update_epics_filename()
                    
                    self.mca_controller.working_directories .savedata = os.path.dirname(
                        str(fileout))  # working directory xrd files
                    mcaUtil.save_folder_settings(self.mca_controller.working_directories )
                    new_file = increment_filename(filename)
                    if new_file != filename:
                        self.widget.actionSave_next.setText(
                            'Save next: ' + os.path.basename(new_file))
                        self.widget.actionSave_next.setEnabled(True)
                    else:
                        self.widget.actionSave_next.setText('Save next')
                        self.widget.actionSave_next.setEnabled(False)
                else:
                    mcaUtil.displayErrorMessage('fs')
            else:
                mcaUtil.displayErrorMessage('fs')

    def update_epics_filename(self):
        if self.mca_controller.mca is not None:
            if self.McaFilename is not None:
                name = self.mca_controller.mca.get_name_base()
                self.McaFilename.put(name)

    def openFile(self, *args, **kwargs):
        filename = kwargs.get('filename', None)
        if filename is None:
            filename = open_file_dialog(self.widget, "Open spectrum file.",
                                    self.mca_controller.working_directories .savedata)
        if filename != '' and filename is not None:
            if os.path.isfile(filename):
                if self.mca_controller.Foreground != 'file':
                    success = self.mca_controller.initMCA('file',filename) == 0
                else:
                    [filename, success] = self.mca_controller.mca.read_file(file=filename, netcdf=0, detector=0)
                if success:
                    self.mca_controller.working_directories .savedata = os.path.dirname(str(filename)) #working directory xrd files
                    mcaUtil.save_folder_settings(self.mca_controller.working_directories )
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
                os.path.join(self.mca_controller.working_directories .savedata,
                            img_filename + self.mca_controller.working_directories .export_ext),
                ('Data (*.xy);;Data (*.chi);;Data (*.dat);;GSAS (*.fxye);;png (*.png)'))
            if filename is not '':
                if filename.endswith('.png'):
                    self.widget.pg.export_plot_png(filename)
                #elif filename.endswith('.svg'):
                #    self.widget.pg.export_plot_svg(filename)
                else:
                    self.mca_controller.mca.export_pattern(filename, self.mca_controller.unit, self.mca_controller.plotController.units[self.mca_controller.unit])