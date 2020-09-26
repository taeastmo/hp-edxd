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



import os, os.path, sys, platform, copy

from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QInputDialog, QMessageBox, QErrorMessage
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from epics.clibs import *  # makes sure dlls are included in the exe

from hpm.models.mcaModel import MCA
from hpm.models.epicsMCA import epicsMCA

from hpm.widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog
from hpm.widgets.eCalWidget import mcaCalibrateEnergy
from hpm.widgets.TthCalWidget import mcaCalibrate2theta
from hpm.widgets.xrfWidget import xrfWidget
from hpm.widgets.hpmcaWidget import hpMCAWidget


from hpm.controllers.PhaseController import PhaseController
from hpm.controllers.mcaPlotController import plotController
from hpm.controllers.RoiController import RoiController
from hpm.controllers.OverlayController import OverlayController
from hpm.controllers.DisplayPrefsController import DisplayPreferences
#from hpm.controllers.hklGenController import hklGenController

import utilities.hpMCAutilities as mcaUtil
from utilities.HelperModule import increment_filename

from epics import PV

Theme = 1   # app style 0=windows 1=dark 
from .. import style_path

class hpmcaController(QObject):
    key_signal = pyqtSignal(str)
    
    def __init__(self, app):
        super().__init__()
        self.app = app  # app object
        global Theme
        self.Theme = Theme
        self.style_path = style_path
        self.setStyle(self.Theme)
        self.widget = hpMCAWidget(app) 
        self.make_prefs_menu()  # for mac
        self.displayPrefs = DisplayPreferences(self.widget.pg)


        self.McaFilename = None
        self.McaFileNameHolder = None
        self.McaFilename_PV = '16bmb:McaFilename'
        self.elapsed_time_presets = ['0','2','5','30','60','120'] 
        
        self.zoom_pan = 0        # mouse left button interaction mode 0=rectangle zoom 1=pan
        
        self.create_connections() 
        
        self.working_directories = mcaUtil.restore_folder_settings('hpMCA_folder_settings.json')
        self.file_options = mcaUtil.restore_file_settings('hpMCA_file_settings.json')
        self.presets = mcaUtil.mcaDisplay_presets() 
        self.last_saved = ''
        
        # initialize some stuff
        self.mca = None              # mca model
        self.epicsMCAholder = None   # holds a epicsMCA reference so that it doesnt
        self.Foreground = None       # str, can be either 'epics' or 'file'
        
        self.plotController = None    
        self.roi_controller = None
        self.phase_controller = None  # phase controller 
        self.fluorescence_controller = None
        self.overlay_controller = None
        self.controllers_initialized = False
    
        self.unit = 'E' #default units
        
    def create_connections(self):
        ui = self.widget
        ui.btnROIadd.clicked.connect(lambda:self.roi_action('add'))
        ui.btnROIclear.clicked.connect(lambda:self.roi_action('clear'))
        ui.btnROIdelete.clicked.connect(lambda:self.roi_action('delete'))
        ui.btnROIprev.clicked.connect(lambda:self.roi_action('prev'))
        ui.btnROInext.clicked.connect(lambda:self.roi_action('next'))
        ui.btnKLMprev.clicked.connect(lambda:self.xrf_action('prev'))
        ui.btnKLMnext.clicked.connect(lambda:self.xrf_action('next'))
        ui.lineEdit_2.editingFinished.connect(lambda:self.xrf_search(ui.lineEdit_2.text()))

        ui.key_signal.connect(self.key_sig_callback)
       
        #epics related buttons:
        self.epicsBtns = [ui.btnOn,ui.btnOff,ui.btnErase]

        
        self.epicsPresets = [ui.PRTM_pv, ui.PLTM_pv]
        self.epicsElapsedTimeBtns_PRTM = [ui.PRTM_0,
                                          ui.PRTM_1,
                                          ui.PRTM_2,
                                          ui.PRTM_3,
                                          ui.PRTM_4,
                                          ui.PRTM_5  ]
        self.epicsElapsedTimeBtns_PLTM = [ui.PLTM_0,
                                          ui.PLTM_1,
                                          ui.PLTM_2,
                                          ui.PLTM_3,
                                          ui.PLTM_4,
                                          ui.PLTM_5  ]
        self.update_elapsed_preset_btn_messages(self.elapsed_time_presets)
        

        ui.radioLog.toggled.connect(self.LogScaleSet)
        ui.radioE.toggled.connect(lambda:self.HorzScaleRadioToggle(self.widget.radioE))
        ui.radioq.toggled.connect(lambda:self.HorzScaleRadioToggle(self.widget.radioq))
        ui.radioChannel.toggled.connect(lambda:self.HorzScaleRadioToggle(self.widget.radioChannel))
        ui.radiod.toggled.connect(lambda:self.HorzScaleRadioToggle(self.widget.radiod))

        ui.actionSave_next.setEnabled(False)
        ui.actionSave_next.triggered.connect(lambda:self.ClickedSaveNextFile(ui.actionSave_next.text()))
        ui.actionExit.triggered.connect(self.widget.close)
        ui.actionSave_As.triggered.connect(self.ClickedSaveFile)
        ui.actionExport_pattern.triggered.connect(self.export_pattern)
        ui.actionOpen_file.triggered.connect(self.openFile)
        ui.actionJCPDS.triggered.connect(self.jcpds_module)
        ui.actionCalibrate_energy.triggered.connect(self.calibrate_energy_module)
        ui.actionCalibrate_2theta.triggered.connect(self.calibrate_tth_module)
        ui.actionOpen_detector.triggered.connect(self.openDetector)
        ui.actionROIs.triggered.connect(self.roi_module)
        ui.actionOverlay.triggered.connect(self.overlay_module)
        ui.actionFluor.triggered.connect(self.fluorescence_module)
        ui.actionPreferences.triggered.connect(self.preferences_module)
        ui.actionPressure.triggered.connect(self.pressure_module)
        ui.actionhklGen.triggered.connect(self.hklGen_module)
        ui.actionManualTth.triggered.connect(self.set_Tth)
        ui.actionDisplayPrefs.triggered.connect(self.display_preferences_module)
        ui.actionPresets.triggered.connect(self.presets_module)
        ui.actionAbout.triggered.connect(self.about_module)

        ui.baseline_subtract.clicked.connect(self.baseline_subtract_callback)
        
        ui.file_dragged_in_signal.connect(self.file_dragged_in_signal)

    def make_prefs_menu(self):
        _platform = platform.system()
        if _platform == "Darwin":    # macOs has a 'special' way of handling preferences menu
            pact = QtWidgets.QAction('Preferences', self.app)
            pact.triggered.connect(self.preferences_module)
            pact.setMenuRole(QtWidgets.QAction.PreferencesRole)
            pmenu = QtWidgets.QMenu('Preferences')
            pmenu.addAction(pact)
            menu = self.widget.menuBar()
            menu.addMenu(pmenu)

    def about_module(self):
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Information)
        self.msg.setText('This program was written by R. Hrubiak')
        self.msg.setInformativeText('More info to come...')
        self.msg.setWindowTitle('About')
        self.msg.setDetailedText('The details are as follows:')
        self.msg.setStandardButtons(QMessageBox.Ok)
        self.msg.show()

    def file_dragged_in_signal(self, f):
        self.openFile(filename=f)

    def key_sig_callback(self, sig):
        if sig == 'right' :
            self.roi_action('next')
        if sig == 'left' :
            self.roi_action('prev')
        if sig == 'delete' :
            self.roi_action('delete')
        if sig == 'shift_press' :
            self.zoomPan(1)
        if sig == 'shift_release' :
            self.zoomPan(0)  
            
    def set_Tth(self):
        mca = self.mca
        calibration = copy.deepcopy(mca.get_calibration()[0])
        tth = calibration.two_theta
        val, ok = QInputDialog.getDouble(self.widget, "Manual 2theta setting", "Current 2theta = "+ '%.4f'%(tth)+"\nEnter new 2theta: \n(Note: calibrated 2theta value will be updated)",tth,0,180,4)
        if ok:
            calibration.two_theta = val
            mca.set_calibration([calibration])


    def preferences_module(self, *args, **kwargs):
        [ok, file_options] = mcaUtil.mcaFilePreferences.showDialog(self.widget, self.file_options) 
        if ok :
            self.file_options = file_options
            if self.mca != None:
                self.mca.file_settings = file_options
            mcaUtil.save_file_settings(file_options)

    def display_preferences_module(self, *args, **kwargs):
        self.displayPrefs.show()
            
    
    def presets_module(self, *args, **kwargs):
        presets = self.mca.get_presets()
        
        [ok, presets] = mcaUtil.mcaControlPresets.showDialog(self.widget,presets) 
        if ok :
            self.presets = presets
            self.mca.set_presets(self.presets)
            #mcaUtil.save_file_settings(file_preferences)
    

    def initMCA(self, mcaType, det_or_file):
        [live_btn, real_btn] = self.epicsPresets
        epicsElapsedTimeBtns_PRTM = self.epicsElapsedTimeBtns_PRTM
        epicsElapsedTimeBtns_PLTM = self.epicsElapsedTimeBtns_PLTM
        if mcaType == 'file':      
            mca = MCA()
            mca.auto_process_rois = True
            [fileout, success] = mca.read_file(file=det_or_file, netcdf=0, detector=0)
            
            if not success:
                return 1
            if self.mca != None:
                if self.Foreground == 'epics':
                    self.mca.dataAcquired.disconnect()
                    self.mca.acq_stopped.disconnect()
                    
                    self.McaFileNameHolder = self.McaFilename
                    self.epicsMCAholder = self.mca
            self.McaFilename = None        
            self.mca = mca
            self.blockSignals(True)
            for btn in self.epicsBtns:
                btn.setEnabled(False)
                btn.setChecked(False)
            self.blockSignals(False)
            live_btn.disconnect()
            real_btn.disconnect()
            for btn in epicsElapsedTimeBtns_PRTM:
                btn.disconnect()
            for btn in epicsElapsedTimeBtns_PLTM:
                btn.disconnect()
        elif mcaType == 'epics': 
            name = ''
            
            if self.epicsMCAholder is not None:
                name = self.epicsMCAholder.name
            if self.McaFileNameHolder is not None:
                self.McaFilename = self.McaFileNameHolder
            else:
                try:
                    self.McaFilename = PV(self.McaFilename_PV)
                except:
                    pass
            if name == det_or_file :
                self.mca = self.epicsMCAholder
                self.mca.toggleEpicsWidgetsEnabled(True)
            else:
                mca = epicsMCA(det_or_file, self.epicsBtns, self.file_options)
                
                if not mca.initOK:
                    live_btn.disconnect()
                    real_btn.disconnect()
                    return 1
                    
                

                self.mca = mca
                if self.epicsMCAholder != None:
                    self.epicsMCAholder.unload()
                self.epicsMCAholder = self.mca
            record = self.mca.name
            live_btn.connect(record + '.PRTM')
            real_btn.connect(record + '.PLTM')
            for btn in epicsElapsedTimeBtns_PRTM:
                btn.connect(record + '.PRTM')
            for btn in epicsElapsedTimeBtns_PLTM:
                btn.connect(record + '.PLTM')
            
        self.mca.auto_process_rois = True
        if self.controllers_initialized:
            self.plotController.set_mca(self.mca)
            self.phase_controller.set_mca(self.mca)
            self.roi_controller.set_mca(self.mca)
            self.fluorescence_controller.set_mca(self.mca)
        self.Foreground = mcaType
        
        return 0

    def update_elapsed_preset_btn_messages(self, elapsed_presets):
        for i, btn in enumerate(self.epicsElapsedTimeBtns_PLTM):
            btn.setMessage(message = elapsed_presets[i])
        for i, btn in enumerate(self.epicsElapsedTimeBtns_PRTM):
            btn.setMessage(message = elapsed_presets[i])

    def initControllers(self):
        #initialize plot model
        
        self.plotController = plotController(self.widget.pg, self.mca, self, self.unit)
        # updates cursor position labels
        self.plotController.staticCursorMovedSignal.connect(self.mouseCursor)
        self.plotController.fastCursorMovedSignal.connect(self.mouseMoved)  
        self.plotController.selectedRoiChanged.connect(self.roi_selection_updated) 
        self.plotController.envUpdated.connect(self.envs_updated_callback)
        
        #initialize roi controller
        self.roi_controller = self.plotController.roi_controller
        
        # initialize phase controller
        self.phase_controller = PhaseController(self.widget.pg, self.mca, 
                                            self.plotController, self.roi_controller, 
                                            self.working_directories)
        # initialize overlay controller: not done yet
        self.overlay_controller = OverlayController( self, self.plotController, self.widget)
        #initialize xrf controller
        self.fluorescence_controller = xrfWidget(self.widget.pg, self.plotController, self.roi_controller, self.mca)
        self.fluorescence_controller.xrf_selection_updated_signal.connect(self.xrf_updated)

        #initialize hklGen controller
        #self.hlkgen_controller = hklGenController(self.widget.pg,self.mca,self.plotController,self.roi_controller)
        
        
        self.controllers_initialized = True

        self.widget.menu_items_set_enabled(True)
        
        return 0
        
    def closeEvent(self, QCloseEvent, *event):
        self.app.closeAllWindows()

    ########################################################################################
    ########################################################################################

    def openDetector(self):
        # initialize epics mca
        text, ok = QInputDialog.getText(self.widget, 'EPICS MCA', 'Enter MCA PV name: ', text='16bmb:aim_adc1')
        if ok:
            mcaTemp = self.mca 
            status = self.initMCA('epics',text)
            if status == 0:
                if self.controllers_initialized == False:
                    status = self.initControllers()
                if status == 0:
                    self.data_updated()
                    acquiring = self.mca.get_acquire_status()
                    self.mca.dataAcquired.signal.connect(self.dataReceivedEpics)
                    self.mca.acq_stopped.signal.connect(self.acq_stopped)
                    if acquiring == 1:
                        self.mca.acqOn()
                    elif acquiring == 0:
                        self.mca.acqOff()
                    self.update_titlebar()
            else:
                self.mca = mcaTemp
                mcaUtil.displayErrorMessage( 'init')

    def dataReceivedEpics(self ):
        self.data_updated()

    ########################################################################################
    ########################################################################################

    def acq_stopped(self):
        #print('stopped (acq_stopped)')
        if self.file_options.autosave:
            if self.mca.file_name != '':
                new_file = increment_filename(self.mca.file_name)
                if new_file != self.mca.file_name:
                    self.saveFile(new_file)
                    #print('save: ' + new_file)
                    
        if self.file_options.autorestart:
            self.mca.acq_erase_start()

    def ClickedSaveFile(self):  # handles Save As...
        if self.mca != None:
            filename =  save_file_dialog(self.widget, "Save spectrum file.",
                                    self.working_directories.savedata,
                                    'Spectrum (*.hpmca)', False)
            if filename != None:
                if len(filename)>0:
                    self.saveFile(filename)

    def ClickedSaveNextFile(self, menu_text):
        if self.mca != None:
            filename = menu_text.split(': ')[1]
            filename = os.path.join(self.working_directories.savedata, filename)
            self.saveFile(filename)

    def saveFile(self, filename):
        if self.mca != None:
            exists = os.path.isfile(filename)
            if not exists:
                write = True
            else:
                if  os.access(filename, os.R_OK):
                    base = os.path.basename(filename)
                    if self.file_options.warn_overwrite:
                        choice = QMessageBox.question(None, 'Confirm Save As',
                                                    base+" already exists. \nDo you want to replace it?",
                                                    QMessageBox.Yes | QMessageBox.No)
                        write = choice == QMessageBox.Yes                              
                    else: write = True
                else: write = False
            if write:
                fileout, success = self.mca.write_file(
                    file=filename, netcdf=0)
                if success:
                    #self.update_titlebar()
                    self.update_epics_filename()
                    
                    self.working_directories.savedata = os.path.dirname(
                        str(fileout))  # working directory xrd files
                    mcaUtil.save_folder_settings(self.working_directories)
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
        if self.mca is not None:
            if self.McaFilename is not None:
                name = self.mca.get_name_base()
                self.McaFilename.put(name)

    def openFile(self, *args, **kwargs):
        filename = kwargs.get('filename', None)
        if filename is None:
            filename = open_file_dialog(self.widget, "Open spectrum file.",
                                    self.working_directories.savedata)
        if filename != '' and filename is not None:
            if os.path.isfile(filename):
                if self.Foreground != 'file':
                    success = self.initMCA('file',filename) == 0
                else:
                    [filename, success] = self.mca.read_file(file=filename, netcdf=0, detector=0)
                if success:
                    self.working_directories.savedata = os.path.dirname(str(filename)) #working directory xrd files
                    mcaUtil.save_folder_settings(self.working_directories)
                    # best to initialize controllers only once per session
                    if not self.controllers_initialized:  
                        self.initControllers()
                    self.data_updated()
                else:
                    mcaUtil.displayErrorMessage( 'fr')
            else:
                mcaUtil.displayErrorMessage( 'fr')

    def export_pattern(self):
        if self.mca is not None:
            img_filename, _ = os.path.splitext(os.path.basename(self.mca.file_name))
            filename = save_file_dialog(
                self.widget, "Save Pattern Data.",
                os.path.join(self.working_directories.savedata,
                            img_filename + self.working_directories.export_ext),
                ('Data (*.xy);;Data (*.chi);;Data (*.dat);;GSAS (*.fxye);;png (*.png)'))
            if filename is not '':
                if filename.endswith('.png'):
                    self.widget.pg.export_plot_png(filename)
                #elif filename.endswith('.svg'):
                #    self.widget.pg.export_plot_svg(filename)
                else:
                    self.mca.export_pattern(filename, self.unit, self.plotController.units[self.unit])

    ########################################################################################
    ########################################################################################

    def update_titlebar(self):
        name = self.mca.name
        if name != '':
            name += ' - '
        self.widget.setWindowTitle(name + u'hpMCA')

    def data_updated(self):
        self.plotController.update_plot()  
        self.update_titlebar()
        elapsed = self.mca.get_elapsed()[0]
        self.widget.lblLiveTime.setText("%0.2f" %(elapsed.live_time))
        self.widget.lblRealTime.setText("%0.2f" %(elapsed.real_time))

    def envs_updated_callback(self, envs):
        #print(envs)
        pass

    def xrf_updated(self,text):
        self.blockSignals(True)
        self.widget.lineEdit_2.setText(text)
        self.blockSignals(False)
    
    ########################################################################################
    ########################################################################################

    def overlay_module(self):
        if self.mca != None:
            self.overlay_controller.showWidget()

    def calibrate_energy_module(self):
        if self.mca != None:
            self.ce = mcaCalibrateEnergy(self.mca)
            if self.ce.nrois < 2:
                mcaUtil.displayErrorMessage( 'calroi')
                self.ce.destroy()
            else:
                self.ce.raise_widget()
    
    def calibrate_tth_module(self):
        if self.mca != None:
            phase=self.working_directories.phase
            self.ctth = mcaCalibrate2theta(self.mca, jcpds_directory=phase)
            if self.ctth.nrois < 1:
                mcaUtil.displayErrorMessage( 'calroi')
                self.ctth.destroy()
            else:
                self.ctth.raise_widget()
    
    def jcpds_module(self):
        if self.mca !=None:
            self.phase_controller.show_view()
    
    def roi_module(self):
        if self.mca !=None:
            self.roi_controller.show_view()
            
    def fluorescence_module(self):
        if self.mca !=None:
            self.fluorescence_controller.show()

    def pressure_module(self):
        self.roi_controller.pressure()

    def hklGen_module(self):
        self.hlkgen_controller.show_view()
        

    ########################################################################################
    ########################################################################################

    def roi_action(self, action):
        if self.mca != None:
            if action == 'add':
                if self.plotController.is_cursor_in_range():
                    #self.add_roi_btn()
                    mode = self.widget.btnROIadd.text()
                    #self.plotController.roi_construct(mode)
                    widths = {'E': 0.7, 'q': 0.1, 'Channel':20, 'd': 0.1}
                    if mode == 'Add':
                        self.widget.btnROIadd.setText("Set")
                        if self.unit in widths:
                            width = widths[self.unit]
                        else:
                            width = 2
                        self.plotController.roi_construct(mode,width=width)
                    else:
                        self.widget.btnROIadd.setText("Add")
                        reg = self.plotController.roi_construct(mode)
                        if reg is not None:
                            self.roi_controller.addROIbyChannel(reg[0],reg[1])
                else:
                    self.widget.btnROIadd.setChecked(False)
            elif action == 'delete':
                self.roi_controller.remove_btn_click_callback()
            elif action == 'clear':
                self.roi_controller.clear_rois()
            elif action == 'next':
                self.roi_controller.navigate_btn_click_callback('next')
            elif action == 'prev':
                self.roi_controller.navigate_btn_click_callback('prev')
            else: 
                pass
        else:
            if action == 'add':
                self.widget.btnROIadd.setChecked(False)

    def roi_selection_updated(self, text):
        self.widget.lineROI.setText(text)

    def xrf_action(self, action):
        if self.mca != None:
            if action == 'next':
                self.fluorescence_controller.navigate_btn_click_callback('next')
            elif action == 'prev':
                self.fluorescence_controller.navigate_btn_click_callback('prev')
            else: 
                pass

    def xrf_search(self, query):
        if self.mca != None:
            self.fluorescence_controller.search_by_symbol(query)

    ########################################################################################
    ########################################################################################

    def HorzScaleRadioToggle(self,b):
        if b.isChecked() == True:
            if self.widget.radioE.isChecked() == True:
                horzScale = 'E'
            elif self.widget.radioq.isChecked() == True:
                horzScale = 'q'
            elif self.widget.radioChannel.isChecked() == True:
                horzScale = 'Channel'
            elif self.widget.radiod.isChecked() == True:
                horzScale = 'd'
            self.set_unit(horzScale)

    def set_unit(self,unit):
            self.unit = unit
            if self.mca != None:
                self.plotController.set_unit(unit)

    def zoomPan(self, zoom):
        if zoom: setting = 1
        else: setting = 0
        self.setPlotMouseMode(setting)

    def setPlotMouseMode(self, mode):
        pg = self.widget.pg
        pg.setPlotMouseMode(mode)
        
    def setPlotLogMode(self, mode):
        if self.plotController != None:
            self.plotController.setLogMode([False, mode])
            self.overlay_controller.update_log_scale()
        pg = self.widget.pg   
        pg.set_log_mode(False, mode)
        
    def LogScaleSet(self):
        log_scale = self.widget.radioLog.isChecked()
        self.widget.baseline_subtract.setEnabled( log_scale==False)
        if log_scale:
            if self.widget.baseline_subtract.isChecked():
                self.widget.baseline_subtract.setChecked(False)
                self.baseline_subtract_callback()
        self.setPlotLogMode(log_scale)

    def baseline_subtract_callback(self):
        if self.plotController != None:

            baseline_state = self.widget.baseline_subtract.isChecked()
            self.mca.baseline_state = baseline_state
            self.plotController.updated_baseline_state()

        
    ########################################################################################
    ########################################################################################

    def mouseMoved(self, text):
        self.widget.indexLabel.setText(text)

    def mouseCursor(self, text):
        self.widget.cursorLabel.setText(text)

    ########################################################################################
    ########################################################################################    

    def setStyle(self, Style):
        #print('style:  ' + str(Style))
        if Style==1:
            WStyle = 'plastique'
            file = open(os.path.join(self.style_path, "stylesheet.qss"))
            stylesheet = file.read()
            self.app.setStyleSheet(stylesheet)
            file.close()
            self.app.setStyle(WStyle)
        else:
            WStyle = "windowsvista"
            self.app.setStyleSheet(" ")
            #self.app.setPalette(self.win_palette)
            self.app.setStyle(WStyle)
      
        
    ########################################################################################
    ########################################################################################
