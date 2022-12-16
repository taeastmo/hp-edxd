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


from fileinput import filelineno
import imp
from tkinter.messagebox import NO
import numpy as np
from scipy import interpolate
from PyQt5 import QtCore, QtWidgets
#from pyqtgraph.functions import pseudoScatter
import os
import time
import copy

from .mcareaderGeStrip import *
from .mcaModel import McaCalibration, McaElapsed, McaROI, McaEnvironment
from utilities.CARSMath import fit_gaussian
from .eCalModel import calc_parabola_vertex, fit_energies
from .mcaComponents import McaROI
import hpm.models.Xrf as Xrf

from hpm.models.MaskModel import MaskModel

class AnalysisStep(QtCore.QObject):
    updated = QtCore.pyqtSignal(np.ndarray)
    def __init__(self, name, data_in_dims, data_out_dims, mask=False):
        super().__init__()
        self.name = name

        self.params_in = {}
        self.params_out = {}

        self.function_inputs = {}
        self.function_outputs = {}

        self.params_in['data_in_dims'] = data_in_dims
        self.params_out['data_out_dims'] = data_out_dims

        self.params_in['mask'] = mask  # this is used only by the controller to determine what kind of widget is needed

        self.analysis_function = None
        self.processed = False

    def set_param(self, param_in):
        for param in param_in:
            self.params_in[param] = param_in[param]

    def set_function(self, f , inputs, outputs):
        self.analysis_function = f
        self.function_inputs = inputs
        self.function_outputs = outputs

    def calculate (self):
        if self.analysis_function is not None:

            data = self._get_function_params()
            out = self.analysis_function(**data)
            
            for param in self.function_outputs:
                self.params_out[param] = out[param]
            self.processed = True
            self.updated.emit(self.params_out['data_out'])

    def _get_function_params(self):
        out = {}
        for param in self.function_inputs:
            out[param] = self.params_in[param]
        return out

    def set_data_in(self, data):
        self.processed = False
        self.params_in['data_in'] = data
        self.params_in['mask_img'] = np.zeros(data.shape, dtype=bool)
        self.params_in['weights'] = np.ones(data.shape)

    def get_data_out(self):
        return self.params_out['data_out']

    def get_unit_out(self):
        return self.params_out['unit_out']

    def get_data_out_dims(self):
        return self.params_out['data_out_dims']

    def set_mask(self, mask):
        self.processed = False
        self.params_in['mask_img'] = mask

   

class AmorphousAnalysisModel(QtCore.QObject):  # 
    def __init__(self,  *args, **filekw):
        
        """
        Creates new Multiple Spectra object.  
    
        Example:
            m = MultipleSpectraModel()
        """
        self.mca = None
        self.multi_spectra_model =  None

        self.steps = {}
        self.make_calculators()

    def set_models(self, mca, multi_spectra_model):
        
        self.mca = mca
        self.multi_spectra_model = multi_spectra_model



    def clear(self):
        self.__init__()

    def make_calculators(self):
        pass
        # this is a placeholder for the eventual calculation
        # List of the steps needed for the calculation
        # 1. Convert dataset to E
        # 2. apply mask in E (punch and fill any peaks)
        # 3. Flaten to 1D (np.mean, axis=0) , this is now the estimated beam profile
        # 4. Normalize the original dataset in E by the estimated beam profile
        # 5. convert to q
        # 6. apply any mask in q (punch and fill any peaks)
        # 7. calculate 2-theta-dependent scaling factors by looking at consecutive brightness of the nearby rows
        # 8. Flaten to 1D (np.mean, axis=0), this is now the estimated Iq (flattening is weighted and masked )
        # 9. convert Iq to E for each row
        #10. normalize dataset in E by Iq, remember to scale Iq for each row by 2-theta-dependent scaling factors
        #11. Flaten to 1D (np.mean, axis=0) , this is now the estimated beam profile

        # repeat steps 4. to 11. 
    
        # .. convert Iq to Sq by applying scattering factors correction


        steps = {}
        steps[1] = AnalysisStep('dataset E',2,2)
        steps[2 ] = AnalysisStep('mask in E',2,2,mask=True)
        steps[3 ] = AnalysisStep('Flaten',2,1)
        steps[4 ] = AnalysisStep('Normalize ',2,2)
        steps[5 ] = AnalysisStep('convert to q',2,2)
        steps[6 ] = AnalysisStep('mask in q',2,2,mask=True)
        steps[7 ] = AnalysisStep('2-th scaling',2,1)
        steps[8 ] = AnalysisStep('Flaten ',2,1)
        steps[9 ] = AnalysisStep('Iq to E', 1,2)
        steps[10] = AnalysisStep('normalize E by Iq',2,2)
        steps[11] = AnalysisStep('Flaten', 2,1)

        steps[1].set_function(self._propagate_data, ['data_in'],  ['data_out'])
        steps[2].set_function(self._propagate_data, ['data_in'],  ['data_out'])
        steps[3].set_function(self._flaten_data, ['data_in', 'unit_in','scale_in', 'mask_img','weights'],  ['data_out'])
        steps[4].set_function(self._normalize, ['data_in', 'norm_function'],  ['data_out'])
        steps[5].set_function(self._rebin, ['data_in', 'unit_in', 'unit_out', 'mask_img'],  ['data_out', 'mask_out'])

        steps[8].set_function(self._flaten_data, ['data_in', 'unit_in','scale_in', 'mask_img','weights'],  ['data_out'])

        self.steps = steps

    def calculate(self):

        self.multi_spectra_model.rebin_scale('E') 
        self.multi_spectra_model.rebin_scale('q') 

        scale_E = self.multi_spectra_model.E_scale
        scale_q = self.multi_spectra_model.q_scale
        
        data_in_E = copy.deepcopy(self.multi_spectra_model.E)
        data_in_q = copy.deepcopy(self.multi_spectra_model.q)
        data_in_E[:,:69] = 0

        self.steps[1].set_data_in(data_in_E)
        self.steps[1].calculate()
        self.steps[2].set_data_in(self.steps[1].get_data_out())
        self.steps[2].calculate()

        self.steps[3].set_data_in(self.steps[2].get_data_out())
        self.steps[3].set_param({'unit_in':'E','scale_in':scale_E})
        self.steps[3].calculate()

        self.steps[4].set_data_in(self.steps[2].get_data_out())
        self.steps[4].set_param({'norm_function':self.steps[3].get_data_out()[1]})
        self.steps[4].calculate()

        self.steps[5].set_data_in(self.steps[4].get_data_out())
        self.steps[5].set_param({'unit_in':'E', 'unit_out':'q'})
        self.steps[5].calculate()

        self.steps[8].set_data_in(self.steps[5].get_data_out())
        weights_q = data_in_q/ np.amax(data_in_q)
        weights_q [weights_q==0 ] = 1e-7
        self.steps[8].set_param({'weights':weights_q, 'unit_in':'q','scale_in':scale_q})
        self.steps[8].calculate()

 
    def _propagate_data(self, **args):
        data = args['data_in']
        args['data_out'] = data
        return args

  
    def _flaten_data(self, **args):

        # Compute the average beam profile by averaging all the rows while in energy space. 
        # Then, convert that average profile to q space then you can use that to 
        # normalize all of the data rows.
        # do a weighted average because the high energy / low energy bins will be more noisy 
        data = args['data_in']
        unit = args['unit_in']
        mask = args['mask_img']
        scale = args['scale_in']
        weights = args['weights']
        y = np.average(np.ma.array(data, mask=mask), weights= weights, axis=0 )
        if unit == 'E':
            scale = self.multi_spectra_model.E_scale
        elif unit == 'q':
            scale = self.multi_spectra_model.q_scale
        x = np.arange(len(y)) * scale[0] + scale[1]
        args['data_out'] = np.asarray([x, y])
        return args

    def _normalize(self, **args):
        data = args['data_in']
        out = np.zeros(data.shape)
        norm_function = args['norm_function']
        norm_function[norm_function==0]= np.amin(norm_function[norm_function!=0])
        for i in range(np.shape(data)[0]):
           out[i] = data[i] / norm_function
        args['data_out'] = out
        return args

    def _rebin(self, **args):
        data = args['data_in']
        unit = args['unit_out']
        mask = args['mask_img']
        new_mask = copy.deepcopy(mask)
        new_data = np.ones(data.shape)
        out = np.zeros(data.shape)

        self._rebin_scale(data, new_data, mask, new_mask, 'Channel', unit)
        
        args['data_out'] = new_data
        args['mask_out'] = new_mask
        return args

    def is2thetaScan(self):
        '''
        Returns True if the mca is a 2theta scan, i.e. each element (detector) is collected 
        at a different 2theta. Otherwise returns False. Essentially checks if 
        the 2theta for each element is diffetent. 
        '''
        pass

    def energy_to_2theta(self):
        '''
        transposes the 2D dataset, converts from 2D EDX to 2D ADX
        '''
        data_t = np.transpose(self.data)
        s = np.shape(data_t)
        n_det = s[0]
        n_cnan = s[1]
        cal_t = []
        cal = McaCalibration()
        
        cal.slope = self.tth_scale[0]
        cal.offset = self.tth_scale[1]
        cal.set_dx_type('adx')
        for det in range(n_det):
            cal_t.append(copy.deepcopy(cal))
     
        print(len(cal_t))

    def _rebin_scale(self, data, new_data, mask, new_mask, scale, new_scale):
        
        rows = len(data)
        tth = np.zeros(rows)
        bins = np.size(data[0])
        x = np.arange(bins)
        calibrations = self.mca.get_calibration()
        rebinned_scales = []
    
        if new_scale == 'q':
            for row in range(rows):
                calibration = calibrations[row]
                q = calibration.channel_to_q(x)
                tth[row]= calibration.two_theta
                rebinned_scales.append(q)
        elif new_scale == 'E':
            for row in range(rows):
                calibration = calibrations[row]
                e = calibration.channel_to_energy(x)
                tth[row]= calibration.two_theta
                rebinned_scales.append(e)
        tth_min = np.amin(tth)
        tth_max = np.amax(tth)
        if tth_max != tth_min:
            tth_step = (tth_max-tth_min)/rows
            self.tth_scale = [tth_step, tth_min]

        rebinned_scales = np.asarray(rebinned_scales)
        rebinned_min = np.amin( rebinned_scales)
        rebinned_max = np.amax(rebinned_scales)
     
        rebinned_step = (rebinned_max-rebinned_min)/bins
        if new_scale == 'q':
            self.q_scale = [rebinned_step, rebinned_min]
        elif new_scale == 'E':
            self.E_scale = [rebinned_step, rebinned_min]
        rebinned_new = [x*rebinned_step+rebinned_min]*rows
        self.align_multialement_data(data, new_data, rebinned_scales,rebinned_new )

        self.align_multialement_data(mask, new_mask , rebinned_scales,rebinned_new ,kind='nearest')
        
    def rebin_scratch(self, scale, new_scale):
        
        if new_scale == 'q':
            data = self.scratch_E
            new_data = self.scratch_q
            mask = self.mask_model._mask_data_E
            new_mask = self.mask_model._mask_data_q
       
        elif new_scale == 'E':
            data = self.scratch_q
            new_data = self.scratch_E
            mask = self.mask_model._mask_data_q
            new_mask = self.mask_model._mask_data_E
            
        self._rebin_scale(data, new_data, mask, new_mask, scale, new_scale)

    def rebin_scale(self, new_scale='q'):
        data = self.data
        mask = self.mask_model._mask_data
        if new_scale == 'q':
            new_data = self.q
            new_mask = self.mask_model._mask_data_q
       
        elif new_scale == 'E':
            new_data = self.E
            new_mask = self.mask_model._mask_data_E
            
        self._rebin_scale(data, new_data, mask, new_mask, 'Channel', new_scale)

    def rebin_channels(self, order = 1):
        # This is useful for the germanium strip detector data, 
        # where the rows have to be aligned before processing
        
        data = self.data
        bins = np.size(data[0])
        x =  np.arange(bins)
        rows = len(data)
        new_scales = [x]*rows
        if not len(self.channel_calibration_scales):
            
            now = time.time()
            
            range_1 = (667,1100)
            range_2 = (3000,3480)
            range_3 = (2600,3000)

            max_points_left = np.zeros(rows)
            max_points_right = np.zeros(rows)
            max_points_middle= np.zeros(rows)

            fit_range = 20
            for row in range(rows):
                max_rough = int(range_1[0]+ np.argmax(data[row][slice(*range_1)]))
                if max_rough == 0:
                    continue
                fit_segment_x = x[max_rough-fit_range:max_rough+fit_range]
                fit_segment_y = data[row][max_rough-fit_range:max_rough+fit_range]
                min_y = np.amin(fit_segment_y)
                _ , centroid,_ = fit_gaussian(fit_segment_x,fit_segment_y - min_y)
                max_points_left[row] = centroid

                max_rough = int(range_2[0] + np.argmax(data[row][slice(*range_2)]))
                fit_segment_x = x[max_rough-fit_range:max_rough+fit_range]
                fit_segment_y = data[row][max_rough-fit_range:max_rough+fit_range]
                min_y = np.amin(fit_segment_y)
                _ , centroid,_ = fit_gaussian(fit_segment_x,fit_segment_y- min_y)
                max_points_right[row] = centroid

                if order == 2:
                    max_rough = int(range_3[0] + np.argmax(data[row][slice(*range_3)]))
                    fit_segment_x = x[max_rough-fit_range:max_rough+fit_range]
                    fit_segment_y = data[row][max_rough-fit_range:max_rough+fit_range]
                    min_y = np.amin(fit_segment_y)
                    _ , centroid,_ = fit_gaussian(fit_segment_x,fit_segment_y- min_y)
                    max_points_middle[row] = centroid
            
            max_points_left_ =  max_points_left[max_points_left != 0]
            max_points_right_ = max_points_right[max_points_right != 0]
            max_points_middle_ = max_points_middle[max_points_middle != 0]
            left = np.mean(max_points_left_)
            right = np.mean(max_points_right_)
            middle = np.mean(max_points_middle_)
        
            slope = np.ones(rows)   # relative slopes
            offset = np.zeros(rows)  # relative y-intercepts
            quad = np.zeros(rows)  # quad coefficient

            slope_inv = np.ones(rows)   # relative slopes
            offset_inv = np.zeros(rows)  # relative y-intercepts
            quad_inv = np.zeros(rows)  # quad coefficient
            
            for row in range(rows):
                if max_points_left[row] == 0:
                    continue
                x1 = left
                x2 = right
                
                y1 = max_points_left[row]
                y2 = max_points_right[row]
                
                if order == 1:
                    slope[row] = (y1-y2)/(x1-x2)
                    offset[row] = (x1*y2 - x2*y1)/(x1-x2)
                    slope_inv[row] = (x1-x2)/(y1-y2)
                    offset_inv[row] = (y1*x2 - y2*x1)/(y1-y2)
                elif order == 2:
                    x3 = middle
                    y3 = max_points_middle[row]
                    quad[row],slope[row],offset[row] = calc_parabola_vertex(x1,y1,x2,y2,x3,y3)
                    quad_inv[row],slope_inv[row],offset_inv[row] = calc_parabola_vertex(y1,x1,y2,x2,y3,x3)

            calibration = {}
            calibration['slope'] = slope
            calibration['offset'] = offset
            calibration['quad'] = quad
            calibration_inv = {}
            calibration_inv['slope'] = slope_inv
            calibration_inv['offset'] = offset_inv
            calibration_inv['quad'] = quad_inv
            self.calibration = calibration
            self.calibration_inv = calibration_inv

            self.channel_calibration_scales = self.create_multialement_alighment_calibration(data, calibration)
       
        self.align_multialement_data(data , self.rebinned_channel_data, new_scales, self.channel_calibration_scales )
        
    def create_multialement_alighment_calibration(self, data, calibration):
        rows = len(data)
        bins = np.size(data[0])
        x = np.arange(bins)
        slope = calibration['slope']
        offset = calibration['offset']
        quad = calibration['quad']
        calibration_scales = []
        for row in range(rows): 
            xnew = x * slope[row] + offset[row]
            if quad[row] != 0:
                xnew = xnew + quad[row] * x * x
            calibration_scales.append(xnew)
        return calibration_scales
            
    def align_multialement_data (self,  data, new_data, old_scales, new_scales, kind='linear'):
        rows = len(data)
        
        bins = np.size(data[0])
        x = np.arange(bins)
        for row in range(rows): 
            x = old_scales[row]
            xnew = new_scales[row]
            new_data[row] = self.shift_row(data[row],x, xnew, kind)
        

    def shift_row(self, row,x, xnew, kind='linear'):
        f = interpolate.interp1d(x, row, assume_sorted=True, bounds_error=False, fill_value=0, kind=kind)
        row = f(xnew)
        return row



    def aligned_to_channel(self, aligned, row):
        slope = self.calibration['slope'][row]
        offset = self.calibration['offset'][row]
        channel = aligned * slope + offset
        quad = self.calibration['quad'][row]
        if quad != 0:
            channel = channel + quad * aligned * aligned
        return channel

    def channel_to_aligned(self, channel, row):
        slope = self.calibration_inv['slope'][row]
        offset = self.calibration_inv['offset'][row]
        aligned = channel * slope + offset
        quad = self.calibration_inv['quad'][row]
        if quad != 0:
            aligned = aligned + quad * channel * channel
        return aligned

    def make_aligned_rois(self, row, rois):
        
        all_new_rois = []
        for roi in rois:
            left = roi.left
            right = roi.right
            aligned_left = self.channel_to_aligned(left, row)
            aligned_right = self.channel_to_aligned(right, row)
            roi.left = aligned_left
            roi.right = aligned_right
        for det in range(self.mca.n_detectors):
            new_rois = []
            for roi in rois:
                aligned_left = roi.left
                aligned_right = roi.right
                left = int(round(self.aligned_to_channel(aligned_left,det)))
                right = int(round(self.aligned_to_channel(aligned_right,det)))
                new_roi = McaROI(left,right,label = roi.label)
                new_rois.append(new_roi)
            all_new_rois.append(new_rois)
        return all_new_rois

    def calibrate_all_elements(self, order = 1):
        calibration = self.mca.get_calibration()
        all_rois = self.mca.get_rois()
        det0_rois = all_rois[0]
        energies = []
        for r in det0_rois:
            energy = Xrf.lookup_xrf_line(r.label)
            if (energy == None):
                energy = Xrf.lookup_gamma_line(r.label)
            if (energy != None): 
                energies.append( energy)
        for det in range(self.mca.n_detectors):
            cal = calibration[det]
            rois = all_rois[det]
            for i, roi in enumerate(rois):
                roi.energy = energies[i]
            fit_energies(rois, order,cal)
