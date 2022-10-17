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

# Based on code from Dioptas - GUI program for fast processing of 2D X-ray diffraction data

""" 


"""

import numpy as np

from PyQt5 import QtCore
from hpm.models.jcpds import jcpds
from hpm.models.cif import CifConverter
from utilities.HelperModule import calculate_color
from hpm.models.pressure.LatticeRefinement import latticeRefinement



class LatticeRefinementModel(QtCore.QObject):
    phase_added = QtCore.pyqtSignal()
    phase_removed = QtCore.pyqtSignal(int)  # phase ind
    phase_changed = QtCore.pyqtSignal(int)  # phase ind
    phase_reloaded = QtCore.pyqtSignal(int)  # phase ind

    reflection_added = QtCore.pyqtSignal(int)
    reflection_deleted = QtCore.pyqtSignal(int, int)  # phase index, reflection index

    num_phases = 0

    def __init__(self):
        super().__init__()
        self.reflection_groups = {}
        self.use_groups = {}
        self.phases= {}
        self.active = False
        self.reflections = []
        self.output = {}

        self.ddiff = {}
        self.dobs = {}
        self.dcalc = {}
        self.P = {}
        self.V = {}
        self.refined_lattice = {}
       
    def set_reflections(self, reflections):
        self.reflections = reflections
        self.update_phases()

    def set_phases(self, phases):
        self.phases = phases

    def update_phases(self):
        reflections = self.reflections
      
        if len(reflections)>0:
            self.reflection_groups = {}     # separate reflections into groups based on name 
           
            for r in reflections:
                l = r.label.split(' ')[0]
                if len(l)>1:
                    if not l in self.reflection_groups.keys():
                        self.reflection_groups[l]=[r]

                        
                    else:
                        self.reflection_groups[l].append(r)
    def get_phases(self):
        return list(self.reflection_groups.keys())
                    
    def clear(self):
        self.__init__()
            
    def refine_phase(self, p):
        lattice_out = []

        
        if p in self.reflection_groups and p in self.phases:
        
            if p !='':
                curr_phase = None
                
                if p in self.phases.keys():
                    curr_phase = self.phases[p]
          
                DHKL = []
                phase = self.reflection_groups[p]
                use = self.use_groups[p]
                for i, r in enumerate(phase):
                    u = use[i] 
                    if u:
                        d = r.d_spacing
                        hkl = r.label.split(' ')[1]
                        if not len(hkl)==3 or not hkl.isdigit():
                            break
                        h = int(hkl[0])
                        k = int(hkl[1])
                        l = int(hkl[2])
                        dhkl = [d,h,k,l]
                        DHKL.append(dhkl)
                if len(dhkl)>0:
                    self.lattice_model = latticeRefinement()
                    self.lattice_model.set_dhkl(DHKL)
                    symmetry = curr_phase.params['symmetry']
                    self.lattice_model.set_symmetry(symmetry.lower())
                    self.lattice_model.refine()
                    volume_out = self.lattice_model.get_volume()
                    lattice_out = self.lattice_model.get_lattice()
                    
                    self.P[p] = p
                    self.V[p] = volume_out
                    self.refined_lattice[p] = lattice_out
                    
                    DCalc = self.lattice_model.refinement_output['Dcalc']

                    self.ddiff[p] = []
                    self.dobs[p] = []
                    self.dcalc[p] = []

                    for i, dcalc in enumerate(DCalc):
                        d = dcalc 
                        dobs = DHKL[i][0]
                        ddiff = dobs - d
                        self.ddiff[p].append(ddiff)
                        self.dobs[p].append(dobs)
                        self.dcalc[p].append(d)

                      
                        
                        
     

