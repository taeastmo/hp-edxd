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
import numpy as np
from scipy import interpolate
from PyQt5 import QtCore, QtWidgets
#from pyqtgraph.functions import pseudoScatter
import os
import time


from .mcareaderGeStrip import *
from .mcaModel import McaCalibration, McaElapsed, McaROI, McaEnvironment
from utilities.CARSMath import fit_gaussian

class MultipleSpectraModel(QtCore.QObject):  # 
    def __init__(self, *args, **filekw):
        
        """
        Creates new Multiple Spectra object.  
    
        Example:
            m = MultipleSpectraModel()
        """
        
        self.max_spectra = 500
        self.nchans = 4000
        self.data = []
        self.rebinned_channel_data = []
        self.E = []
        self.q = []

        self.current_scale = {'label': 'channel', 'range': [1,0]}
        self.q_scale = [1 , 0]
        self.E_scale = [1 , 0]
        
        self.r = {'files_loaded':[],
                'start_times' :[],
                'data': np.empty((0,0)),
                'calibration':[],
                'elapsed':[]}

      

    def clear(self):
        self.__init__()

    def was_canceled(self):
        return False

    def rebin_scale(self, scale='q'):
        data = self.data
        rows = len(data)
     
        bins = np.size(data[0])
        x = np.arange(bins)
        calibrations = self.r['calibration']
        rebinned_scales = []
       
        if scale == 'q':
            for row in range(rows):
                calibration = calibrations[row]
                q = calibration.channel_to_q(x)
                rebinned_scales.append(q)

        elif scale == 'E':
            for row in range(rows):
                calibration = calibrations[row]
                q = calibration.channel_to_energy(x)
                rebinned_scales.append(q)

        rebinned_scales = np.asarray(rebinned_scales)
        rebinned_min = np.amin( rebinned_scales)
        rebinned_max = np.amax(rebinned_scales)
     
        rebinned_step = round((rebinned_max-rebinned_min)/bins,3)
        if scale == 'q':
            self.q_scale = [rebinned_step, rebinned_min]
        elif scale == 'E':
            self.E_scale = [rebinned_step, rebinned_min]
        rebinned_new = [x*rebinned_step+rebinned_min]*rows
        
        self.align_multialement_data(data, self.q, rebinned_scales,rebinned_new )

    def rebin_for_energy(self):
        #calibration = self.r['calibration']
        data = self.data
        rows = len(data)
        now = time.time()
        bins = np.size(data[0])
        x = np.arange(bins)
        half_bins = int(bins/2)
        max_points_left = np.zeros(rows)
        max_points_right = np.zeros(rows)
        fit_range = 10
        for row in range(rows):
            max_rough = int( np.argmax(data[row][0:half_bins]))
            fit_segment_x = x[max_rough-fit_range:max_rough+fit_range]
            fit_segment_y = data[row][max_rough-fit_range:max_rough+fit_range]
            min_y = np.amin(fit_segment_y)
            _ , controid,_ = fit_gaussian(fit_segment_x,fit_segment_y - min_y)
            max_points_left[row] = controid

            max_rough = int(half_bins + np.argmax(data[row][-half_bins:]))
            fit_segment_x = x[max_rough-fit_range:max_rough+fit_range]
            fit_segment_y = data[row][max_rough-fit_range:max_rough+fit_range]
            min_y = np.amin(fit_segment_y)
            _ , controid,_ = fit_gaussian(fit_segment_x,fit_segment_y- min_y)
            max_points_right[row] = controid
        
        left = max(max_points_left)
        right = min(max_points_right)
      
        M = np.ones(rows)   # relative slopes
        B = np.zeros(rows)  # relative y-intercepts
        
        for row in range(rows):
            x1 = left
            x2 = right
            y1 = max_points_left[row]
            y2 = max_points_right[row]
            M[row] = (y1-y2)/(x1-x2)
            B[row] = (x1*y2 - x2*y1)/(x1-x2)
            
        calibration = {}
        calibration['slope'] = M
        calibration['offset'] = B
        self.calibration = calibration
        self.calibration_scales = self.create_multialement_alighment_calibration(data, calibration)
        x =  np.arange(bins)
        new_scales = [x]*rows
        self.align_multialement_data(data , self.rebinned_channel_data, new_scales, self.calibration_scales )
        
    def create_multialement_alighment_calibration(self, data, calibration):
        rows = len(data)
        bins = np.size(data[0])
        x = np.arange(bins)
        M = calibration['slope']
        B = calibration['offset']
        calibration_scales = []
        for row in range(rows): 
            xnew = x * M[row] + B[row]
            calibration_scales.append(xnew)
        return calibration_scales
            
    def align_multialement_data (self,  data, new_data, old_scales, new_scales):
        rows = len(data)
       
        bins = np.size(data[0])
        x = np.arange(bins)
        for row in range(rows): 
            x = old_scales[row]
            xnew = new_scales[row]
            new_data[row] = self.shift_row(data[row],x, xnew)
        

    def shift_row(self, row,x, xnew):
        f = interpolate.interp1d(x, row, assume_sorted=True, bounds_error=False, fill_value=0)
        row = f(xnew)
        return row

    def find_chi_file_nelements(self, file):
        file_text = open(file, "r")
        a = True
        comment_rows = 0
        first_data_line = 0
        line_n = 0
        while a:
            file_line = file_text.readline()
            
            if not file_line:
                print("End Of File")
                a = False
            else:
                if file_line.startswith("#"):
                    comment_rows +=1
                else:
                    if first_data_line == 0 :      
                        if  file_line.split()[0].isdigit():
                            first_data_line = line_n
            line_n +=1
        nelem = line_n - first_data_line
        return nelem
    
    def read_chi_files_2d(self, paths, *args, **kwargs):
        #fit2d or dioptas chi type file

        if 'progress_dialog' in kwargs:
            progress_dialog = kwargs['progress_dialog']
        else:
            progress_dialog = QtWidgets.QProgressDialog()

        paths = paths [:self.max_spectra]
        nfiles = len (paths)   

        nchans = self. find_chi_file_nelements(paths[0])
        self.data = np.zeros([nfiles, nchans])
        files_loaded = []
        times = []
        self.nchans = nchans
        QtWidgets.QApplication.processEvents()
        for d, file in enumerate(paths):
            if d % 5 == 0:
                #update progress bar only every 5 files to save time
                progress_dialog.setValue(d)
                QtWidgets.QApplication.processEvents()
        
            file_text = open(file, "r")

            a = True
            row = 0
            while a:
                file_line = file_text.readline()
                if not file_line.startswith ('#'):
                    columns = file_line.split()
                    if len(columns):
                        self.data[d][row]=float(columns[1])
                    row +=1
                if row >= nchans-1:
                    a = False
            files_loaded.append(file)
            file_text.close()
          
            
            if progress_dialog.wasCanceled():
                break
        QtWidgets.QApplication.processEvents()
        r = self.r
        r['files_loaded'] = files_loaded
        r['start_times'] = times
        r['data'] = self.data

    def test_read_mca_file_type1(self, file):
        nelem, first_data_line = read_mca_header(file)
        type1 = len(nelem)>0
        return type1
        
    def read_mca_ascii_file_2d(self, paths, *args, **kwargs):
        """
        Reads a single multispectral mca file from the Ge strip detector.
          The file format is a tagged ASCII format.
        The file contains the information about the number of rows and columns in the header.
        

        Inputs:
            paths:
                List, containing the name of the disk file to read. Still expects a 
                list as an imput even though it will only read the first file
                
        Outputs:
            Returns a dictionary of the following type
                'files_loaded':     mca file name # this is used when loading  a sequence of files
                'start_times' :     n.a. # this is used when loading multiple files, 
                                    in the mca file all spectra are measured simultaneously.
                'data'        :     mca counts in a form of a 2-D numpy array 
                                    (dimension 1: spectrum index
                                     dimension 2: channel index) 
            
        Example:
            m = read_mca_ascii_file_2d(['file.mca'])  
            
        """
        file = paths[0]
        correct_type = self.test_read_mca_file_type1(file)
        if correct_type:

            nelem, first_data_line = read_mca_header(paths[0])

            if 'progress_dialog' in kwargs:
                progress_dialog = kwargs['progress_dialog']
            else:
                progress_dialog = QtWidgets.QProgressDialog()

            #paths = paths [:self.max_spectra]
            progress_dialog.setMaximum(nelem[0])
            self.data = np.zeros([nelem[0], nelem[1]])
            files_loaded = paths
            times = []
            calibration = [McaCalibration()]
            elapsed = [McaElapsed()]
            rois = [[]]
            
            n_detectors= nelem[0]
            for det in range(1, n_detectors):
                elapsed.append(McaElapsed())
                calibration.append(McaCalibration())
                rois.append([])
            QtWidgets.QApplication.processEvents()
            fp = open(paths[0], 'r')
            for h in range(first_data_line):
                line = fp.readline()

            for d in range(nelem[0]):
                if d % 5 == 0:
                    #update progress bar only every 5 files to save time
                    progress_dialog.setValue(d)
                    QtWidgets.QApplication.processEvents()
            
                line = fp.readline()
                
                counts = line.split('  ')[:-2]
                for chan, count in enumerate(counts):
                        
                    self.data[d][chan]=int(count)
                
                if progress_dialog.wasCanceled():
                    break
            fp.close()
            QtWidgets.QApplication.processEvents()
            r = self.r
            r['files_loaded'] = files_loaded
            r['start_times'] = times
            r['data'] = self.data
            r['calibration'] = calibration
            r['elapsed'] = elapsed

    def read_ascii_files_2d(self, paths, *args, **kwargs):
        """
        Reads multiple disk files.  The file format is a tagged ASCII format.
        The file contains the information from the Mca object which it makes sense
        to store permanently, but does not contain all of the internal state
        information for the Mca.  This procedure reads files written with
        write_ascii_file().
        This mehtod can be several times faster than reading individual mca files.

        Inputs:
            paths:
                The names of the disk files to read.
                
        Outputs:
            Returns a dictionary of the following type
                'files_loaded':     files_loaded
                'start_times' :     start_times
                'data'        :     mca counts in a form of a 2-D numpy array 
                                    (dimension 1: file index
                                     dimension 2: channel index) 
            
        Example:
            m = read_ascii_files_2d(['mca.hpmca'])
            
        """
        if 'progress_dialog' in kwargs:
            progress_dialog = kwargs['progress_dialog']
        else:
            progress_dialog = QtWidgets.QProgressDialog()

        paths = paths [:self.max_spectra]
        nfiles = len (paths)   
        self.data = np.zeros([nfiles, self.nchans])
        files_loaded = []
        calibration = [McaCalibration()]
        elapsed = [McaElapsed()]
        rois = [[]]
        times = []
        n_detectors = nfiles
        for det in range(1, n_detectors):
            elapsed.append(McaElapsed())
            calibration.append(McaCalibration())
            rois.append([])
        nchans = self.nchans
        QtWidgets.QApplication.processEvents()
        for d, file in enumerate(paths):
            if d % 5 == 0:
                #update progress bar only every 5 files to save time
                progress_dialog.setValue(d)
                QtWidgets.QApplication.processEvents()
            
            try:
                fp = open(file, 'r')
            except:
                continue
            line = ''
            while(1):
                
                line = fp.readline()
                
                if (line == ''): break
                pos = line.find(' ')
                if (pos == -1): pos = len(line)
                tag = line[0:pos]
                value = line[pos:].strip()
                values = value.split()
                if (tag == 'VERSION:'):
                    pass
                elif (tag == 'DATE:'):  
                    start_time = value
                    times.append(start_time)
                elif (tag == 'REAL_TIME:'):
                    
                    elapsed[d].start_time = start_time
                    elapsed[d].real_time = float(values[0])
                elif (tag == 'LIVE_TIME:'):  
                   
                    elapsed[d].live_time = float(values[0])
                elif (tag == 'CAL_OFFSET:'):
                   
                    calibration[d].offset = float(values[0])
                elif (tag == 'CAL_SLOPE:'):
                   
                    calibration[d].slope = float(values[0])
                elif (tag == 'CAL_QUAD:'):  
                   
                    calibration[d].quad = float(values[0])
                elif (tag == 'TWO_THETA:'):
                  
                    calibration[d].two_theta = float(values[0])
                    calibration[d].set_dx_type('edx')
                    calibration[d].units = "keV"
                
                    
                elif (tag == 'DATA:'):
                    for chan in range(nchans):
                        line = fp.readline()
                        counts = line.split()
                        self.data[d][chan]=int(counts[0])
            files_loaded.append(os.path.normpath(file))
                
            fp.close()
            if progress_dialog.wasCanceled():
                break
        QtWidgets.QApplication.processEvents()
        r = self.r
        r['files_loaded'] = files_loaded
        r['start_times'] = times
        r['data'] = self.data
        r['calibration'] = calibration
        r['elapsed'] = elapsed
        

    def read_ascii_file_multielement_2d(self, paths, *args, **kwargs):
        """
        Reads a disk file.  The file format is a tagged ASCII format.
        The file contains the information from the Mca object which it makes sense
        to store permanently, but does not contain all of the internal state
        information for the Mca.  This procedure reads files written with
        write_ascii_file().

        Inputs:
            file:
                The name of the disk file to read.
                
        Outputs:
            Returns a dictionary of the following type:
            'n_detectors': int,
            'calibration': [McaCalibration()],
            'elapsed':     [McaElapsed()],
            'rois':        [[McaROI()]]
            'data':        [Numeric.array]
            'environment': [[McaEnvironment()]]
            
        Example:
            m = read_ascii_file('mca.001')
            m['elapsed'][0].real_time

        Modification by RH Dec. 30 2021
        Version 3.1A
        Added a distionction between EDX and ADX files.
        For ADX files a WAVELENGTH field is written rather than TWO_THETA.
        For ADX data is written as float, for EDX the as int.
        """

        file = paths[0]
        if 'progress_dialog' in kwargs:
            progress_dialog = kwargs['progress_dialog']
        else:
            progress_dialog = QtWidgets.QProgressDialog()
        
        
        try:
            fp = open(file, 'r')
        except:
            return 
        line = ''
        start_time = ''
        max_rois = 0
        self.data = []
        
        environment = []
        n_detectors = 1  # Assume single element data
        elapsed = [McaElapsed()]
        calibration = [McaCalibration()]
        rois = [[]]
        times = []
        dx_type = ''
        
            
        while(1):
            line = fp.readline()
            if (line == ''): break
            pos = line.find(' ')
            if (pos == -1): pos = len(line)
            tag = line[0:pos]
            value = line[pos:].strip()
            values = value.split()
            if (tag == 'VERSION:'):
                pass
            elif (tag == 'DATE:'):  
                start_time = value
               
                times.append(start_time)
            elif (tag == 'ELEMENTS:'):
                n_detectors  = int(value)
                for det in range(1, n_detectors):
                    elapsed.append(McaElapsed())
                    calibration.append(McaCalibration())
                    rois.append([])
           
            elif (tag == 'CHANNELS:'):
                nchans = int(value)
                progress_dialog.setMaximum(nchans)
            elif (tag == 'ROIS:'):
                nrois = []
                for d in range(n_detectors):
                    nrois.append(int(values[d]))
                max_rois = max(nrois)
                for d in range(n_detectors):
                    for r in range(nrois[d]):
                        rois[d].append(McaROI())
            elif (tag == 'REAL_TIME:'):
                for d in range(n_detectors):
                    elapsed[d].start_time = start_time
                    elapsed[d].real_time = float(values[d])
            elif (tag == 'LIVE_TIME:'):  
                for d in range(n_detectors):
                    elapsed[d].live_time = float(values[d])
            elif (tag == 'CAL_OFFSET:'):
                for d in range(n_detectors):
                    calibration[d].offset = float(values[d])
            elif (tag == 'CAL_SLOPE:'):
                for d in range(n_detectors):
                    calibration[d].slope = float(values[d])
            elif (tag == 'CAL_QUAD:'):  
                for d in range(n_detectors):
                    calibration[d].quad = float(values[d])
            elif (tag == 'TWO_THETA:'):
                for d in range(n_detectors):
                    calibration[d].two_theta = float(values[d])
                    calibration[d].set_dx_type('edx')
                    calibration[d].units = 'keV'
                data_type = int
                dx_type = 'edx'
            elif (tag == 'WAVELENGTH:'):
                for d in range(n_detectors):
                    calibration[d].wavelength = float(values[d])
                    calibration[d].set_dx_type('adx')
                    calibration[d].units = 'degrees'
                data_type = float
                dx_type = 'adx'
            elif (tag == 'ENVIRONMENT:'):
                env = McaEnvironment()
                p1 = value.find('=')
                env.name = value[0:p1]
                p2 = value[p1+2:].find('"')
                env.value = value[p1+2: p1+2+p2]
                env.description = value[p1+2+p2+3:-1]
                environment.append(env)
            elif (tag == 'DATA:'):
                
                self.data = []
                for d in range(n_detectors):
                    self.data.append(np.zeros(nchans,  dtype=data_type))
                for chan in range(nchans):
                    if chan % 50 == 0:
                        #update progress bar only every 5 files to save time
                        progress_dialog.setValue(d)
                        QtWidgets.QApplication.processEvents()
                    line = fp.readline()
                    counts = line.split()
                    for d in range(n_detectors):
                        self.data[d][chan]=data_type(counts[d])
                
            else:
                for i in range(max_rois):
                    roi = 'ROI_'+str(i)+'_'
                    if (tag == roi+'LEFT:'):
                        for d in range(n_detectors):
                            if (i < nrois[d]):
                                rois[d][i].left = int(values[d])
                            break
                    elif (tag == roi+'RIGHT:'):
                        for d in range(n_detectors):
                            if (i < nrois[d]):
                                rois[d][i].right = int(values[d])
                            break
                    elif (tag == roi+'LABEL:'):
                        labels = value.split('&')
                        for d in range(n_detectors):
                            if (i < nrois[d]):
                                rois[d][i].label = labels[d].strip()
                            break
                    else:
                        pass
        fp.close()
        
        # Built dictionary to return
        r = self.r
        r['files_loaded'] = paths
        r['start_times'] = times
        r['data'] = self.data
        r['calibration'] = calibration
        r['elapsed'] = elapsed
            