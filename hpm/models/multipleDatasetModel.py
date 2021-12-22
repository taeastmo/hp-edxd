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


import numpy as np
from PyQt5 import QtCore, QtWidgets

class MultipleSpectraModel(QtCore.QObject):  # 
    def __init__(self, *args, **filekw):
        
        """
        Creates new Multiple Spectra object.  
    
        Example:
            m = MultipleSpectraModel()
        """
        
        self.max_spectra = 500
        self.nchans = 4000
        self.data = None
        
        self.r = {'files_loaded':[],
                'start_times' :[],
                'data': np.empty((0,0))}

        print(self.r['data'])

    def clear(self):
        self.__init__()

    def was_canceled(self):
        return False

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
        times = []
        nchans = self.nchans
        QtWidgets.QApplication.processEvents()
        for d, file in enumerate(paths):
            if d % 2 == 0:
                #update progress bar only every 10 files to save time
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
                if (tag == 'DATE:'):  
                    start_time = value
                    times.append(start_time)
                elif (tag == 'DATA:'):
                    for chan in range(nchans):
                        line = fp.readline()
                        counts = line.split()
                        self.data[d][chan]=int(counts[0])
            files_loaded.append(file)
                
            fp.close()
            if progress_dialog.wasCanceled():
                break
        QtWidgets.QApplication.processEvents()
        r = self.r
        r['files_loaded'] = files_loaded
        r['start_times'] = times
        r['data'] = self.data
        
