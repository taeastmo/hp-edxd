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
#import imp
#from this import d
'''from tkinter import N
from tkinter.messagebox import NO'''
import numpy as np
from scipy import interpolate
from PyQt5 import QtCore, QtWidgets
#from pyqtgraph.functions import pseudoScatter
import os
import time
import copy
from scipy.ndimage import gaussian_filter
from scipy.ndimage import zoom

from .mcareaderGeStrip import *
from .mcaModel import McaCalibration, McaElapsed, McaROI, McaEnvironment
from utilities.CARSMath import fit_gaussian
from .eCalModel import calc_parabola_vertex, fit_energies
from .mcaComponents import McaROI
import hpm.models.Xrf as Xrf

from hpm.models.MaskModel import MaskModel

from .. import resources_path

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
        #self.params_in['mask_img'] = np.zeros(data.shape, dtype=bool)
        #self.params_in['weights'] = np.ones(data.shape)

    def get_data_out(self):
        return self.params_out['data_out']

    def get_unit_out(self):
        return self.params_out['unit_out']

    def get_data_out_dims(self):
        return self.params_out['data_out_dims']

    def load_mask(self, filename):
        self.processed = False
     
        if 'mask_model' in self.params_in:
            mask_model = self.params_in['mask_model']
            data = self.params_in['data_in']
            mask_model.set_dimension(data.shape)
            mask_model.load_mask(filename)

            mask = mask_model.get_mask()
            self.params_in['mask_img'] = mask

    def set_mask(self, mask):
        self.processed = False
        self.params_in['mask_img'] = mask
        if 'mask_model' in self.params_in:
            mask_model = self.params_in['mask_model']
            mask_model.set_dimension(mask.shape)
            mask_model.set_mask(mask)

    def get_mask(self):
        mask = self.params_in['mask_img']
        if 'mask_model' in self.params_in:
            mask_model = self.params_in['mask_model']
            mask = mask_model.get_mask()
        return mask


class AmorphousAnalysisModel(QtCore.QObject):  # 
    def __init__(self,  *args, **filekw):
        
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
        self.defs = [('dataset E',2,2),
                ('mask in E',2,2,True),
                ('blur',2,2),
                ('Flaten 1',2,1),
                ('unFlaten 1',1,2),
                ('Normalize',2,2),
                
                ('convert to q',2,2),
                ('convert to q Ieff',1,2),
                ('mask in q',2,2,True),
                ('weights q',2,2),
                ('get row scale',2,1),
                ('apply scaling',2,2),
                ('S(q)',2,1),
                ('Iq to E', 1,2),
                ('normalize by Iq',2,2),
                
                
                #('apply scaling 2',2,2),
                #('apply scaling 3',2,2),
                ('Flaten 3',2,1),
                ]
        for i, d in enumerate(self.defs):

            steps[d[0]] = AnalysisStep(*d)
        
        steps['dataset E'].set_function(self._propagate_data, ['data_in'],  ['data_out'])
        steps['mask in E'].set_function(self._propagate_data, ['data_in'],  ['data_out'])
        steps['blur'].set_function(self._bin, ['data_in', 'sigma', 'scaling_factor'],  ['data_out'])
        steps['Flaten 1'].set_function(self._flaten_data, ['data_in', 'range','unit_in','scale_in', 'mask_img','weights'],  ['data_out'])
        steps['unFlaten 1'].set_function(self._unflaten_data, ['data_in', 'rows'],  ['data_out'])
        
        
        steps['Normalize'].set_function(self._normalize, ['data_in', 'mask_img', 'norm_function'],  ['data_out'])
        
        #steps['mask in E'].set_function(self._propagate_data, ['data_in'],  ['data_out'])
        steps['convert to q'].set_function(self._rebin, ['data_in', 'unit_in', 'unit_out', 'mask_img'],  ['data_out', 'mask_out'])
        steps['convert to q Ieff'].set_function(self._rebin, ['data_in', 'unit_in', 'unit_out', 'mask_img'],  ['data_out', 'mask_out'])
        steps['mask in q'].set_function(self._propagate_data, ['data_in'],  ['data_out'])
        
        steps['weights q'].set_function(self._propagate_data, ['data_in'],  ['data_out'])
        steps['get row scale'].set_function(self._get_row_scale, ['data_in', 'mask_img','weights'],  ['data_out'])
        steps['apply scaling'].set_function(self._apply_row_scale, ['data_in', 'row_scale_in'],  ['data_out'])

        #steps['Flaten 2'].set_function(self._flaten_data, ['data_in',  'range','unit_in','scale_in', 'mask_img','weights'],  ['data_out'])
        steps['Iq to E'].set_function(self._q_to_channel, ['data_in'],  ['data_out'])

        steps['normalize by Iq'].set_function(self._normalize_3d, ['data_in','mask_img', 'norm_function'],  ['data_out'])
        steps['S(q)'].set_function(self._flaten_data, ['data_in',  'range','unit_in','scale_in', 'mask_img','weights'],  ['data_out'])

        #steps['scale dataset E'].set_function(self._apply_row_scale, ['data_in', 'row_scale_in'],  ['data_out'])
        steps['Flaten 3'].set_function(self._flaten_data, ['data_in',  'range','unit_in','scale_in', 'mask_img','weights'],  ['data_out'])
        #steps['apply scaling 2'].set_function(self._apply_row_scale, ['data_in', 'row_scale_in'],  ['data_out'])
        #steps['apply scaling 3'].set_function(self._apply_row_scale, ['data_in', 'row_scale_in'],  ['data_out'])

        
        #steps['S(q) corr'].set_function(self._flaten_data, ['data_in',  'range','unit_in','scale_in', 'mask_img','weights'],  ['data_out'])

        #steps['convert to q corr'].set_function(self._rebin, ['data_in', 'unit_in', 'unit_out', 'mask_img'],  ['data_out', 'mask_out'])
        

        self.steps = steps

    def calculate_1(self):

        self.multi_spectra_model.rebin_scale('E') 
        self.multi_spectra_model.rebin_scale('q') 

        self.scale_E = self.multi_spectra_model.E_scale
        self.scale_q = self.multi_spectra_model.q_scale

       
        
        self.data_in_E = copy.deepcopy(self.multi_spectra_model.E )
    
        self.data_in_q = copy.deepcopy(self.multi_spectra_model.q )
   
        #self.data_in_E[:,:600] = 0

        for step in (1,2,3,4,5,6,7,8,9,10,11,12, 13):
            self._calculate_step(step)

    def calculate_2(self):
        for step in (14,):
            self._calculate_step(step)

    def calculate_3(self):
        for step in (5, 6,15,10,11,12, 13):
            self._calculate_step(step)

    def calculate_4(self):
        for step in (1,):
            self._calculate_step(step)

    def calculate_5(self):
        for step in (7,8,9,10,11, 12, 13):
            self._calculate_step(step)
        

    def _calculate_step(self, step):
        if step == 1:
            self.steps['dataset E'].set_data_in(self.data_in_E)
            self.steps['dataset E'].calculate()
        elif step == 2:
            data = self.steps['dataset E'].get_data_out()
            self.steps['mask in E'].set_data_in(data)
            mask = np.zeros(data.shape) == 1
            mask[:,:1200] = True
            mask[:,3450:] = True
            
            self.steps['mask in E'].set_mask(mask)
            self.steps['mask in E'].calculate()

            self.steps['blur'].set_data_in(data)
            self.steps['blur'].set_param({'sigma':10, 'scaling_factor':10})
            self.steps['blur'].set_mask(mask)
            self.steps['blur'].calculate()
        
        elif step == 3:
            data = self.steps['blur'].get_data_out()
            rows = data.shape[0]
            self.steps['Flaten 1'].set_data_in(data)

            mask = self.steps['mask in E'].get_mask()
            weights_E = np.ones(data.shape)

            self.steps['Flaten 1'].set_param({'mask_img':mask, 'range':(80,rows-1)})
            self.steps['Flaten 1'].set_param({'unit_in':'E','scale_in':self.scale_E, 'weights':weights_E})
            self.steps['Flaten 1'].calculate()


            flattened = self.steps['Flaten 1'].get_data_out()[1]
            self.steps['unFlaten 1'].set_data_in(flattened)
            self.steps['unFlaten 1'].set_param({'rows':rows})
            self.steps['unFlaten 1'].calculate()
            
        elif step == 4:
            data = self.steps['mask in E'].get_data_out()
            
            self.steps['Normalize'].set_data_in(data)
            mask = self.steps['mask in E'].get_mask()
            self.steps['Normalize'].set_param({'mask_img':mask})
            norm_function = self.steps['Flaten 1'].get_data_out()[1] 
            self.steps['Normalize'].set_param({'norm_function':norm_function})
            self.steps['Normalize'].calculate()
        elif step == 5:
            self.steps['convert to q'].set_data_in(self.steps['Normalize'].get_data_out())
            mask = self.steps['mask in E'].get_mask()
            self.steps['convert to q'].set_param({'mask_img':mask})
            self.steps['convert to q'].set_param({'unit_in':'E', 'unit_out':'q'})
            self.steps['convert to q'].calculate()

            self.steps['convert to q Ieff'].set_data_in(self.steps['unFlaten 1'].get_data_out())
            mask = self.steps['mask in E'].get_mask()
            self.steps['convert to q Ieff'].set_param({'mask_img':mask})
            self.steps['convert to q Ieff'].set_param({'unit_in':'E', 'unit_out':'q'})
            self.steps['convert to q Ieff'].calculate()

        elif step == 6:
            

            data = self.steps['convert to q'].get_data_out()
            self.steps['mask in q'].set_data_in(data)
            
            mask = np.zeros(data.shape) == 1
            #self.steps['mask in q'].load_mask('/Users/ross/GitHub/hp-edxd/hpm/resources/q.mask')
            self.steps['mask in q'].set_mask(mask)
            self.steps['mask in q'].calculate()   

        elif step == 7:
           
            w_q = self.steps['convert to q Ieff'].get_data_out()
            
            w_q = w_q / np.amax(w_q)
            mask = self.steps['mask in q'].get_mask()
            w_q [w_q==0 ] = 1e-9
            
            self.steps['weights q'].set_data_in(w_q)
            self.steps['weights q'].calculate()

            self.steps['get row scale'].set_data_in(self.steps['mask in q'].get_data_out())
            
            self.steps['get row scale'].set_param({'mask_img':mask})
            
            self.steps['get row scale'].set_param({'weights':w_q, 'unit_in':'q','scale_in':self.scale_q})
            self.steps['get row scale'].calculate()

        elif step == 8:
            self.steps['apply scaling'].set_data_in(self.steps['mask in q'].get_data_out())
     
            row_scale_in = self.steps['get row scale'].get_data_out()
            self.steps['apply scaling'].set_param({'row_scale_in':row_scale_in})
            self.steps['apply scaling'].calculate()    

        elif step == 9:

            data = self.steps['apply scaling'].get_data_out()
            rows = data.shape[0]
            self.steps['S(q)'].set_data_in(data)

            mask = self.steps['mask in q'].get_mask()
            self.steps['S(q)'].set_param({'mask_img':mask, 'range':(4,rows-1)})
            
            w_q = self.steps['weights q'].get_data_out()
            
            self.steps['S(q)'].set_param({'weights':w_q, 'unit_in':'q','scale_in':self.scale_q})
            self.steps['S(q)'].calculate()
            
        elif step == 10:
            self.steps['Iq to E'].set_data_in(self.steps['S(q)'].get_data_out())
            self.steps['Iq to E'].calculate()

        elif step == 11:
            self.steps['normalize by Iq'].set_data_in(self.steps['mask in E'].get_data_out())
            mask = self.steps['mask in E'].get_mask()
            self.steps['normalize by Iq'].set_param({'mask_img':mask})
            self.steps['normalize by Iq'].set_param({'norm_function':self.steps['Iq to E'].get_data_out()})
            self.steps['normalize by Iq'].calculate()

        elif step == 12:
            
            """self.steps['apply scaling 2'].set_data_in(self.steps['normalize by Iq'].get_data_out())
            row_scale_in = self.steps['get row scale'].get_data_out()
            self.steps['apply scaling 2'].set_param({'row_scale_in':row_scale_in})
            self.steps['apply scaling 2'].calculate()   """ 

            '''self.steps['apply scaling 3'].set_data_in(self.steps['dataset E'].get_data_out())
            row_scale_in = self.steps['get row scale'].get_data_out()
            self.steps['apply scaling 3'].set_param({'row_scale_in':row_scale_in})
            self.steps['apply scaling 3'].calculate()   ''' 

        elif step == 13:
            data = self.steps['normalize by Iq'].get_data_out()
            rows = data.shape[0]
            self.steps['Flaten 3'].set_data_in(data)

            mask = self.steps['mask in E'].get_mask()
            self.steps['Flaten 3'].set_param({'mask_img':mask, 'range':(20,rows-1)})

            weights = np.ones(data.shape)

            self.steps['Flaten 3'].set_param({'unit_in':'E','scale_in':self.scale_E, 'weights':weights})
            self.steps['Flaten 3'].calculate()


        elif step == 14:

            data = self.steps['mask in E'].get_data_out()
            
            self.steps['Normalize'].set_data_in(data)
            mask = self.steps['mask in E'].get_mask()
            self.steps['Normalize'].set_param({'mask_img':mask})
            norm_function = self.steps['Flaten 3'].get_data_out()[1] 
            self.steps['Normalize'].set_param({'norm_function':norm_function})
            self.steps['Normalize'].calculate()

       
        
        elif step == 15:
            data = self.steps['convert to q'].get_data_out()
            rows = data.shape[0]
            self.steps['S(q)'].set_data_in(data)

            mask = self.steps['mask in q'].get_mask()
            self.steps['S(q)'].set_param({'mask_img':mask, 'range':(0,rows-1)})
            
            w_q = self.steps['weights q'].get_data_out()
            
            self.steps['S(q)'].set_param({'weights':w_q, 'unit_in':'q','scale_in':self.scale_q})
            self.steps['S(q)'].calculate()
 
    def _propagate_data(self, **args):
        # propagates data_in to data_out
        data = args['data_in']
        args['data_out'] = data
        return args

    def _mask_zeros(self, **args):
        data = args['data_in']
        mask = data == 0
        args['mask_img'] = mask
        args['data_out'] = data
        return args

    def _unflaten_data(self, **args):

        # copy a 2d data to all rows, making it 3D
        data = args['data_in']
        rows = args['rows']
        out = np.zeros((rows,len(data)))
        for row in range(rows):
            out[row,:] = data
        args['data_out'] = out
        return args
  
    def _flaten_data(self, **args):

        # Compute the average beam profile by averaging all the rows while in energy space. 
        # Then, convert that average profile to q space then you can use that to 
        # normalize all of the data rows.
        # do a weighted average because the high energy / low energy bins will be more noisy 
        
        rng = args['range']
        data = args['data_in'][rng[0]:rng[1]]
        unit = args['unit_in']
        mask = args['mask_img'][rng[0]:rng[1]]
        scale = args['scale_in']
        weights = args['weights'][rng[0]:rng[1]]
        
        not_mask = np.logical_not(mask)
        reduced_not_mask = np.logical_or.reduce(not_mask, axis=0)
        reduced_mask = np.logical_not(reduced_not_mask)

        weights = np.ma.array(weights, mask=mask)
        y = np.ma.array( np.average(np.ma.array(data, mask=mask), weights= weights, axis=0 ), mask = reduced_mask)
        y[reduced_mask] = 0
        if unit == 'E':
            scale = self.multi_spectra_model.E_scale
        elif unit == 'q':
            scale = self.multi_spectra_model.q_scale

        #l,r = self.find_non_zero_range(y)
        #y[:l]=y[l]
        
        x = np.arange(len(y)) * scale[0] + scale[1]
        args['data_out'] = np.asarray([x, y])
        return args

    def _normalize(self, **args):
        # divides each row in the data_in (2D) by the norm_function (2D)
        data = args['data_in']
        mask = args['mask_img']
        data = np.ma.array( data, mask = mask)
        
        out = np.zeros(data.shape)
        norm_function = args['norm_function']
        norm_function[norm_function==0]= np.amin(norm_function[norm_function!=0])
        for i in range(np.shape(data)[0]):
           out[i] = data[i] / norm_function
        out [mask] = 0
        args['data_out'] = out
        return args

    def _subtract_3d(self, **args):
        # divides each row in the data_in (3D) by the norm_function (3D)
        data = args['data_in']
        
        subtract_data = args['subtract_data']
        
        out = data - subtract_data 
        out [out<=0] = 1e-7
        args['data_out'] = out
        return args    

    def _normalize_3d(self, **args):
        # divides each row in the data_in (3D) by the norm_function (3D)
        data = args['data_in']
        mask = args['mask_img']
        norm_function = args['norm_function']
        norm_function[norm_function<0.01]= 1
        
        out = data / norm_function
        out [ mask] = 0
        args['data_out'] = out
        return args

    @staticmethod
    def find_non_zero_range(a):
        # Find the indices of the non-zero elements
        nonzero_indices = np.flatnonzero(a)
        # Find the index of the maximum value among the non-zero indices
        last_nonzero_index = np.amax(nonzero_indices)
        # Find the index of the minimum value among the non-zero indices
        first_nonzero_index = np.amin(nonzero_indices)
        return first_nonzero_index, last_nonzero_index

    def _get_row_scale(self, **args):
        # calculates the relative scaling of rows with the last row having the scale value of 1
        # uses masked and weighted scaling or adjecent rows
        # the weights are the normalized counts of the Im
        data = args['data_in']
        mask = args['mask_img']
        weights = args['weights']
        rows = np.arange(data.shape[0])
        new_data = np.ones(data.shape[0])
        last_row_index = rows[-1]
        row = data[last_row_index]
        mask_row = mask[last_row_index]
        weights_row = np.ma.array(weights[last_row_index], mask=mask_row)
        
        first_nonzero_index, last_nonzero_index = self.find_non_zero_range(row) 
        scale = 1
        for next_row_index in np.flip( rows):
            next_row = data[next_row_index]
            next_mask_row = mask[next_row_index]
            common_mask = next_mask_row | mask_row
            next_first_nonzero_index, next_last_nonzero_index = self.find_non_zero_range(next_row) 
            first_index = max(first_nonzero_index,next_first_nonzero_index)
            last_index = min(last_nonzero_index, next_last_nonzero_index)
            common_mask[:first_index] = True
            common_mask[last_index:] = True
            common_mask[row<1] = True
            common_mask[next_row<1] = True
            #row_masked = np.ma.array(row, mask=common_mask)
            #next_row_masked = np.ma.array(next_row, mask=common_mask)

            row_masked_subset = row[np.logical_not(common_mask)]
            next_row_masked_subset = next_row[np.logical_not(common_mask)]
            divided = next_row_masked_subset / row_masked_subset
            weights_row_subset = weights_row[np.logical_not(common_mask)]
            weighted_average_subset = np.sum(divided * weights_row_subset)/ np.sum(weights_row_subset)
            average_scale = weighted_average_subset
            #divided = np.ma.array(next_row_masked/row_masked, mask = common_mask)
            #average_scale = np.ma.average( divided, weights=weights_row)
            #average_scale = np.average (divided )
            scale = scale * average_scale
            new_data[next_row_index] = scale
            row = next_row
            mask_row = next_mask_row
            next_weights_row = np.ma.array(weights[next_row_index], mask=common_mask)
            
            weights_row = next_weights_row
            first_nonzero_index, last_nonzero_index = next_first_nonzero_index, next_last_nonzero_index 
        args['data_out'] = np.asarray([rows, new_data])
        return args

    def _apply_row_scale(self, **args):
        # calculates the relative scaling of rows with the last row having the scale value of 1
        data = args['data_in']
        row_scale_in = args['row_scale_in'][1]
        row_scale_in [row_scale_in==0 ] = 1e-7  # avoid division by 0
        rows = np.arange(data.shape[0])
        new_data = np.zeros(data.shape)
        for row in rows:
            new_data[row] = data[row] / row_scale_in[row]

        args['data_out'] = new_data
        return args

    def _bin(self, **args):
        # applies a gaussian blur to the 3d data, rebins the channels before applying the blur

        data = args['data_in']
        sigma = args['sigma']
        scaling_factor = args['scaling_factor']
        #mask = args['mask_img']
        array = data
        scaling_factor = 10
        channels = data.shape[1]
        binned_array = np.mean(array.reshape(-1, scaling_factor), axis=1).reshape(-1, int(channels/scaling_factor))
        blurred_array = gaussian_filter(binned_array, sigma=sigma)
        interpolated_array = zoom(blurred_array, zoom=(1, scaling_factor))
        args['data_out'] = interpolated_array
        
        #args['mask_out'] = new_mask
        return args

    def _rebin(self, **args):
        # re-bins the data_in into a different scale, 
        # for example change each row in data_in from E scale to q scale
        data = args['data_in']
        
        unit_out = args['unit_out']
        mask = args['mask_img']
        new_mask = copy.deepcopy(mask)
        new_data = np.ones(data.shape)

        self._rebin_to_scale(data, new_data, mask, new_mask, unit_out)
        
        args['data_out'] = new_data
        args['mask_out'] = new_mask
        return args

    def _q_to_channel(self, **args):

        # used to convert 2D data in (q) back to 3D data in (E, 2theta)
        data = args['data_in']
        x = data[0]
        rows = len(self.mca.get_calibration())
        y = data[1]
        data_3d = np.zeros((rows,len(x)))
        for row in range(rows):
            data_3d[row] = y
        unit = 'q'

        new_data = np.zeros((rows, len(x)))

        self._rebin_to_channel(x,data_3d, new_data, unit) # this updates the new_data array directly
        #new_data[new_data<0.01]= 1

        args['data_out']=new_data

        return args
    
    def _rebin_to_channel(self, x, data, new_data, unit):
        rows = len(data)
        bins = np.size(data[0])
        calibrations = self.mca.get_calibration()
        q_ranges = []
        channel_ranges = []
        for row in range(rows):
            calibration = calibrations[row]
            ch = calibration.scale_to_channel(x,unit)
            q_ranges.append(ch)
            channel_ranges.append(np.arange(bins))
        q_ranges = np.asarray(q_ranges)
        self.align_multialement_data(data, new_data, q_ranges, channel_ranges )

    def _rebin_to_scale(self, data, new_data, mask, new_mask, unit):
        
        rows = len(data)
        tth = np.zeros(rows)
        bins = np.size(data[0])
        x = np.arange(bins)
   
        calibrations = self.mca.get_calibration()
    
        rebinned_scales = []

   
        if unit == 'q':
            for row in range(rows):
                calibration = calibrations[row]
                q = calibration.channel_to_q(x)
                tth[row]= calibration.two_theta
                rebinned_scales.append(q)
        elif unit == 'E':
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
        if unit == 'q':
            self.q_scale = [rebinned_step, rebinned_min]
        elif unit == 'E':
            self.E_scale = [rebinned_step, rebinned_min]
        rebinned_new = [x*rebinned_step+rebinned_min]*rows
        self.align_multialement_data(data, new_data, rebinned_scales,rebinned_new )

        self.align_multialement_data(mask, new_mask , rebinned_scales,rebinned_new ,kind='nearest')
        
    
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
        #x = np.arange(bins)
        for row in range(rows): 
            x = old_scales[row]
            xnew = new_scales[row]
            new_data[row] = self.shift_row(data[row],x, xnew, kind)
        

    def shift_row(self, row,x, xnew, kind='linear'):
        f = interpolate.interp1d(x, row, assume_sorted=True, bounds_error=False, fill_value=0, kind=kind)
        row = f(xnew)
        return row



    