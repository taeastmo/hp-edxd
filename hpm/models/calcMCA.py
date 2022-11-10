import numpy as np
#from epics.clibs import *
import copy
import time
import utilities.hpMCAutilities as hpUtil
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox
from hpm.models.mcaModel import *

from hpm.models.multipleDatasetModel import MultipleSpectraModel

class multiMCA(MCA):
    """
    Creates a new calcMCA. calcMCA acts like a regular multi-detector MCA, but can be
        created either by reading a single multi-detector mca file, or by 
        reading multiple single-detector mca files.

    Keywords:
        record_Name:
        The name of the multielement MCA file for the MCA object being created.

        file_options:

        record_name_file:
        
        environment_file:
        This keyword can be used to specify the name of a file which
        contains the names of EPICS process variables which should be saved
        in the header of files written with Mca.write_file().
        If this keyword is not specified then this function will attempt the
        following:
            - If the system environment variable MCA_ENVIRONMENT is set then
                it will attempt to open that file
            - If this fails, it will attempt to open a file called
                'catch1d.env' in the current directory.
                This is done to be compatible with the data catcher program.
        This is an ASCII file with each line containing a process variable
        name, followed by a space and a description field.

    Example:

    """
    def __init__(self, *args,  **kwargs):
        
        super().__init__()
        
        record_name = kwargs['record_name']
        file_options  = kwargs['file_options']
        environment_file  = kwargs['environment_file']
        dead_time_indicator  = kwargs['dead_time_indicator']

        self.name = record_name
        
        self.last_saved=''
        self.file_settings = file_options
        self.verbose = False
        
        self.mcaRead = None
        self.record_name = record_name
        
        self.max_rois = 24           
        self.initOK = False             

        self.multi_spectra_model = MultipleSpectraModel()
