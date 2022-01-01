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
import copy
import utilities.centroid
import numpy as np
import os
from hpm.widgets.CustomWidgets import FlatButton, DoubleSpinBoxAlignRight, VerticalSpacerItem, NoRectDelegate, \
    HorizontalSpacerItem, ListTableWidget, VerticalLine, DoubleMultiplySpinBoxAlignRight
from hpm.widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog
from hpm.widgets.RoiWidget import RoiWidget, plotFitWindow

from hpm.models.mcaModel import  McaROI
from PyQt5.QtCore import pyqtSignal, QObject

class RoiController(QObject):

    roi_updated_signal = pyqtSignal(int, str )  
    roi_selection_changed_signal = pyqtSignal(int,str)
    #rois_changed = pyqtSignal()  

    def __init__(self, mcaModel, plotWidget, plotController,mainController):
        super().__init__()
        
        self.set_mca(mcaModel)
        self.mcaController = mainController
        self.roi = []
        self.roi_sets = []
        self.rois_widget = RoiWidget()
        self.plot_fit_window = plotFitWindow()
        
        self.active = False
        self.plotFitOpen = False
        self.win = None
        self.fitPlot = None
        self.dataPlot = None
        self.fitPlots = None
        self.selectedROI = 0
        self.selectedROI_persist = 0
        self.roiLen = 0
        self.roiSetsLen = 0
        self.dataLen = self.mca.nchans
        self.pattern_widget = plotWidget
        self.plotController = plotController
        self.unit = 'E'
        self.unit_ = 'KeV'
        self.roi_cursor = []
        color = self.add_roi_cursor_plot()
        self.rois_widget.roi_tw.set_tw_header_unit(self.unit,self.unit_)
       
        #self.phases =dict()
        self.create_signals()
        

    def set_mca(self, mca):
        self.mca = mca
        self.calibration = self.mca.get_calibration()[0]

    def get_calibration(self):
        return self.calibration
        
    def create_signals(self):
        self.plotController.logScaleYUpdated.connect(self.update_log_y_scale)
        self.connect_click_function(self.rois_widget.delete_btn, self.remove_btn_click_callback)
        self.connect_click_function(self.rois_widget.clear_btn, self.clear_rois)
        self.connect_click_function(self.rois_widget.show_fit_btn, self.show_fit)
        self.connect_click_function(self.rois_widget.save_peaks_btn, self.save_peaks)
        

        self.rois_widget.widget_closed.connect(self.view_closed)
        self.rois_widget.roi_tw.currentCellChanged.connect(self.roi_selection_changed)
        self.rois_widget.show_cb_state_changed.connect(self.change_roi_use)
        self.rois_widget.roi_tw.name_item_changed.connect(self.edit_roi_name)

        self.plot_fit_window.widget_closed.connect(self.plot_fit_closed)
        self.rois_widget.key_signal.connect(self.key_sig_callback)

    def connect_click_function(self, emitter, function):
        emitter.clicked.connect(function)      

    def key_sig_callback(self, sig):
        if sig == 'delete' :
            self.remove_btn_click_callback()



    def save_peaks(self):
        img_filename, _ = os.path.splitext(os.path.basename(self.mca.name))
        filename = save_file_dialog(
            self.mcaController.widget, "Save ROI's Data.",
            os.path.join(self.mcaController.working_directories.savedata,
                        img_filename + '.csv'),
            ('Comma separated values (*.csv)'))
        if filename != '':
            self.mca.save_peaks_csv(filename)

    

    def show_view(self):
        self.active = True
        #self.update_rois()
        self.rois_widget.raise_widget()
        #print('roi view opened')
    def view_closed(self):
        self.active = False
        if self.plotFitOpen:
            self.plotFitOpen = False
            self.plot_fit_window.close()

    def update_log_y_scale (self, log_mode):
        self.update_roi_cursor_lines()

    def update_unit (self):
        self.unit_ = self.plotController.units[self.unit]
        unit = self.unit
        if unit == '2 theta':
            unit = u'2θ'
        self.rois_widget.roi_tw. set_tw_header_unit(unit,self.unit_)
        #self.update_rois(use_only=True)
        if self.fitPlots is not None:
            if self.plotFitOpen:
                cur_ind = self.rois_widget.roi_tw. get_selected_roi_row()
                if cur_ind >= 0 :
                    self.updateFitPlot(cur_ind)


    def update_set_rois (self, roi_sets, use_only=False):
        oldLen =  copy.copy(self.roiSetsLen)
        self.selectedROI_persist = copy.copy(self.selectedROI)
       

        newLen = len(roi_sets)
        self.nrois = len(roi_sets)
        self.blockSignals(True)
        self.rois_widget.roi_sets_tw.blockSignals(True)
        if newLen == oldLen:
            for name in roi_sets:
                index = roi_sets.index(name)
                
                self.update_roi_by_ind(index, name, True)
        else:
            while self.rois_widget.roi_sets_tw.rowCount() > 0:
                self.rois_widget.roi_sets_tw.del_roi(self.rois_widget.roi_sets_tw.rowCount()-1,silent=True)
            for name in roi_sets:
        
                self.rois_widget.roi_sets_tw.add_roi(name, True,  silent=True)
        self.blockSignals(False)              
        self.rois_widget.roi_sets_tw.blockSignals(False)    
        self.rois_widget.roi_sets_tw.blockSignals(False)      
        if self.selectedROI_persist<len(roi_sets):
            sel = np.clip(self.selectedROI_persist,0,31)
        else: 
            sel = len(roi_sets)-1
        self.rois_widget.roi_sets_tw. select_roi(sel) 
        self.selectedROI=sel
        
        

        self.roiSetsLen = copy.copy(self.nrois)
        if self.plotFitOpen:
            self.show_fit()

    def update_rois(self, use_only=False):
        oldLen =  copy.copy(self.roiLen)
        self.selectedROI_persist = copy.copy(self.selectedROI)
        unit =self.plotController.get_unit()
        if self.unit !=unit:
            self.unit=unit
            self.update_unit()
        self.calibration = self.mca.get_calibration()[0]
        if not use_only:
            self.roi = self.mca.get_rois()[0]
            sets = []
            for r in self.roi:
                name_base = r.label.split(' ')[0]
                if not name_base in sets:
                    sets.append(name_base)
            self.update_set_rois(sets)

        newLen = len(self.roi)
        self.nrois = len(self.roi)
        self.blockSignals(True)
        self.rois_widget.roi_tw.blockSignals(True)
        if newLen == oldLen:
            for r in self.roi:
                index = self.roi.index(r)
                centroid, fwhm, counts = self.get_roi_attributes(r, self.unit)
                self.update_roi_by_ind(index, r.use, r.label, '%.3f'%(centroid), '%.3f'%(fwhm), '%d'%(counts))
        else:
            while self.rois_widget.roi_tw.rowCount() > 0:
                self.rois_widget.roi_tw.del_roi(self.rois_widget.roi_tw.rowCount()-1,silent=True)
            for r in self.roi:
                centroid, fwhm, counts = self.get_roi_attributes(r, self.unit)
                self.rois_widget.roi_tw.add_roi(r.use, r.label, 
                                '%.3f'%(centroid), '%.3f'%(fwhm), self.roi.index(r),'%d'%(counts),  silent=True)
        self.blockSignals(False)              
        self.rois_widget.roi_tw.blockSignals(False)    
        self.rois_widget.roi_tw.blockSignals(False)      
        if self.selectedROI_persist<len(self.roi):
            sel = np.clip(self.selectedROI_persist,0,31)
        else: 
            sel = len(self.roi)-1
        self.rois_widget.roi_tw. select_roi(sel) 
        self.selectedROI=sel
        self.emit_rois_updated()
        

        self.roiLen = copy.copy(self.nrois)
        if self.plotFitOpen:
            self.show_fit()
        
     

    def get_roi_attributes(self, roi, unit):
        if self.unit == 'E': 
            centroid = roi.energy
            fwhm = roi.fwhm_E
        elif self.unit == 'q': 
            centroid = roi.q
            fwhm = roi.fwhm_q
        elif self.unit == 'd': 
            centroid = roi.d_spacing
            fwhm = abs(roi.fwhm_d)
        elif self.unit == '2 theta': 
            centroid = roi.two_theta
            fwhm = abs(roi.fwhm_tth)
        else: 
            centroid = roi.centroid
            fwhm = roi.fwhm
        try:
            counts = max(roi.counts)
        except:
            counts = 0
        return centroid, fwhm, counts

    def emit_rois_updated(self):
        selection = self.rois_widget.roi_tw. get_selected_roi_row()
        if selection >-1 and selection < len(self.roi):
            out = self.roi[selection].label
            
        else: 
            out = ''
        self.selectedROI = selection
        self.update_roi_cursor_lines()
        self.roi_updated_signal.emit(selection, out)

    def navigate_btn_click_callback(self, action=''):
        n=len(self.roi)
        if n >0:
            if action == 'next':
                move = 1
            elif action == 'prev':
                move = -1
            else:
                move = 0
            curr_ind = self.selectedROI 
            new_ind = curr_ind + move
            
            if new_ind >=0 and new_ind<n:
                pass
            else:  # enable loop-around
                if new_ind<0:
                    new_ind= n+new_ind
                else:
                    new_ind=new_ind-n
            if new_ind != curr_ind:
                self.rois_widget.roi_tw.select_roi(new_ind)    

    def roi_selection_changed(self, row, **kwargs):
        cur_ind = row
        self.selectedROI = row
        if self.plotFitOpen:
            self.updateFitPlot(cur_ind)
        if cur_ind >-1 and cur_ind < len(self.roi): 
            out = self.roi[cur_ind].label
               
        else: out = ''
        self.update_roi_cursor_lines() 
        self.roi_selection_changed_signal.emit(cur_ind, out)
        #print('selected: ' + str(cur_ind))

    def updateFitPlot(self,ind):
        if self.plotFitOpen:
            rois = self.roi
            if ind >=0 and len(rois)>0 and ind < len(rois):
                x = self.roi[ind].channels
                fit = self.roi[ind].yFit
                x_fit = self.roi[ind].x_yfit
                label = self.roi[ind].label
                if self.unit == 'E':
                    x_fit = self.calibration.channel_to_energy(x_fit)
                    x = self.calibration.channel_to_energy(x)
                elif self.unit == 'q':
                    x_fit = self.calibration.channel_to_q(x_fit)
                    x = self.calibration.channel_to_q(x)
                elif self.unit == 'd':
                    x_fit = self.calibration.channel_to_d(x_fit)
                    x = self.calibration.channel_to_d(x)
                elif self.unit == '2 theta':
                    x_fit = self.calibration.channel_to_tth(x_fit)
                    x = self.calibration.channel_to_tth(x)
                if label == '':
                    label = '#'+str(ind) 
                label = 'ROI '+label+' fit'
                counts = self.roi[ind].counts
            else:
                x_fit=[]
                fit=[]
                label=""
                x=[]
                counts=[]
            self.plot_fit_window.set_data(x_fit,fit,label,x,counts,self.unit,self.unit_)
            

    def show_fit(self):
        cur_ind = self.rois_widget.roi_tw. get_selected_roi_row()
        if not self.plotFitOpen:
            self.plot_fit_window.raise_widget()
            self.plotFitOpen = True
        self.updateFitPlot(cur_ind)    
    
    def plot_fit_closed(self):
        self.plotFitOpen = False


    def change_roi_use(self, ind, use):
        rois = self.roi
        if ind >=0 and len(rois)>0 and ind < len(rois):
            self.mca.change_roi_use(ind, use)  
            self.update_rois(use_only=True)
            
    def remove_btn_click_callback(self, *args, **kwargs):
        """
        Deletes the currently selected roi
        """
        ind = self.rois_widget.roi_tw. get_selected_roi_row()
        if ind >= 0:
            rois = self.roi
            if ind >=0 and len(rois)>0 and ind < len(rois):
                self.blockSignals(True)
                self.mca.delete_roi(ind,0)
                self.roi_removed(ind)
                self.roiLen = self.roiLen -1 
                self.blockSignals(False)
                self.update_rois()
                self.blockSignals(False)

    def roi_removed(self, ind):
        self.rois_widget.roi_tw. del_roi(ind)
        

    def clear_rois(self, *args, **kwargs):
        """
        Deletes all rois from the GUI
        """
        self.blockSignals(True)
        while self.rois_widget.roi_tw.rowCount() > 0:
            self.roi_removed(self.rois_widget.roi_tw.rowCount()-1)
        self.mca.clear_rois()
        self.roiLen = 0
        self.blockSignals(False)
        self.update_rois()


    def addROISbyE(self, e):
        E2C = self.get_calibration().energy_to_channel
        rois = []
        for roi in e:
            r={}
            ch=E2C(roi[0])
            hw=roi[1]
            lbl=roi[2]
            r['channel']=ch
            r['halfwidth']=hw
            r['label']=lbl
            rois.append(r)
        self.addReflections(rois)
        
    def addJCPDSReflections(self, reflections, phase):
        self.blockSignals(True)
        rois = []
        for r in reflections:
            rois.append(self.make_roi_by_channel(r['channel'],r['halfwidth'], \
                                                 r['label'],r['name'],r['hkl']))
        rois = self.validate_rois(rois)
        #self.phases[phase.name]=[rois,phase]
        self.mca.add_rois(rois, detector=0)
        self.blockSignals(False)
        self.update_rois()

    def validate_rois(self,rois):
        n = self.mca.nchans
        rois_valid = []
        for roi in rois:
            if roi is not None:
                l = roi.left
                r = roi.right
                if l >=0 and l< n and r >=0 and r< n:
                    rois_valid.append(roi)
        return rois_valid

    def addReflections(self, reflections):
        self.blockSignals(True)
        rois = []
        for r in reflections:
            rois.append(self.make_roi_by_channel(r['channel'],r['halfwidth'],r['label']))
        rois = self.validate_rois(rois)
        self.mca.add_rois(rois, detector=0)
        self.blockSignals(False)
        self.update_rois()

    def make_roi_by_channel(self, channel, halfWidth=10, label='', jcpds='',hkl=[]):
        cP = channel
        left = cP - halfWidth
        right = cP + halfWidth + 1
        dataLen = self.mca.nchans
        if left >= halfWidth and right <= dataLen-1-halfWidth:
            newRoi = McaROI(left,right,label=label)
            newRoi.jcpds_file = jcpds
            newRoi.hkl=hkl
            return newRoi
        return None

    def addROIbyChannel(self, channel, halfWidth=10, label=''):
        cP = channel
        left = cP - halfWidth
        right = cP + halfWidth + 1
        dataLen = self.mca.nchans
        if left >= halfWidth and right <= dataLen-1-halfWidth:
            newRoi = McaROI(left,right,label=label)
            self.mca.add_roi(newRoi, detector=0)
            ind = self.mca.find_roi(newRoi.left,newRoi.right)
            self.selectedROI = ind
            self.update_rois()

    def edit_roi_name(self, ind, name):
        rois = self.roi
        
        if ind >=0 and len(rois)>0 and ind < len(rois):
            self.mca.auto_process_rois = False
            curr_roi = rois[ind]
            curr_roi.label = name
            rois[ind] = curr_roi
            self.mca.set_rois(rois)
            self.mca.auto_process_rois = True
            self.update_rois()
                
    def update_roi_by_ind(self, ind, use, name, centroid, fwhm, counts):
        self.rois_widget.roi_tw. update_roi(ind, use, name, centroid, fwhm, counts)

    def roi_name_changed(self, ind, name):
        self.rois_widget.roi_tw. rename_roi(ind, name)




    ###############################################################
    #######  roi cursor stuff  ####################################

    def add_roi_cursor_plot(self):
        """
        Adds a roi_cursor to the Pattern view.
        :return:
        """
        label = ''
        positions = [0]
        intensities = [1]
        baseline = [1]
        color = self.pattern_widget.add_roi_cursor(label,
                                              positions,
                                              intensities,
                                              baseline)
        return color

    def show_state_changed(self, ind, state):
        if state:
            self.pattern_widget.show_roi_cursor(ind)
        else:
            self.pattern_widget.hide_roi_cursor(ind)
        pass

    def clear_roi_cursor(self):
        self.show_state_changed(0,False)

    def update_roi_cursor_lines(self):
        """
        """
        roi_ind = self.selectedROI
        if len(self.roi) < 1:
            roi_label = ''
            positions = 0
            intensities = 1
            baseline = 1
        else:
            axis_range = self.plotController.getRange()
            y_range = axis_range[1]
            y_max = np.amax(y_range)
            if y_max == 1:
                y_max = np.amax(self.plotController.mca.data[0])
            roi_height = y_max*1.1
            roi = self.roi[roi_ind]
            if self.unit == 'E':
                roi_position = roi.energy
            elif self.unit == 'q':
                roi_position = roi.q
            elif self.unit == 'd':
                roi_position = roi.d_spacing
            elif self.unit == 'Channel':
                roi_position = roi.centroid
            elif self.unit == '2 theta':
                roi_position = roi.two_theta

            roi_label = '%.4f' % (roi_position) + ' '  + self.unit_
            if roi.label != '':
                roi_label = roi_label + ', ' + roi.label 

            #x = self.roi[ind].channels
            #fit = self.roi[ind].yFit
            counts = self.roi[roi_ind].counts
            if len(counts)>0:
                intensities = np.amax(counts)
            else :
                intensities = 1
            baseline = intensities
            log_mode = self.plotController.get_log_mode_y()
            if log_mode:
                baseline = baseline*1.2
                intensities = intensities *3
            else:
                baseline=baseline+y_max*0.015
                intensities=intensities+y_max*0.1
            positions = roi_position
            if intensities <= 1:
                intensities = 1
            if baseline <= 1:
                baseline = 1
        self.pattern_widget.update_roi_cursor_intensities(
                                                    0, 
                                                    [positions], 
                                                    [intensities], 
                                                    [baseline])
        self.pattern_widget.rename_roi_cursor(0,roi_label)
    