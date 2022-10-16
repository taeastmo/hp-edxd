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
        self.phases = []
        self.reflections = []
        self.phase_files = []
        self.phase_colors = []
        self.phase_visible = []

        self.same_conditions = True

    

