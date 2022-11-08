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


from ast import Return
import imp
import re
import pyqtgraph as pg
import numpy as np
from numpy.core.records import array
from pyqtgraph.graphicsItems.PlotDataItem import dataType
from scipy import interpolate
from math import sqrt, sin, pi
import utilities.centroid as centroid
import copy
import json
import time
from hpm.models.mcareader import McaReader
from hpm.widgets.UtilityWidgets import xyPatternParametersDialog
import os
import utilities.CARSMath as CARSMath
from utilities.filt import spectra_baseline
from .mcareaderGeStrip import *

from epics import caput, caget, PV

class MCA():  # 
    

    """ Device-independent MultiChannel Analyzer (MCA) class """
    def __init__(self, file=None, file_settings = None, *args, **filekw):
        """
        Creates new Mca object.  The data are initially all zeros, and the number
        of channels is 4000.
        
        Keywords:
            file:
                Name of a file to read into the new Mca object with read_file()
                
        Example:
            m = Mca('my_spectrum.dat')
        """
        
        self.dx_type = 'edx'

        self.name = ''
        self.file_name = ''
        self.file_saved_timestamp = None
        self.file_settings = file_settings # not used in this based class, used in device dependent class

        self.max_rois = 32
        self.n_detectors = 1
        self.nchans = 4000
        self.data = [np.zeros(self.nchans)+1]
        self.baseline = [np.zeros(self.nchans)+1]
        self.baseline_state = 0
        
        self.rois = [[]]
        self.rois_from_file = [[]]
        self.rois_from_det = [[]]
        self.auto_process_rois = True

        self.calibration = [McaCalibration()]
        self.elapsed = [McaElapsed()]
        self.presets = McaPresets()
        self.environment = []

        self.wavelength = None  # persistent wavelength for axd mode useful when loading files without wavelength, e.g. *.chi
        #if (file != None):
        #    self.read_file(file, **filekw)
        self.fileIO = mcaFileIO()

        

    ########################################################################
    def get_calibration(self):
        """ Returns the Mca calibration, as an McaCalibration object """
        return self.calibration

    ########################################################################
    def set_calibration(self, calibration, det = 0):
        """
        Sets the Mca calibration.
        
        Inputs:
            calibration:
                An McaCalibration object
        """
        self.calibration[det] = calibration

    ########################################################################
    def get_presets(self):
        """ Returns the Mca presets, as an McaCPresets object """
        return self.presets

    ########################################################################
    def set_presets(self, presets):
        """
        Sets the Mca presets.
        
        Inputs:
            presets:
                An McaPresets object
        """
        self.presets = presets

    ########################################################################
    def get_elapsed(self):
        """ Returns the Mca elapsed parameters, as an McaElapsed object """
        return self.elapsed

    ########################################################################
    def set_elapsed(self, elapsed):
        """
        Sets the Mca elapsed parameters.
        
        Inputs:
            elapsed:
                An McaElapsed object
        """
        self.elapsed = copy.copy(elapsed)

    ########################################################################
    def get_name(self):
        """ Returns the Mca name as a string """
        return self.name

    def get_name_base(self):
        name = os.path.basename(self.file_name)
        
        return name


    

    ########################################################################
    def set_name(self, name):
        """
        Sets the Mca name.
        
        Inputs:
            name:
                A string
        """
        self.name = name

    ########################################################################
    
    def get_file_rois(self, energy=0):
        """ Returns the Mca ROIS, as a list of McaROI objects """
        rois = copy.copy(self.rois_from_file)
     
        return rois 
    
    def get_det_rois(self, energy=0):
        """ Returns the Mca ROIS, as a list of McaROI objects """
        rois = copy.copy(self.rois_from_det)
       
        return rois 
    
    def get_rois(self, energy=0):
        """ Returns the Mca ROIS, as a list of McaROI objects """
        rois = copy.copy(self.rois)
      
        return rois

    def get_rois_offline(self, energy=0):
        """ Returns the Mca ROIS, as a list of McaROI objects, dont override with epics mca etc """
        
        rois = copy.copy(self.rois)
        '''
        if (energy != 0):
            for roi in rois:
                roi.left = self.calibration.channel_to_energy(roi.left)
                roi.right = self.calibration.channel_to_energy(roi.right)
        '''
        return rois

    def compute_get_rois(self):
        self.compute_rois()

        rois = copy.copy(self.rois)

    def compute_rois(self):
        for det in self.rois:
                for roi in det:
                    self.compute_roi(roi, det)

    def compute_roi(self, roi, detector=0):
        ## computes and updates the centroid/energy/fwhm of a roi
        ## ideally should be called when a new roi is added or data updated
        ## the goal is to simplify things for users of this class, centroids/energy of roi 
        ## should always be ready for the user 
        #start_time = time.time()
        

        [roi, fwhm_chan] = centroid.computeCentroid(self.data[detector], roi, 1)
        roi.fwhm = fwhm_chan
        roi.fwhm_E = (self.calibration[detector].channel_to_energy(roi.centroid + 
                                        fwhm_chan/2.) - 
                            self.calibration[detector].channel_to_energy(roi.centroid - 
                                        fwhm_chan/2.))
        roi.fwhm_q = (self.calibration[detector].channel_to_q(roi.centroid + 
                                        fwhm_chan/2.) - 
                            self.calibration[detector].channel_to_q(roi.centroid - 
                                        fwhm_chan/2.))
        roi.fwhm_d = (self.calibration[detector].channel_to_d(roi.centroid + 
                                        fwhm_chan/2.) - 
                            self.calibration[detector].channel_to_d(roi.centroid - 
                                        fwhm_chan/2.))      
        roi.fwhm_tth = (self.calibration[detector].channel_to_tth(roi.centroid + 
                                        fwhm_chan/2.) - 
                            self.calibration[detector].channel_to_tth(roi.centroid - 
                                        fwhm_chan/2.))                             

        roi.energy = self.calibration[detector].channel_to_energy(roi.centroid)
        roi.two_theta = self.calibration[detector].channel_to_tth(roi.centroid)
        roi.q = self.calibration[detector].channel_to_q(roi.centroid)
        roi.d_spacing = self.calibration[detector].channel_to_d(roi.centroid)


    ########################################################################
    def set_rois(self, rois, energy=0, detector=0, source='file'):
        """
        Sets the region-of-interest parameters for the MCA.
        The rois information is contained in an object of class McaRoi.
        This routine is not needed if the information in the McaRoi instance
        is already in channel units.  It is needed if the information in the
        .left and .right fields is in terms of energy.

        Inputs:
            rois:
                A list of objects of type McaROI
                
        Keywords:
            energy:
                Set this flag to indicate that the .left and .right fields
                of rois are in units of energy rather than channel number.
                
        Example:
            mca = Mca('mca.001')
            r1 = McaROI()
            r1.left = 5.4
            r1.right = 5.6
            r2 = McaROI()
            r2.left = 6.1
            r2.right = 6.2
            mca.set_rois([r1,r2], energy=1)
        """
        if source == 'file':
            self.rois_from_file[detector] = []
            set_rois = self.rois_from_file
        elif source == 'controller':
            self.rois[detector]  = []
            set_rois = self.rois
        elif source == 'detector':
            self.rois_from_det[detector]  = []
            set_rois = self.rois_from_det
        
        for roi in rois:
            '''if self.auto_process_rois :
                self.compute_roi(roi, 0)'''
            
            '''
            if (energy == 1):
                r.left =  self.calibration.energy_to_channel(r.left, clip=1)
                r.right = self.calibration.energy_to_channel(r.right, clip=1)
            '''
            lbl = roi.label
            if len(lbl)> 12:
                if ' ' in lbl:
                    parts = lbl.split(' ')
                    end = parts[-1]
                    end = end[:3]
                    start = parts[0]
                    start = start[:8]
                    lbl = start + ' ' +end
                else:
                    lbl = lbl[:12]
            roi.label = lbl
            set_rois[detector].append(roi)


    ########################################################################
    
    def add_roi(self, roi, energy=0, detector=0, source='file'):
        """
        This procedure adds a new region-of-interest to the MCA.

        Inputs:
            roi: An object of type mcaROI.
            
        Kyetwords:
            energy:
                Set this flag to 1 to indicate that the .left and .right 
                fields of roi are in units of energy rather than channel 
                number.
                
        Example:
            mca = Mca('mca.001')
            roi = McaROI()
            roi.left = 500
            roi.right = 600
            roi.label = 'Fe Ka'
            mca,add_roi(roi)
        """

        if source == 'file':
            
            set_rois = self.rois_from_file
        elif source == 'controller':
            set_rois = self.rois
        elif source == 'detector':
            set_rois = self.rois_from_det

        r = copy.copy(roi)
        if self.auto_process_rois :
            self.compute_roi(r, detector)
        '''
        if (energy == 1):
            r.left = self.calibration.energy_to_channel(r.left, clip=1)
            r.right = self.calibration.energy_to_channel(r.right, clip=1)
        '''
        set_rois[detector].append(r)

        # Sort ROIs.  This sorts by left channel.
        tempRois = copy.copy(set_rois[detector])
        tempRois.sort()
        
        set_rois[detector] = tempRois
        
    
    def add_rois(self, rois, energy=0, detector = 0, source ='file'):
        """
        Adds multiple new ROIs to the epicsMca.

        Inputs:
            rois:
                List of McaROI objects.
        """

        if source == 'file':
            
            set_rois = self.rois_from_file
        elif source == 'controller':
            set_rois = self.rois

        elif source == 'detector':
            set_rois = self.rois_from_det
       
        n_new_rois = len(rois)
        nrois = len(set_rois[detector])
        new_total = n_new_rois + nrois
        if new_total > self.max_rois:
            extra = new_total - self.max_rois 
            keep = n_new_rois - extra
            rois = rois[:keep]

        for roi in rois:
            r = copy.copy(roi)
            if self.auto_process_rois :
                self.compute_roi(r, detector)
            '''
            if (energy == 1):
                r.left = self.calibration.energy_to_channel(r.left, clip=1)
                r.right = self.calibration.energy_to_channel(r.right, clip=1)
            '''
            set_rois[detector].append(r)

            # Sort ROIs.  This sorts by left channel.
            tempRois = copy.copy(set_rois[detector])
            tempRois.sort()
            
            set_rois[detector] = tempRois

    def change_roi_use(self, ind, use, detector=0):
        roi = self.rois[detector][ind].use = use
            
    
    def clear_rois(self, source, detector):
        self.set_rois([], detector=detector,source=source)

    

    ########################################################################
    def get_data(self):
        """ Returns the data (counts) from the Mca """
        return self.data

    ########################################################################
    def set_data(self, data):
        """
        Copies an array of data (counts) to the Mca.

        Inputs:
            data:
                A Numeric array of data (counts).
        """
        self.data = data
        
        
        
        #if self.auto_process_rois :
        #    for det in self.rois:
        #        for roi in det:
        #            self.compute_roi(roi, det)

    ########################################################################

    def get_baseline(self):
        baselines = []
        for d in self.data:
            
            baselines.append(spectra_baseline(d, 0.04, 50, method='gust'))
       
        self.baselines = baselines
        return self.baselines

    def get_bins(self,detector=0):
        n = len(self.data[detector])
        return np.linspace(0,n-1, n) 

    

    def get_energy(self, detector):
        """
        Returns a list containing the energy of each channel in the MCA spectrum.

        Procedure:
            Simply returns mca.channel_to_energy() for each channel
            
        Example:
            from Mca import *
            mca = Mca('mca.001')
            energy = mca.get_energy()
        """
        channels = np.arange(len(self.data[detector]))
        return self.calibration[detector].channel_to_energy(channels)
    ########################################################################
    def get_roi_counts(self, background_width=1):
        """
        Returns a tuple (total, net) containing the total and net counts of
        each region-of-interest in the MCA.

        Kyetwords:
            background_width:
                Set this keyword to set the width of the background region on either
                side of the peaks when computing net counts.  The default is 1.
                
        Outputs:
            total:  The total counts in each ROI.
            net:    The net counts in each ROI.

            The dimension of each list is NROIS, where NROIS
            is the number of currently defined ROIs for this MCA.  It returns
            and empty list for both if NROIS is zero.
            
        Example:
            mca = Mca('mca.001')
            total, net = mca.get_roi_counts(background_width=3)
            print 'Net counts = ', net
        """
        total = []
        net = []
        nchans = len(self.data)
        for roi in self.rois:
            left = roi.left
            ll = max((left-background_width+1), 0)
            if (background_width > 0):
                bgd_left = sum(self.data[ll:(left+1)]) / (left-ll+1)
            else: bgd_left = 0.
            right = roi.right
            rr = min((right+background_width-1), nchans-1)
            if (background_width > 0):
                bgd_right = sum(self.data[right:rr+1]) / (rr-right+1)
            else: bgd_right = 0.
            total_counts = self.data[left:right+1]
            total.append(sum(total_counts))
            n_sel        = right - left + 1
            bgd_counts   = bgd_left + np.arange(n_sel,dtype=float)/(n_sel-1) * \
                                    (bgd_right - bgd_left)
            net_counts   = total_counts - bgd_counts
            net.append(sum(net_counts))
        return (total, net)
    ########################################################################    

    ########################################################################
    

    ########################################################################
    def find_roi(self, left, right, energy=0, detector =0):
        """
        This procedure finds the index number of the ROI with a specified
        left and right channel number.

        Inputs:
            left:
                Left channel number (or energy) of this ROI
                
            right:
                Right channel number (or energy) of this ROI
            
        Keywords:
            energy:
                Set this flag to 1 to indicate that Left and Right are in units
                of energy rather than channel number.
                
        Output:
            Returns the index of the specified ROI, -1 if the ROI was not found.
            
        Example:
            mca = Mca('mca.001')
            index = mca.find_roi(100, 200)
        """
        l = left
        r = right
        if (energy == 1):
            l = self.calibration.energy_to_channel(l, clip=1)
            r = self.calibration.energy_to_channel(r, clip=1)
        index = 0
        for roi in self.rois[detector]:
            if (l == roi.left) and (r == roi.right): return index
            index = index + 1
        return -1

    ########################################################################
    def delete_roi(self, index, detector=0):
        """
        This procedure deletes the specified region-of-interest from the MCA.

        Inputs:
            index:  The index of the ROI to be deleted, range 0 to len(mca.rois)
            
        Example:
            mca = Mca('mca.001')
            mca.delete_roi(2)
        """
        del self.rois[detector][index]


    ########################################################################

    ########################################################################
    def get_environment(self):
        """
        Returns a list of McaEnvironment objects that contain the environment
        parameters of the Mca.
        """
        return self.environment

    ########################################################################
    def set_environment(self, environment):
        """
        Copies a list of McaEnvironment objects to the Mca object.

        Inputs:
            environment:
                A list of McaEnvironment objects.
        """
        self.environment = environment

    def write_file(self, file, netcdf=0):
        """
        Writes Mca or Med objects to a disk file.
        
        It calls Mca.write_netcdf_file if the netcdf keyword flg is set,

        Note that users who want to read such files with Python are strongly
        encouraged to use Mca.read_file()

        Inputs:
            file:
                The name of the disk file to write.
                
        Keywords:
            netcdf:
                Set this flag to write the file in netCDF format, otherwise
                the file is written in ASCII format.  See the documentation
                for Mca.write_ascii_file and Mca.write_netcdf_file for 
                information on the formats.
    
        Example:
            mca = Mca()
            mca.write_file('mca.001')
        """
        # Call the get_xxx() methods to make sure things are up to date
        data = self.get_data()
        calibration = self.get_calibration()
        elapsed = self.get_elapsed()
        presets = self.get_presets()
        rois = self.get_rois()
        environment = self.get_environment()
        

        if (netcdf != 0):
            pass
            #    write_netcdf_file(file, data, calibration, elapsed, presets, rois, environment)
        else:
            try:
                self.fileIO.write_ascii_file(file, data, calibration, elapsed, presets, rois, environment)
                self.file_name=file
                
            except:
                return [file, False]

        
        return [file, True]

    
    ########################################################################
    
    
    def read_file(self, file, netcdf=0, detector=0, persistent_rois=[]):
        """
        Reads a disk file into an MCA object.  If the netcdf=1 flag is set it
        reads a netcdf file, else it assumes the file is ASCII.
        If the data file has multiple detectors then the detector keyword can be
        used to specify which detector data to return.

        Inputs:
            file:
                The name of the disk file to read.
                
        Keywords:
            netcdf:
                Set this flag to read files written in netCDF format, otherwise
                the routine assumes that the file is in ASCII format.
                See the documentation for Mca.write_ascii_file and
                Mca.write_netcdf_file for information on the formats.

            detector:
                Specifies which detector to read if the file has multiple detectors.
           
                
        Example:
            mca = Mca()
            mca.read_file('mca.001')
        """
        if (netcdf != 0):
            pass
            #r = read_netcdf_file(file)
        else:
            if file.endswith('.mca'):
                [r, success] = self.fileIO.read_mca_file(file)
            elif file.endswith('.chi'):
                [r, success] = self.fileIO.read_chi_file(file, wavelength=self.wavelength)
                wavelength = r['calibration'][0].wavelength
                self.wavelength = wavelength
            elif file.endswith('.xy'):
                [r, success] = self.fileIO.read_chi_file(file, wavelength=self.wavelength)
                wavelength = r['calibration'][0].wavelength
                self.wavelength = wavelength
            else:
                [r, success] = self.fileIO.read_ascii_file(file)
     
        if success == True:
            self.file_name=file
            self.calibration = r['calibration']
            self.data = r['data']
            self.nchans = len(r['data'][0])
            self.n_detectors=len(self.data)
            self.rois_from_file = [[]]*self.n_detectors
            self.rois = [[]]*self.n_detectors
            self.elapsed = r['elapsed']
            if persistent_rois == []:
                rois = r['rois']
            else:
                rois = [persistent_rois]*16
            
            for i , roi in enumerate(rois):
                self.set_rois(roi, detector=i) 
            self.environment = r['environment']
            self.name = os.path.split(file)[-1]
            self.dx_type = r['dx_type']
    
        return([file,success])

    def save_peaks_csv(self,file):

        self.fileIO.write_peaks(file, self.rois[0])

    def export_pattern(self, filename, unit='channel', unit_='#',detector=0,header=None, subtract_background=False):
        """
        Saves the current data pattern.
        :param filename: where to save
        :param header: you can specify any specific header
        :param subtract_background: whether or not the background set will be used for saving or not
        """
        y = self.data[detector]
        channels = np.arange(len(y))

        if filename.endswith('.fxye'):
            unit = 'q'
            unit_=  "A^-1"
        if unit == 'E':
            x = self.calibration[detector].channel_to_energy(channels)
        elif unit == 'q':
            x = self.calibration[detector].channel_to_q(channels)
        elif unit == 'd':
            x = self.calibration[detector].channel_to_d(channels)
        else: x = channels

        if filename.endswith('.xy'):
            self.fileIO.write_pattern(filename,x,y,unit,unit_, header=self._create_xy_header(unit))
        elif filename.endswith('.fxye'):
            self.fileIO.write_pattern(filename,x,y,unit,unit_, header=self._create_fxye_header(filename,"q_A^-1"))
        else:
            self.fileIO.write_pattern(filename,x,y,unit,unit_)

    def _create_xy_header(self, unit):
        """
        Creates the header for the xy file format (contains information about calibration parameters).
        :return: header string
        """
        header = self.make_headers()
        header = header.replace('\r\n', '\n')
        header = '# ' + unit + '\t I'
        return header

    def _create_fxye_header(self, filename, unit):
        """
        Creates the header for the fxye file format (used by GSAS and GSAS-II) containing the calibration information
        :return: header string
        """
        header = 'Generated file ' + filename + ' using hpMCA\n'
        header = header + self.make_headers()
        
        lam = 1
        if unit == 'q_A^-1':
            con = 'CONQ'
        else:
            con = 'CONS'

        header = header + '\nBANK\t1\tNUM_POINTS\tNUM_POINTS ' + con + '\tMIN_X_VAL\tSTEP_X_VAL ' + \
                 '{0:.5g}'.format(lam * 1e10) + ' 0.0 FXYE'
        return header

    def make_headers(self, hdr="#", has_mask=None, has_dark=None, has_flat=None,
                     polarization_factor=None, normalization_factor=None,
                     metadata=None):
        """
        :param hdr: string used as comment in the header
        :type hdr: str
        :param has_dark: save the darks filenames (default: no)
        :type has_dark: bool
        :param has_flat: save the flat filenames (default: no)
        :type has_flat: bool
        :param polarization_factor: the polarization factor
        :type polarization_factor: float

        :return: the header
        :rtype: str
        """
        

        header_lst = "" 
        '''["Mask applied: %s" % has_mask,
                       "Dark current applied: %s" % has_dark,
                       "Flat field applied: %s" % has_flat,
                       "Polarization factor: %s" % polarization_factor,
                       "Normalization factor: %s" % normalization_factor]'''

        if metadata is not None:
            header_lst += ["", "Headers of the input frame:"]
            header_lst += [i.strip() for i in json.dumps(metadata, indent=2).split("\n")]
        header = "\n".join(["%s %s" % (hdr, i) for i in header_lst])

        return header

        
########################################################################

class McaPresets():
    """
    The preset time and counts for an Mca.
    
    Fields:
        .live_time       # Preset live time in seconds
        .real_time       # Preset real time in seconds
        .read_time       # Time that the Mca was last read in seconds
        .total_counts    # Preset total counts between the preset
                        #    start and stop channels
        .start_channel   # Start channel for preset counts
        .end_channel     # End channel for preset counts
        .dwell           # Dwell time per channel for MCS devices
        .channel_advance # Channel advance source for MCS hardware:
                        #    0=internal, 1=external
        .prescale        # Prescaling setting for MCS hardware
    """
    def __init__(self):
        self.live_time = 0.
        self.real_time = 0.
        self.total_counts = 0.
        self.start_channel = 0
        self.end_channel = 0
        self.dwell = 0.
        self.channel_advance = 0
        self.prescale = 0

    

########################################################################

########################################################################
class mcaFileIO():
    def __init__(self):
        pass


        
    def read_mca_file (self, file, tth=15):  #amptek type file

        
        r = {}
        loaded = False
        mca_type = -1
        test_1 = self.test_read_mca_file_type1(file)
        if test_1:
            mca_type = 1
        else:
            test_0 = self.test_read_mca_file_type0(file)
            if test_0:
                mca_type = 0
        
        if mca_type == 0:
            [r, loaded] = self.read_mca_file_type0(file, tth)
        elif mca_type == 1:
            [r, loaded] = self.read_mca_file_type1(file, tth)
            
        return [r, loaded]

        

    def test_read_mca_file_type1(self, file):
        nelem, first_data_line = read_mca_header(file)
        type1 = len(nelem)>0
        return type1

    def read_mca_file_type1(self, path, tth, element =0):
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
        elapsed = McaElapsed()
        r = {}
        loaded = False
        calibration = McaCalibration(dx_type='edx')

        nelem, first_data_line = read_mca_header(path)
        data = np.zeros((int(nelem[0]),int(nelem[1])))
       
     
        fp = open(path, 'r')
        for h in range(first_data_line):
            line = fp.readline()
        for d in range(nelem[0]):
            line = fp.readline()
            counts = line.split('  ')[:-2]
            for chan, count in enumerate(counts):
                data[d][chan]=int(count)

        fp.close()
       
        calibration.two_theta= tth
        
        r['n_detectors'] = nelem[0]
        r['calibration'] = [calibration]*nelem[0]
        r['elapsed'] = [elapsed]*nelem[0]
        r['rois'] = [[]]*nelem[0]
        r['data'] = data
        r['environment'] = []
        r['dx_type'] = 'edx'
        loaded = True
        return [r, loaded]
        
    def test_read_mca_file_type0(self, file):
        mcafile = McaReader(file)
        
        ans = mcafile.get_live_time()
        type_0 = ans != None
        return type_0

    def read_mca_file_type0 (self, file, tth=15):  #amptek type file

        mcafile = McaReader(file)
        elapsed = McaElapsed()
        r = {}
        loaded = False
        

        elapsed.live_time = mcafile.get_live_time()
        elapsed.real_time = mcafile.get_real_time()
        elapsed.start_time = mcafile.get_start_time()
        calibration = McaCalibration(dx_type='edx')
        
        cal_func = mcafile.get_calibration_function()
        if cal_func is not None:
            calibration.offset, calibration.slope = cal_func
        file_rois = mcafile.get_rois()
        rois = []
        for r in file_rois:
            roi = McaROI()
            roi.left = int(r[0])
            roi.right = int(r[1])
            rois.append(roi)
        data = mcafile.get_data()
        basefile=os.path.basename(file)
        #tth = xyPatternParametersDialog.showDialog(basefile,'tth',15)
        calibration.two_theta= tth
        
        r['n_detectors'] = 1
        r['calibration'] = [calibration]
        r['elapsed'] = [elapsed]
        r['rois'] = [rois]
        r['data'] = [data]
        r['environment'] = []
        r['dx_type'] = 'edx'
        loaded = True
        return [r, loaded]
        #mcafile.plot()

 

    def read_ascii_file(self, file):
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
        try:
            fp = open(file, 'r')
        except:
            return [None, False]
        line = ''
        start_time = ''
        max_rois = 0
        data = None
        
        environment = []
        n_detectors = 1  # Assume single element data
        elapsed = [McaElapsed()]
        calibration = [McaCalibration()]
        rois = [[]]
        dx_type = ''
        try:
            
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
                elif (tag == 'ELEMENTS:'):
                    n_detectors  = int(value)
                    for det in range(1, n_detectors):
                        elapsed.append(McaElapsed())
                        calibration.append(McaCalibration())
                        rois.append([])
                elif (tag == 'CHANNELS:'):
                    nchans = int(value)
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
                    
                    data = []
                    for d in range(n_detectors):
                        data.append(np.zeros(nchans,  dtype=data_type))
                    for chan in range(nchans):
                        line = fp.readline()
                        counts = line.split()
                        for d in range(n_detectors):
                            data[d][chan]=data_type(counts[d])
                    
                else:
                    for i in range(max_rois):
                        roi = 'ROI_'+str(i)+'_'
                        if (tag == roi+'LEFT:'):
                            for d in range(n_detectors):
                                if (i < nrois[d]):
                                    rois[d][i].left = int(values[d])
                                #break
                        elif (tag == roi+'RIGHT:'):
                            for d in range(n_detectors):
                                if (i < nrois[d]):
                                    rois[d][i].right = int(values[d])
                                #break
                        elif (tag == roi+'LABEL:'):
                            labels = value.split('&')
                            for d in range(n_detectors):
                                if (i < nrois[d]):
                                    rois[d][i].label = labels[d].strip()
                                #break
                        else:
                           
                            pass
            
            # Make sure DATA array is defined, else this was not a valid data file
            if (data == None): return [None, False]
            fp.close()
            # Built dictionary to return
            r = {}
            r['n_detectors'] = n_detectors
            r['calibration'] = calibration
            r['elapsed'] = elapsed
            r['rois'] = rois
            r['data'] = data
            r['environment'] = environment
            r['dx_type'] = dx_type
            
            return [r, True]
        except:
            return [None, False]

    def compute_tth_calibration_coefficients(self, tth):

        chan = np.linspace(0,len(tth)-1,len(tth))[::50]
        tth = tth[::50]
        weights = np.ones(len(tth)) 

        coeffs = CARSMath.polyfitw(chan, tth, weights, 1)
        
        offset = coeffs[0]
        slope = coeffs[1]
        quad = 0 #coeffs[2]
        '''tth_calc = offset + slope * chan + quad * chan * chan
        tth_diff = tth_calc - tth

        pltError = pg.plot(tth,tth_diff, 
            pen=(200,200,200), symbolBrush=(255,0,0),antialias=True, 
            symbolPen='w', title="MCA Calibration"
        )
        pltError.setLabel('left', 'Calibration error')
        pltError.setLabel('bottom', 'Energy')'''
        return coeffs
        

    def read_chi_file(self, filename, wavelength=None):  #fit2d or dioptas chi type file
        if filename.endswith('.chi') or filename.endswith('.xy'):
            '''fp = open(filename, 'r')
            first_line = fp.readline()
            second_line = fp.readline()
            unit = second_line.strip().upper()[:1]  # reserved for future functionality
            fp.close()'''
            
            skiprows = 4
            data = np.loadtxt(filename, skiprows=skiprows)
            
            x = data.T[0]
            y = data.T[1]
            basefile=os.path.basename(filename)
            #name = basefile.split('.')[:-1][0]


            coeffs = self.compute_tth_calibration_coefficients(x)
            if wavelength == None:

                wavelength = xyPatternParametersDialog.showDialog(basefile,'wavelength',.4)

            r = {}
            r['n_detectors'] = 1
            r['calibration'] = [McaCalibration(offset=coeffs[0],
                                               slope=coeffs[1],
                                               quad=0, 
                                               two_theta= np.mean(x),
                                               units='degrees',
                                               wavelength=wavelength)]
            r['calibration'][0].set_dx_type('adx')
            r['elapsed'] = [McaElapsed()]
            r['rois'] = [[]]
            r['data'] = [y]
            r['environment'] = []
            r['dx_type'] = 'adx'
            return[r,True]
            
        return [None, False]
        
    #######################################################################
    def write_ascii_file(self, file, data, calibration, elapsed, presets, rois,
                        environment):
        """
        Writes Mca or Med data to a disk file.  The file 
        format is a tagged ASCII format.  The file contains the information 
        from the Mca object which it makes sense to store permanently, but 
        does not contain all of the internal state information for the Mca.  
        Files written with this routine can be read with read_ascii_file(), which
        is called by Mca.read_file() if the netcdf flag is 0.

        This procedure is typically not called directly, but is called
        by Mca.write_file if the netcdf=1 keyword is not used.

        This function can be used for writing for Mca objects, in which case
        each input parameter is an object, such as McaElapsed, etc.
        It can also be used for writing Med objects, in which case each input
        parameter is a list.

        If the rank of data is 2 then this is an Med, and the number of detectors
        is the first dimension of data

        Inputs:
            file:
                The name of the disk file to write.
                
            data:
                The data to write.  Either 1-D array or list of 1-D arrays.

            calibration:
                An object of type McaCalibration, or a list of such objects.

            elapsed:
                An object of type McaElapsed, or a list of such objects.

            presets:
                An object of type McaPresets, or a list of such objects.

            rois:
                A list of McaROI objects, or a list of lists of such objects.
            
            environment:
                A list of McaEnvironment objects, or a list of lists of such objects.
        
        Modification by RH Dec. 30 2021
        Version 3.1A
        Added a distionction between EDX and ADX files.
        For ADX files a WAVELENGTH field is written rather than TWO_THETA.
        For ADX data is written as float, for EDX the as int.
        """



        if (np.ndim(data) == 2):
            n_det = len(data)
        else:
            n_det = 1
        fformat = '%f ' * n_det
        eformat = '%e ' * n_det
        iformat = '%d ' * n_det
        sformat = '%s ' * n_det
        if (n_det == 1):
            # commented out since attributes are already stored as lists (with future outlook for multiple detectors) - RH
            """ # For convenience we convert all attributes to lists
            data = data
            rois = rois
            calibration = calibration
            presets = presets
            elapsed = elapsed
            """
        nchans = len(data[0])
        dx_type = calibration[0].dx_type
        version = '3.1A' if dx_type == 'adx'  else '3.1'
        start_time = elapsed[0].start_time

        fp = open(file, 'w')
        fp.write('VERSION:    '+version+'\n')
        fp.write('ELEMENTS:   '+str(n_det)+'\n')
        fp.write('DATE:       '+str(start_time)+'\n')
        fp.write('CHANNELS:   '+str(nchans)+'\n')

        nrois = []
        for roi in rois:
            nrois.append(len(roi))
        fp.write('ROIS:       '+(iformat % tuple(nrois))+'\n')
        real_time=[]; live_time=[]
        for e in elapsed:
            real_time.append(e.real_time)
            live_time.append(e.live_time)
        fp.write('REAL_TIME:  '+(fformat % tuple(real_time))+'\n')
        fp.write('LIVE_TIME:  '+(fformat % tuple(live_time))+'\n')
        offset=[]; slope=[]; quad=[]; two_theta=[]; wavelength=[]
        for c in calibration:
            offset.append(c.offset)
            slope.append(c.slope)
            quad.append(c.quad)
            if c.dx_type == 'edx':
                two_theta.append(c.two_theta)
            if c.dx_type == 'adx':
                wavelength.append(c.wavelength)
        fp.write('CAL_OFFSET: '+(eformat % tuple(offset))+'\n')
        fp.write('CAL_SLOPE: '+(eformat % tuple(slope))+'\n')
        fp.write('CAL_QUAD: '+(eformat % tuple(quad))+'\n')
        if c.dx_type == 'edx':
            fp.write('TWO_THETA: '+(fformat % tuple(two_theta))+'\n')
            data_format = iformat
        if c.dx_type == 'adx':
            fp.write('WAVELENGTH: '+(fformat % tuple(wavelength))+'\n')
            data_format = fformat

        for i in range(max(nrois)):
            num = str(i)
            left=[]; right=[]; label=[]
            for d in range(n_det):
                if (i < nrois[d]):
                    left.append(rois[d][i].left)
                    right.append(rois[d][i].right)
                    label.append(rois[d][i].label + '&')
                else:
                    left.append(0)
                    right.append(0)
                    label.append(' &')
            fp.write('ROI_'+num+'_LEFT:  '+(iformat % tuple(left))+'\n')
            fp.write('ROI_'+num+'_RIGHT:  '+(iformat % tuple(right))+'\n')
            fp.write('ROI_'+num+'_LABEL:  '+(sformat % tuple(label))+'\n')
        for e in environment:
            fp.write('ENVIRONMENT: '       + str(e.name) +
                                    '="'  + str(e.value) +
                                    '" (' + str(e.description) + ')\n')
        fp.write('DATA: \n')
        counts = np.zeros(n_det)
        for i in range(nchans):
            for d in range(n_det):
                counts[d]=data[d][i]
            fp.write((data_format % tuple(counts))+'\n')
        fp.close()


    def write_pattern(self, filename, x, y, unit, unit_, header=None):
        """
        Saves the x, y data pattern.
        :param filename: where to save
        :param header: you can specify any specific header
        """
        
        file_handle = open(filename, 'w')
        num_points = len(x)

        if filename.endswith('.chi'):
            if header is None or header == '':
                file_handle.write(filename + '\n')
                file_handle.write(unit + ' ('+ unit_+')''\n\n')
                file_handle.write("       {0}\n".format(num_points))
            else:
                file_handle.write(header)
            for ind in range(num_points):
                file_handle.write(' {0:.7E}  {1:.7E}\n'.format(x[ind], y[ind]))
        elif filename.endswith('.fxye'):
            factor = 100
            if header is not None:
                if 'CONQ' in header:
                    factor = 1
                header = header.replace('NUM_POINTS', '{0:.6g}'.format(num_points))
                header = header.replace('MIN_X_VAL', '{0:.6g}'.format(factor*x[0]))
                header = header.replace('STEP_X_VAL', '{0:.6g}'.format(factor*(x[1]-x[0])))

                file_handle.write(header)
                file_handle.write('\n')
            for ind in range(num_points):
                file_handle.write('\t{0:.6g}\t{1:.6g}\t{2:.6g}\n'.format(factor*x[ind], y[ind], sqrt(abs(y[ind]))))
        else:
            if header is not None:
                file_handle.write(header)
                file_handle.write('\n')
            for ind in range(num_points):
                file_handle.write('{0:.9E}  {1:.9E}\n'.format(x[ind], y[ind]))
        file_handle.close()

    def write_peaks(self, file, rois, background=None):
        """
        Writes a list of obejcts of type McaPeak to a disk file.
        If the background parameter is present it also writes the background
        structure to the file.
        
        Inputs:
            file:
                The name of a disk file to be written ;
            peaks:
                A list of McaPeak objects
                
        Keywords:
            background:
                An object of type McaBackground
                
        Example:
            r = read_peaks('my_peaks.pks')
            peaks = r['peaks']
            peaks[1].initial_energy = 6.4
            write_peaks('mypeaks.pks', peaks)
        """
        lines = []
        if (background != None):
            lines.append('Background_exponent,'     + str(background.exponent)+'\n')
            lines.append('Background_top_width,'    + str(background.top_width)+'\n')
            lines.append('Background_bottom_width,' + str(background.bottom_width)+'\n')
            lines.append('Background_tangent,'      + str(background.tangent)+'\n')
            lines.append('Background_compress,'     + str(background.compress)+'\n')
        lines.append('centroid,'+'fwhm,'+'energy,'+'fwhm_E,'+'q,'+'fwhm_q,'+'d_spacing,'+'fwhm_d,'+'label'+'\n')
        for r in rois:
            lines.append('{:.4e}'.format(r.centroid) + ', ' + 
                        '{:.4e}'.format(r.fwhm)    + ', ' + 
                        '{:.4e}'.format(r.energy) + ', ' + 
                        '{:.4e}'.format(r.fwhm_E)    + ', ' + 
                        '{:.4e}'.format(r.q)   + ', ' + 
                        '{:.4e}'.format(r.fwhm_q)      + ', ' + 
                        '{:.4e}'.format(r.d_spacing)   + ', ' + 
                        '{:.4e}'.format(r.fwhm_d)      + ', ' + 
                        r.label + '\n')
        fp = open(file, 'w')
        fp.writelines(lines)
        fp.close()

class McaROI():
    """
    Class that defines a Region-Of-Interest (ROI)
    Fields
        .left      # Left channel or energy
        .right     # Right channel or energy
        .centroid  # Centroid channel or energy
        .fwhm      # Width
        .bgd_width # Number of channels to use for background subtraction
        .use       # Flag: should the ROI should be used for energy calibration
        .preset    # Is this ROI controlling preset acquisition
        .label     # Name of the ROI
        .d_spacing # Lattice spacing if a diffraction peak
        .energy    # Energy of the centroid for energy calibration
    """
    def __init__(self, left=0., right=0., centroid=0., fwhm=0., bgd_width=0,
                    use=1, preset=0, label='', d_spacing=0., energy=0., q = 0., two_theta=0.):
        """
        Keywords:
            There is a keyword with the same name as each attribute that can be
            used to initialize the ROI when it is created.
        """
        
        self.left = left
        self.right = right
        self.fit_ok = False
        self.centroid = centroid
        self.gross_sum = 0
        self.fwhm = fwhm
        self.fwhm_E = fwhm
        self.fwhm_q = fwhm
        self.fwhm_d = fwhm
        self.fwhm_tth = fwhm
        self.bgd_width = bgd_width
        self.use = use
        self.preset = preset
        self.label = label
        self.d_spacing = d_spacing
        self.energy = energy
        self.two_theta = two_theta
        self.yFit = []
        self.x_yfit = []
        self.channels = []
        self.counts = []
        self.q = q
        self.jcpds_file = ''
        self.hkl = []
    def __lt__(self, other): 
        """
        Comparison operator.  The .left field is used to define ROI ordering
            Updated for Python 3 (python 2 used __cmp__ syntax)
        """ 
        return self.left < other.left
    def compare_counts(self, other):
        """
        Equals operator. useful for epics MCA, only update the record in left, right or label changes.
        """
        eq = self.left == other.left and  \
            self.right == other.right and \
                 self.label == other.label and \
                    self.gross_sum == other.gross_sum
        return eq
    def __eq__(self, other):
        """
        Equals operator. useful for epics MCA, only update the record in left, right or label changes.
        """
        eq = self.left == other.left and  \
            self.right == other.right and \
                 self.label == other.label 
        return eq

    def __repr__(self):
        return (self.label + ' ' + str(self.left)+':'+str(self.right))

########################################################################
class McaPeak():
    """
    Class for definiing the input and output parameters for each peak in
    fit_peaks().
    Input fields set bfore calling fit_peaks(), defaults and descriptions
        .label =       ""      # Peak label
        .self.energy_flag = 0  # Flag for fitting energy
                                #   0 = Fix energy 
                                #   1 = Optimize energy
        .fwhm_flag =   0       # Flag for fitting FWHM
                                #   0 = Fix FWHM to global curve
                                #   1 = Optimize FWHM
                                #   2 = Fix FWHM to input value
        .ampl_factor = 0.      # Fixed amplitude ratio to previous peak
                                #   0.  = Optimize amplitude of this peak
                                #   >0. = Fix amplitude to this value relative
                                #         to amplitude of previous free peak
                                #  -1.0 = Fix amplitude at 0.0
        .initial_energy = 0.   # Peak energy
        .initial_fwhm =   0.   # Peak FWHM
        .initial_ampl =   0.   # Peak amplitude
        
    Output fields returned by fit_peaks(), defaults and descriptions
        .energy =         0.   # Peak energy
        .fwhm =           0.   # Peak FWHM
        .ampl =           0.   # Peak amplitude
        .area =           0.   # Area of peak
        .bgd =            0.   # Background under peak
    """
    def __init__(self):
        self.label =       ""  # Peak label
        self.energy_flag = 0   # Flag for fitting energy
                                #   0 = Fix energy 
                                #   1 = Optimize energy
        self.fwhm_flag =   0   # Flag for fitting FWHM
                                #   0 = Fix FWHM to global curve
                                #   1 = Optimize FWHM
                                #   2 = Fix FWHM to input value
        self.ampl_factor = 0.  # Fixed amplitude ratio to previous peak
                                #   0.  = Optimize amplitude of this peak
                                #   >0. = Fix amplitude to this value relative
                                #         to amplitude of previous free peak
                                #  -1.0 = Fix amplitude at 0.0
        self.initial_energy = 0.  # Peak energy
        self.energy =         0.  # Peak energy
        self.initial_fwhm =   0.  # Peak FWHM
        self.fwhm =           0.  # Peak FWHM
        self.initial_ampl =   0.  # Peak amplitude
        self.ampl =           0.  # Peak amplitude
        self.area =           0.  # Area of peak
        self.bgd =            0.  # Background under peak
        self.ignore =         0   # Don't fit peak

class McaCalibration():
    """
    Class defining an Mca calibration.  The calibration equation is
        energy = .offset + .slope*channel + .quad*channel**2
    where the first channel is channel 0, and thus the energy of the first
    channel is .offset.
    
    Fields:
        .offset    # Offset
        .slope     # Slope
        .quad      # Quadratic
        .units     # Calibration units, a string
        .two_theta # 2-theta of this Mca for energy-dispersive diffraction
        .energy    # Energy to use for angle-dispersive diffraction
    """
    def __init__(self, offset=0., slope=1.0, quad=0., **kwargs):
        """
        There is a keyword with the same name as each field, so the object can
        be initialized when it is created.
        """

        self.offset = offset
        self.slope = slope
        self.quad = quad
        self.dx_type = ''
        self.available_scales = []

        if 'units' in kwargs:
            units = kwargs['units']
        else:
            units = ''
        
        if 'two_theta' in kwargs:
            two_theta = kwargs['two_theta']
        else:
            two_theta = None

        if 'wavelength' in kwargs:
            wavelength = kwargs['wavelength']
        else:
            wavelength = None

        if 'dx_type' in kwargs:
            self.set_dx_type(kwargs['dx_type'])

        self.units = units
        self.two_theta = two_theta      # for edx 
        self.wavelength = wavelength    # for adx 


    def set_dx_type(self, dx_type):
        scales = ["E",
                "q",
                "Channel",
                "d",
                '2 theta'] 
        self.dx_type = dx_type
        if dx_type == 'edx':
            
            self.available_scales = scales[0:-1]
        if dx_type == 'adx':
            
            self.available_scales = scales[1:]

 

    ########################################################################


    def channel_to_scale(self, channel, unit):
        if unit in self.available_scales:
            if unit == 'E':
                Scale = self.channel_to_energy(channel)
            elif unit == 'd':
                Scale = self.channel_to_d(channel)
            elif unit == 'q':
                Scale = self.channel_to_q(channel)
            elif unit == 'Channel':
                Scale = channel
            elif unit == '2 theta':
                Scale = self.channel_to_tth(channel)
            return Scale
        return channel

    def channel_to_tth(self, channel):
        tth = self.channel_to_energy(channel)
        return tth
    


    def scale_to_channel(self, scale, unit):
        if unit in self.available_scales:
            if unit == 'E':
                channel = self.energy_to_channel(scale)
            elif unit == 'd' or unit == 'q':
                
                if unit == 'q':
                    q = scale
                else :
                    if scale != 0:
                        q = 2. * pi / scale
                if 'E' in self.available_scales:
                    e   = 6.199 /((6.28318530718 /q)*np.sin(self.two_theta*0.008726646259972))
                    channel = self.energy_to_channel(e)
                elif "2 theta" in self.available_scales:
                   
                    two_theta = self. q_to_2theta(q)
                    channel = self.energy_to_channel(two_theta)


            elif unit == '2 theta':
                channel = self.energy_to_channel(scale)
            elif unit == 'Channel':
                channel = scale
        else: channel = scale
        return channel

    def q_to_2theta(self, q, wavelength):
        two_theta = np.arcsin(q/(4*pi/wavelength))/0.008726646259972 
        return two_theta

    

    def channel_to_energy(self, channels):
        """
        Converts channels to energy using the current calibration values for the
        Mca.  This routine can convert a single channel number or an array of
        channel numbers.  Users are strongly encouraged to use this function
        rather than implement the conversion calculation themselves, since it
        will be updated if additional calibration parameters (cubic, etc.) are
        added.

        Inputs:
            channels:
                The channel numbers to be converted to energy.  This can be
                a single number or a sequence of channel numbers.
                
        Outputs:
            This function returns the equivalent energy for the input channels.
            
        Example:
            mca = Mca('mca.001')
            channels = [100, 200, 300]
            energy = mca.channel_to_energy(channels) # Get the energy of these
        """
        scalar=np.isscalar(channels)
        if not scalar:
            c = np.asarray(channels)
        else:
            c = channels

        
        e = self.offset + self.slope * c
        
        return e

    ########################################################################
    def channel_to_d(self, channels):
        """
        Converts channels to "d-spacing" using the current calibration values for
        the Mca.  This routine can convert a single channel number or an array of
        channel numbers.  Users are strongly encouraged to use this function
        rather than implement the conversion calculation themselves, since it
        will be updated if additional calibration parameters are added.  This
        routine is useful for energy dispersive diffraction experiments.  It uses
        both the energy calibration parameters and the "two-theta" calibration
        parameter.

        Inputs:
            channels:
                The channel numbers to be converted to "d-spacing".
                This can be a single number or a list of channel numbers.
                
        Outputs:
            This function returns the equivalent "d-spacing" for the input channels.
            The output units are in Angstroms.
            
        Restrictions:
            This function assumes that the units of the energy calibration are keV
            and that the units of "two-theta" are degrees.
            
        Example:
            mca = Mca('mca.001')
            channels = [100,200,300]
            d = mca.channel_to_d(channels)       # Get the "d-spacing" of these
        """
        
        q = self.channel_to_q(channels)
        
        d = 2. * pi / q
        return d

    def channel_to_q(self,channels):
        q = channels
        if "E" in self.available_scales:
            e = self.channel_to_energy(channels)   
            q = 6.28318530718 /(6.199 / e / sin(self.two_theta*0.008726646259972))
        elif "2 theta" in self.available_scales:
            two_theta = self.channel_to_energy(channels)
            
            q = (4*pi/self.wavelength) * np.sin( two_theta * 0.008726646259972)
        return  q

    ########################################################################
    def energy_to_channel(self, energy, clip=0):
        """
        Converts energy to channels using the current calibration values for the
        Mca.  This routine can convert a single energy or an array of energy
        values.  Users are strongly encouraged to use this function rather than
        implement the conversion calculation themselves, since it will be updated
        if additional calibration parameters are added.

        Inputs:
            energy:
                The energy values to be converted to channels. This can be a
                single number or a sequence energy values.
                
        Keywords:
            clip:
                Set this flag to 1 to clip the returned values to be between
                0 and nchans-1.  The default is not to clip.
                
        Outputs:
            This function returns the closest equivalent channel for the input
            energy.  Note that it does not generate an error if the channel number
            is outside the range 0 to (nchans-1), which will happen if the energy
            is outside the range for the calibration values of the Mca.
            
        Example:
            mca = Mca('mca.001')
            channel = mca.energy_to_channel(5.985)
        """
        if (self.quad == 0.0):
            channel = ((energy-self.offset) /
                        self.slope)
        else:
            # Use the quadratic formula, use some shorthand
            a = self.quad
            b = self.slope
            c = self.offset - energy
            # There are 2 roots.  I think we always want the "+" root?
            channel = (-b + np.sqrt(b**2 - 4.*a*c))/(2.*a)
        channel = np.round(channel)
        if (clip != 0): 
            nchans = len(self.data)
            channel = np.clip(channel, 0, nchans-1)
        if (type(channel) == np.array): 
            return channel.astype(np.int)
        else:
            try:
            
                return int(channel)
            except:
                return -1
                

    ########################################################################
    def d_to_channel(self, d, clip=0, tth=None, wavelength = None):
        """
        Converts "d-spacing" to channels using the current calibration values
        for the Mca.  This routine can convert a single "d-spacing" or an array
        of "d-spacings".  Users are strongly encouraged to use this function
        rather than implement the conversion calculation themselves, since it
        will be updated if additional calibration parameters are added.
        This routine is useful for energy dispersive diffraction experiments.
        It uses both the energy calibration parameters and the "two-theta"
        calibration parameter.

        Inputs:
            d:
                The "d-spacing" values to be converted to channels.
                This can be a single number or an array of values.
                
        Keywords:
            clip:
                Set this flag to 1 to clip the returned values to be between
                0 and nchans-1.  The default is not to clip.
                
        Outputs:
            This function returns the closest equivalent channel for the input
            "d-spacing". Note that it does not generate an error if the channel
            number is outside the range 0 to (nchans-1), which will happen if the
            "d-spacing" is outside the range for the calibration values of the Mca.
            
        Example:
            mca = Mca('mca.001')
            channel = mca.d_to_chan(1.598)
        """
        q = 2. * pi / d

        if self.dx_type == 'edx':
            if tth ==None:
                tth = self.two_theta
            e   = 6.199 /((6.28318530718 /q)*np.sin(tth*0.008726646259972))
            channel = self.energy_to_channel(e)
        elif self.dx_type == 'adx':
            
            two_theta = self. q_to_2theta(q, wavelength)
            channel = self.energy_to_channel(two_theta)
        else:
            channel = d
        
        return channel

    ########################################################################

class McaElapsed():
    """
    The elapsed time and counts for an Mca.
    
    Fields:
        .start_time   # Start time and date, a string
        .live_time    # Elapsed live time in seconds
        .real_time    # Elapsed real time in seconds
        .read_time    # Time that the Mca was last read in seconds
        .total_counts # Total counts between the preset start and stop channels
    """
    def __init__(self, start_time='', live_time=0., real_time=0., 
                        read_time=0., total_counts=0.):
        self.start_time = start_time
        self.live_time = live_time
        self.real_time = real_time
        self.read_time = read_time
        self.total_counts = total_counts

class McaEnvironment():
    """
    The "environment" or related parameters for an Mca.  These might include
    things like motor positions, temperature, anything that describes the
    experiment.

    An Mca object has an associated list of McaEnvironment objects, since there
    are typically many such parameters required to describe an experiment.

    Fields:
        .name         # A string name of this parameter, e.g. "13IDD:m1"
        .value        # A string value of this parameter,  e.g. "14.223"
        .description  # A string description of this parameter, e.g. "X stage"
    """
    def __init__(self, name='', value='', description=''):
        self.name = name
        self.value = value
        self.description = description