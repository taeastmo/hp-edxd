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
import functools, math
import os
from hpm.widgets.CustomWidgets import FlatButton, DoubleSpinBoxAlignRight, VerticalSpacerItem, NoRectDelegate, \
    HorizontalSpacerItem, ListTableWidget, VerticalLine, DoubleMultiplySpinBoxAlignRight
from hpm.widgets.UtilityWidgets import save_file_dialog, open_file_dialog, open_files_dialog
from hpm.widgets.RoiWidget import RoiWidget, plotFitWindow
from hpm.widgets.LatticeRefienementWidget import LatticeRefinementWidget
from hpm.models.mcaModel import  McaROI
from PyQt5.QtCore import pyqtSignal, QObject
from hpm.models.pressure.LatticeRefinement import latticeRefinement
import pyqtgraph as pg

class LatticeRefinementController(QObject):

   
    

    def __init__(self, mcaModel, plotWidget, plotController, mainController):
        super().__init__()
        
        self.set_mca(mcaModel)
        self.mcaController = mainController
        self.phases=dict()
        self.lattice = latticeRefinement()

        
        self.Ediff =[]
        detector = 0
        self.roi = []
        self.calibration = copy.deepcopy(mcaModel.get_calibration()[detector])
        self.two_theta =  self.calibration.two_theta
        self.working_directories = mainController.working_directories.phase
      
        self.active = False
        
        self.dataLen = self.mca.nchans
        self.pattern_widget = plotWidget
        self.plotController = plotController
        self.unit = 'E'
        self.unit_ = 'KeV'
        self.roi_cursor = []
        
        self.widget = LatticeRefinementWidget(self.calibration,self.working_directories)
        

        self.nrois = 0
        
        self.create_signals()

    def set_mca(self, mca):
        self.mca = mca
        self.dataLen = self.mca.nchans
        self.calibration = self.mca.get_calibration()[0]
        self.two_theta =  self.calibration.two_theta

    def get_calibration(self):
        return self.calibration
        
    def create_signals(self):
        
        self.widget.do_fit.clicked.connect(self.menu_do_fit)
        self.widget.plot_cal.clicked.connect(self.menu_plot_refinement)
       
    def pressure(self):
        self.show_view()

    def show_view(self):
        self.active = True
        self.widget.raise_widget()

    def view_closed(self):
        self.active = False


    def menu_do_fit(self):
       
        self.update_phases()
 

    def menu_plot_refinement(self):
        """ Private method """
        energy = []
        E_diff = self.Ediff
        energy_use = []
        E_diff_use = []

        for i in range(len(self.roi)):
            energy.append(self.roi[i].energy)
            
            if (self.roi[i].use):
                energy_use.append(energy[i])
                E_diff_use.append(E_diff[i])
        
        pltError = pg.plot(energy_use,E_diff_use, 
                pen=(200,200,200), symbolBrush=(255,0,0),antialias=True, 
                symbolPen='w', title=f'Energy error'
        )
        pltError.setLabel('left', f'Energy error')
        pltError.setLabel('bottom', 'Energy')


    def set_rois_phases(self, rois, phases):
        self.roi = rois
        self.phases = phases
        self.widget.set_rois(rois)


    def update_phases(self):
        
        rois = self.roi
        tth = self.two_theta
        if len(rois)>0:
            roi_groups = {}     # separate rois into groups based on name 
            for r in rois:
                l = r.label.split(' ')[0]
                if len(l)>1:
                    if not l in roi_groups.keys():
                        roi_groups[l]=[r]
                    else:
                        roi_groups[l].append(r)
            lbl=''
            

            for p in roi_groups:
                if p !='':
                    curr_phase = None
                    
                    
                    if p in self.phases.keys():
                        curr_phase = self.phases[p]
                        
                    else: 
                        lbl += 'phase not recognized'
                        break
                    lbl += p + ':\n '
                    DHKL = []
                    phase = roi_groups[p]
                    for r in phase:
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
                        self.lattice = latticeRefinement()
                        self.lattice.set_dhkl(DHKL)
                        symmetry = curr_phase.params['symmetry']
                        self.lattice.set_symmetry(symmetry.lower())
                        self.lattice.refine()
                        v = self.lattice.get_volume()
                        l = self.lattice.get_lattice()
                        DCalc = self.lattice.refinement_output['Dcalc']
                        v0 = curr_phase.params['v0']
                        v_over_v0 = v/v0
                        v0_v = 1/v_over_v0
                        curr_phase.compute_pressure(volume = v)
                        P = curr_phase.params['pressure']
                        T = curr_phase.params['temperature']
                        #print(str(DHKL))
                        lbl +='volume = ' + '%.3f'%(v)+' A^3\n v/v0 = '+ '%.3f'%(v_over_v0)
                        lbl += '\n P = '+ '%.2f'%(P)+ ' GPa\n T = '+ '%.2f'%(T)
                        lbl += '\nlattice: '
                        for line in l:
                            lbl +='\n'+ line + ": " + str(round(l[line],4))

                        self.Ediff = []

                        for i, dcalc in enumerate(DCalc):
                            e = round(12.398 / (2. * dcalc * np.sin(tth*np.pi/180./2.)),3)
                            #t = self.widget.widgets.calc_d[i]
                            #t.setText(str(e))
                            dobs = DHKL[i][0]
                            eobs = round(12.398 / (2. * dobs * np.sin(tth*np.pi/180./2.)),3)
                            ediff = round(eobs - e,3)
                            #t = self.widget.widgets.calc_d_diff[i]
                            #t.setText(str(ediff))
                            self.Ediff.append(ediff)

                            self.widget.update_roi(i,e,ediff)
                        

            self.widget.phases_lbl.setText(lbl)