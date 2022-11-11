import numpy as np

from math import sqrt, sin, pi



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
        self.available_scales = ['Channel']

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
        self.available_scales = [scales[2]]
        if dx_type == 'edx':
            self.available_scales.append(scales[0])
            
            if self.two_theta != None:
                self.available_scales.append(scales[1])
                self.available_scales.append(scales[3])
            #self.available_scales = scales[0:-1]
        if dx_type == 'adx':
            self.available_scales.append(scales[4])
            if self.wavelength != None:
                self.available_scales.append(scales[1])
                self.available_scales.append(scales[3])
         
        

 

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
                   
                    two_theta = self. q_to_2theta(q, self.wavelength)
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