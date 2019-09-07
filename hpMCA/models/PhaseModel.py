# -*- coding: utf8 -*-
# Dioptas - GUI program for fast processing of 2D X-ray data
# Copyright (C) 2017  Clemens Prescher (clemens.prescher@gmail.com)
# Institute for Geology and Mineralogy, University of Cologne
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Modifications:
    October 9, 2018 Ross Hrubiak
        - modified from Dioptas PhaseModel.py v 0.4.0 by Clemens Prescher
        - made the module standalone, can be used outside of Dioptas
            (removed references to integration, pattern, calibration and possibly other stuff)
        - compatibility with EDXRD

"""

import numpy as np

from PyQt5 import QtCore
from hpMCA.models.jcpds import jcpds
from hpMCA.models.cif import CifConverter



class PhaseLoadError(Exception):
    def __init__(self, filename):
        super(PhaseLoadError, self).__init__()
        self.filename = filename

    def __repr__(self):
        return "Could not load {0} as jcpds file".format(self.filename)


class PhaseModel(QtCore.QObject):
    phase_added = QtCore.Signal()
    phase_removed = QtCore.Signal(int)  # phase ind
    phase_changed = QtCore.Signal(int)  # phase ind
    phase_reloaded = QtCore.Signal(int)  # phase ind

    reflection_added = QtCore.Signal(int)
    reflection_deleted = QtCore.Signal(int, int)  # phase index, reflection index

    num_phases = 0

    def __init__(self):
        super().__init__()
        self.phases = []
        self.reflections = []
        self.phase_files = []

    def send_added_signal(self):
        self.phase_added.emit()

    def add_jcpds(self, filename):
        try:
            jcpds_object = jcpds()
            jcpds_object.load_file(filename)
            self.phases.append(jcpds_object)
            self.phase_files.append(filename)
            self.reflections.append([])
            #self.send_added_signal()
        except (ZeroDivisionError, UnboundLocalError, ValueError):
            raise PhaseLoadError(filename)

    def add_cif(self, filename, intensity_cutoff=0.5, minimum_d_spacing=0.5):
        try:
            cif_converter = CifConverter(0.31, minimum_d_spacing, intensity_cutoff)
            jcpds_object = cif_converter.convert_cif_to_jcpds(filename)
            self.phases.append(jcpds_object)
            self.phase_files.append(filename)
            self.reflections.append([])
        except (ZeroDivisionError, UnboundLocalError, ValueError) as e:
            print(e)
            raise PhaseLoadError(filename)
    
    def del_phase(self, ind):
        del self.phases[ind]
        del self.reflections[ind]
        del self.phase_files[ind]
        self.phase_removed.emit(ind)

    def set_pressure(self, ind, pressure):
        self.phases[ind].compute_d(pressure=pressure)
        self.get_lines_d(ind)

    def set_temperature(self, ind, temperature):
        self.phases[ind].compute_d(temperature=temperature)
        self.get_lines_d(ind)

    def set_pressure_temperature(self, ind, pressure, temperature):
        self.phases[ind].compute_d(temperature=temperature, pressure=pressure)
        self.get_lines_d(ind)

    def set_pressure_all(self, P):
        for phase in self.phases:
            phase.compute_d(pressure=P)

    def get_lines_d(self, ind):
        reflections = self.phases[ind].get_reflections()
        res = np.zeros((len(reflections), 5))
        for i, reflection in enumerate(reflections):
            res[i, 0] = reflection.d
            res[i, 1] = reflection.intensity
            res[i, 2] = reflection.h
            res[i, 3] = reflection.k
            res[i, 4] = reflection.l
        self.reflections[ind] = res
        return res

    def set_temperature_all(self, T):
        for phase in self.phases:
            phase.compute_d(temperature=T)

    def update_all_phases(self):
        for ind in range(len(self.phases)):
            self.get_lines_d(ind)

    # need to modify this for EDXD mode
    def get_phase_line_positions(self, ind, unit='E', wavelength='0.406626',tth=15):
        positions = self.reflections[ind][:, 0]

        if unit == 'd': return positions
        e = 12.398 / (2. * positions * np.sin(tth * np.pi/180./2.))
        if unit == 'E': return e
        if unit == 'q' :
            q = 6.28318530718 /(6.199 / e / np.sin(tth/180.*np.pi/2.))  
            return q  
        else:
            return [0]*len(positions)
        #print (positions)
        

    def get_phase_line_intensities(self, ind, positions, pattern, x_range, y_range):
        
        
        max_pattern_intensity = y_range[1]

        baseline = 1
        phase_line_intensities = self.reflections[ind][:, 1]
        # search for reflections within current pattern view range
        phase_line_intensities_in_range = phase_line_intensities[(positions > x_range[0]) & (positions < x_range[1])]

        # rescale intensity based on the lines visible
        if len(phase_line_intensities_in_range):
            scale_factor = (max_pattern_intensity - baseline) / \
                           np.max(phase_line_intensities_in_range)
        else:
            scale_factor = 1
        if scale_factor <= 0:
            scale_factor = 0.01

        phase_line_intensities = scale_factor * self.reflections[ind][:, 1] + baseline
        return phase_line_intensities, baseline

    def get_rescaled_reflections(self, ind, pattern, x_range,
                                 y_range, wavelength, unit='E', tth=15):
        positions = self.get_phase_line_positions(ind, unit, wavelength, tth)
        intensities, baseline = self.get_phase_line_intensities(ind, positions, pattern, x_range, y_range)
        return positions, intensities, baseline

    
    def add_reflection(self, ind):
        """
        Adds an empty reflection to the reflection table of a phase with index ind
        """
        self.phases[ind].add_reflection()
        self.get_lines_d(ind)
        self.reflection_added.emit(ind)

    def delete_reflection(self, phase_ind, reflection_ind):
        """
        Deletes a reflection from a phase with index phase index.
        """
        self.phases[phase_ind].delete_reflection(reflection_ind)
        self.get_lines_d(phase_ind)
        self.reflection_deleted.emit(phase_ind, reflection_ind)
        self.phase_changed.emit(phase_ind)

    def delete_multiple_reflections(self, phase_ind, indices):
        """
        Deletes multiple reflection from a phase with index phase index.
        """
        indices = np.array(sorted(indices))
        for reflection_ind in indices:
            self.delete_reflection(phase_ind, reflection_ind)
            indices -= 1

    def clear_reflections(self, phase_ind):
        """
        Deletes all reflections from a phase with index phase_ind
        """
        for ind in range(len(self.phases[phase_ind].reflections)):
            self.delete_reflection(phase_ind, 0)

    def update_reflection(self, phase_ind, reflection_ind, reflection):
        """
        Updates the reflection of a phase with a new jcpds_reflection
        :param phase_ind: index of the phase
        :param reflection_ind: index of the refection
        :param reflection: updated reflection
        :type reflection: jcpds_reflection
        """
        self.phases[phase_ind].reflections[reflection_ind] = reflection
        self.phases[phase_ind].params['modified'] = True
        self.phases[phase_ind].compute_d0()
        self.phases[phase_ind].compute_d()
        self.get_lines_d(phase_ind)
        self.phase_changed.emit(phase_ind)    

    def reset(self):
        """
        Deletes all phases within the phase model.
        """
        for ind in range(len(self.phases)):
            self.del_phase(0)