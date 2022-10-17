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
import hpm.models.jcpds as jcpds
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
from hpm.models.LatticeRefinementModel import LatticeRefinementModel
from PyQt5.QtCore import pyqtSignal, QObject

import pyqtgraph as pg

class LatticeRefinementController(QObject):

   
    

    def __init__(self, mcaModel, plotWidget, plotController, mainController):
        super().__init__()

        self.phases_directory = mainController.working_directories.phase
        
        self.widget = LatticeRefinementWidget()
        self.set_mca(mcaModel)
        self.mcaController = mainController
        
        self.model = LatticeRefinementModel()

        detector = 0
        self.ddiff =[]
       
    
        self.dataLen = self.mca.nchans
        self.pattern_widget = plotWidget
        self.plotController = plotController
  
        self.nreflections = 0

        '''self.unit = 'E'
        self.unit_ = 'KeV'''

        self.selected_phase = ''

        self.active = False
        
        self.create_signals()

    def set_mca(self, mca):
        self.mca = mca
        self.dataLen = self.mca.nchans
        self.calibration = self.mca.get_calibration()[0]
        self.two_theta =  self.calibration.two_theta
        if type(self.two_theta) == type(float()):
            self.widget.two_theta.setText(str(round(self.two_theta,5)))



    def set_jcpds_directory(self, directory):
        
        self.phases_directory = directory


    def get_calibration(self):
        return self.calibration
        
    def create_signals(self):
        
        self.widget.do_fit.clicked.connect(self.menu_do_fit)
        self.widget.auto_fit.toggled.connect(self.auto_fit_callback)
        self.widget.plot_cal.clicked.connect(self.menu_plot_refinement)
        self.widget.phases_cbx.activated.connect(self.phases_cbx_callback)

    def phases_cbx_callback(self, *args):
        selected_ind = args[0]
        phase = self.widget.phases_cbx.itemText(selected_ind)
        if phase != self.selected_phase:
            self.selected_phase = phase
            reflections = self.model.reflection_groups[phase]
            self.widget.clear_reflections()
            self.widget.set_reflections(reflections)
        
            self.widget.phases_lbl.setText('')
       
    def pressure(self):
        self.show_view()

    def show_view(self):
        self.active = True
        self.widget.raise_widget()

    def view_closed(self):
        self.active = False

    def auto_fit_callback(self, state):
        if state:
            self.update_phases()

    def menu_do_fit(self):
       
        self.update_phases()

    def update_phases(self):
        self.model.update_phases()
        selected_phase = self.selected_phase
        use = self.widget.get_use()
        self.model.use_groups[selected_phase] = use
        if selected_phase in self.model.phases:
            self.model.refine_phase(selected_phase)

            DCalc = self.model.dcalc[selected_phase]
            for i, dcalc in enumerate(DCalc):
               
                ddiff = self.model.ddiff[selected_phase][i]
                self.widget.update_roi(i,round(dcalc, 4),round(ddiff,4))

            p = self.model.P[selected_phase]
            lattice_out = self.model.refined_lattice[selected_phase]
            volume_out = self.model.V[selected_phase]

            self.update_output(p, lattice_out,  volume_out)
        else:
            fname_label = 'Phase file not found. Please close this \nwindow and load the corresponding phase file (.jcpds) first.'
            self.widget.phases_lbl.setText(fname_label)
        

    def clear_reflections(self, *args, **kwargs):
        """
        Deletes all reflections from the GUI and model
        """
        self.model.clear()
        self.widget.clear_reflections()
        self.widget.phases_lbl.setText('')
        
        self.ddiff =[]
        self.reflection = []
        
     
    def update_reflections(self):
        pass


    def menu_plot_refinement(self):
        """ Private method """
        
        if self.selected_phase in self.model.ddiff:
            E_diff = self.model.ddiff[self.selected_phase]
            if len (E_diff):
                energy_use = self.model.dobs[self.selected_phase]
                E_diff_use = E_diff
            
                
                pltError = pg.plot(energy_use,E_diff_use, 
                        pen=(200,200,200), symbolBrush=(255,0,0),antialias=True, 
                        symbolPen='w', title= f'\N{GREEK CAPITAL LETTER DELTA} d'
                )
                pltError.setLabel('left', f'\N{GREEK CAPITAL LETTER DELTA} d '+ f'\N{LATIN CAPITAL LETTER A WITH RING ABOVE}')
                pltError.setLabel('bottom', 'd '+f'\N{LATIN CAPITAL LETTER A WITH RING ABOVE}')


    def set_reflections_phases(self, reflections, phases):
        self.clear_reflections()
        self.widget.phases_lbl.setText('')

        

        self.model.set_reflections( reflections)
        self.model.set_phases( phases)

        reflection_groups = self.model. get_phases()
        self.widget.phases_cbx.blockSignals(True)
        self.widget.phases_cbx.clear()
        self.widget.phases_cbx.addItems(reflection_groups)
        self.widget.phases_cbx.blockSignals(False)

        if not self.selected_phase in reflection_groups:
            if len(reflection_groups):
                self.selected_phase = reflection_groups[0]
            else:
                self.selected_phase = ''
        
        
        if len(self.selected_phase):
            show_reflections= self.model.reflection_groups[self.selected_phase]
            self.widget.set_reflections(show_reflections)

   
    
            

    def update_output(self,phase, lattice, V):
        curr_phase = self.model.phases[phase]
        v0 = curr_phase.params['v0']
        v_over_v0 = V/v0
        v0_v = 1/v_over_v0
        curr_phase.compute_pressure(volume = V)
        P = curr_phase.params['pressure']
        T = curr_phase.params['temperature']
        lbl= ''

        if not len(lattice):
            lbl += 'Phase '+ phase +' not recognized. \nAdd corresponding phase \nto Phase control.'

        else:
            for line in lattice:
                parameter = line.replace('alpha', f'\N{GREEK SMALL LETTER ALPHA}') \
                                    .replace('beta', f'\N{GREEK SMALL LETTER BETA}') \
                                        .replace('gamma', f'\N{GREEK SMALL LETTER GAMMA}')
                lbl += parameter + " = " + '%.4f'%(round(lattice[line],4)) + '\n'

            lbl += 'V = ' + '%.3f'%(V) + '\n'
            lbl += f'\nV/V\N{SUBSCRIPT ZERO} = '+ '%.3f'%(v_over_v0)
            lbl += '\nP = '+ '%.2f'%(round(P,2))+ ' GPa '
            lbl += '\nT = '+ '%.2f'%(T) + ' K'
            lbl += '\n\n'

        self.widget.phases_lbl.setText(lbl)