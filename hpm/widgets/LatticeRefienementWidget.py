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


from functools import partial
import numpy as Numeric
from PyQt5 import QtWidgets, QtCore

import copy
import functools
import math
import pyqtgraph as pg
from hpm.widgets.CustomWidgets import FlatButton, DoubleSpinBoxAlignRight, VerticalSpacerItem, NoRectDelegate, \
    HorizontalSpacerItem, ListTableWidget, VerticalLine, DoubleMultiplySpinBoxAlignRight

class LatticeRefinementWidget(QtWidgets.QWidget):
    widget_closed = QtCore.pyqtSignal()
    
    

    def __init__(self,):
        super().__init__()
        self.setWindowTitle("Lattice refinement")
        self.setMinimumWidth(600)
        self.roi = []
        
        self._layout = QtWidgets.QVBoxLayout()  
        self.button_widget = QtWidgets.QWidget(self)
        self.button_widget.setObjectName('reflections_control_button_widget')
        self._button_layout = QtWidgets.QHBoxLayout(self.button_widget)
        self._button_layout.setContentsMargins(0, 0, 0, 0)
        self._button_layout.setSpacing(6)
        self.do_fit = t = QtWidgets.QPushButton(self.button_widget, default=False, autoDefault=False)
        t.setText("Refine Lattice")
        t.setFixedWidth(110)
        self._button_layout.addWidget(t)
        self.auto_fit = t = QtWidgets.QPushButton(self.button_widget, default=False, autoDefault=False)
        t.setText("Auto process")
        t.setCheckable(True)
        t.setFixedWidth(110)
        self._button_layout.addWidget(t)
        self.plot_cal = t = QtWidgets.QPushButton(self.button_widget, default=False, autoDefault=False)
        t.setText(f'Plot \N{GREEK CAPITAL LETTER DELTA} d')
        t.setFixedWidth(110)
        self._button_layout.addWidget(t)



        self.lbltwo_theta = t = QtWidgets.QLabel(self.button_widget)
        t.setText(f'2\N{GREEK SMALL LETTER THETA}:')
        t.setFixedWidth(70)
        t.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self._button_layout.addWidget(t)
        self.two_theta = t = QtWidgets.QLabel(self.button_widget)

       

        self._button_layout.addWidget(t)
        self.button_widget.setLayout(self._button_layout)
        self._layout.addWidget(self.button_widget)


        _phase_selection_layout = QtWidgets.QHBoxLayout()
        self.phase_file_label = QtWidgets.QLabel("Phase")
        _phase_selection_layout.addWidget(self.phase_file_label)
        self.phases_cbx = QtWidgets.QComboBox()
        self.phases_cbx.setMaximumWidth(200)
        self.phases_cbx.setMinimumWidth(200)
        _phase_selection_layout.addWidget(self.phases_cbx)
        _phase_selection_layout.addSpacerItem(HorizontalSpacerItem())
        self._layout.addLayout(_phase_selection_layout)


        self.phases_lbl=QtWidgets.QTextEdit('')
        self.phases_lbl.setAcceptRichText(True)
        self._body_layout = QtWidgets.QHBoxLayout()
        self._layout.addLayout(self._body_layout)


        self._horizontal_layout = QtWidgets.QHBoxLayout()
        
        self.roi_tw = reflectionsTableWidget()
        self._horizontal_layout.addWidget(self.roi_tw)
        
        #self.param_tw = latticeOutputTableWidget()
        #self._horizontal_layout.addWidget(self.phases_lbl)
        self.parameter_widget = paramOutWidget()
        self._horizontal_layout.addWidget(self.parameter_widget)

        
        self._body_layout.addLayout(self._horizontal_layout)
        self.setLayout(self._layout)
        self.style_widgets()

    
        

    def style_widgets(self):
        self.setStyleSheet("""
            #roi_control_button_widget QPushButton {
                min-width: 75;
            }
        """)

    def closeEvent(self, event):
        # Overrides close event to let controller know that widget was closed by user
        self.widget_closed.emit()

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.raise_()

class paramValue(QtWidgets.QLabel):
    def __init__(self, text=''):
        super().__init__(text)
        self.setMinimumWidth(75)
        self.setMaximumWidth(75)
        

class paramOutWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self._parameter_layout = QtWidgets.QGridLayout(self)
        self._parameter_layout.setContentsMargins(10,0,10,0)
        self._parameter_layout.setSpacing(2)
        
        self.rows = [[f'a (\N{LATIN CAPITAL LETTER A WITH RING ABOVE})','a_out','a_delta_out'],
                [f'b (\N{LATIN CAPITAL LETTER A WITH RING ABOVE})','b_out','b_delta_out'],
                [f'c (\N{LATIN CAPITAL LETTER A WITH RING ABOVE})','c_out','c_delta_out'],
                [f'\N{GREEK SMALL LETTER ALPHA}\N{DEGREE SIGN}','alpha_out','alpha_delta_out'] ,
                [f'\N{GREEK SMALL LETTER BETA}\N{DEGREE SIGN}','beta_out','beta_delta_out'] ,
                [f'\N{GREEK SMALL LETTER GAMMA}\N{DEGREE SIGN}','gamma_out','gamma_delta_out'],
                [f'V (\N{LATIN CAPITAL LETTER A WITH RING ABOVE}\N{SUPERSCRIPT THREE})','v_out','v_delta_out'] ,
                [f'V/V\N{SUBSCRIPT ZERO}','v_v0_out','v_v0_delta_out'],
                ['P (GPa)','p_out','p_delta_out'],
                ['T (K)','t_out','t_delta_out']
                ]
        
        #### display parameters 
        for i in range(len(self.rows)):
            label = paramValue(self.rows[i][0])
            
            setattr(self, self.rows[i][1], paramValue())
            setattr(self, self.rows[i][2], paramValue())
            self._parameter_layout.addWidget(label, i, 0)
            self._parameter_layout.addWidget(getattr(self,self.rows[i][1]), i, 1)
            self._parameter_layout.addWidget(getattr(self,self.rows[i][2]), i, 2)

    def update_output(self,curr_phase, lattice, V):
        
        v0 = curr_phase.params['v0']
        v_over_v0 = V/v0
        
        curr_phase.compute_pressure(volume = V)
        P = curr_phase.params['pressure']
        T = curr_phase.params['temperature']
        
        if len(lattice):
            row = 0
            for i, line in enumerate( lattice):
                text = '%.4f'%(round(lattice[line],4)) 
                getattr(self, self.rows[i][1]).setText(text)
                row = row +1
                
            pvt =  ['%.3f'%(V),'%.3f'%(v_over_v0),'%.2f'%(round(P,2)),'%.2f'%(T) ]
            for i, line in enumerate( pvt):
                text = line
                getattr(self, self.rows[i+row][1]).setText(text)

    def clear(self):
        for i, row in enumerate( self.rows):
            getattr(self, self.rows[i][1]).setText('')
            getattr(self, self.rows[i][2]).setText('')
 
class reflectionsTableWidget(ListTableWidget):
    show_cb_state_changed = QtCore.pyqtSignal(int, int)
    name_item_changed = QtCore.pyqtSignal(int, str)
    def __init__(self):
        super().__init__(columns=6)
        self.roi_show_cbs = []
        self.name_items = []
        self.index_items = []
        self.nreflections = 0
        #### display column headings    
        

        self.setMinimumWidth(400)
        header_view = QtWidgets.QHeaderView(QtCore.Qt.Horizontal, self)
        self.setHorizontalHeader(header_view)
        header_view.setResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header_view.setResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header_view.setResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header_view.setResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.default_header = ['Use','ROI','HKL',
            'd obs','d calc',f'\N{GREEK CAPITAL LETTER DELTA} d']
        self.header = copy.deepcopy(self.default_header)
        self.setHorizontalHeaderLabels(self.header)
        self.setItemDelegate(NoRectDelegate())

    def populate_reflections(self):
        nreflections = self.nreflections
        #### display reflections parameters
        for i in range(nreflections):
            row=i+1
            use = self.roi[i].use==1
            label = self.roi[i].label.split(' ')[-1]
            dobs = '%.4f' % self.roi[i].d_spacing
            dcalc = '%.4f' % 0.0
            ddiff = '%.4f' % 0.0
            self.add_roi(row, use, label, dobs, dcalc, ddiff)

    def set_reflections(self, reflections):
        self.roi = reflections
        self.nreflections = len(self.roi)
        
        self.populate_reflections()
        
    def roi_removed(self, ind):
        self.del_roi(ind)

    def update_roi(self, ind, dcalc, ddiff):
        self.blockSignals(True)
        counts_item = self.item(ind, 4)
        counts_item.setText('%.4f' % dcalc)
        fwhm_item = self.item(ind, 5)
        fwhm_item.setText('%.4f' % ddiff)
        self.blockSignals(False)

    def clear_reflections(self, *args, **kwargs):
        """
        Deletes all reflections from the GUI
        """
        
        while self.rowCount() > 0:
            self.roi_removed(self.rowCount()-1)
        
        self.roi_show_cbs = []
        self.name_items = []
        self.index_items = []

    def add_roi(self, row, use, label, dobs ,dcalc, ddiff, silent=False):

        self.blockSignals(True)
        current_rows = self.rowCount()
        self.setRowCount(current_rows + 1)

        index_item = QtWidgets.QTableWidgetItem(str(row))
        #index_item.setText(str(ind))
        index_item.setFlags(index_item.flags() & ~QtCore.Qt.ItemIsEditable)
        index_item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.setItem(current_rows, 1, index_item)
        self.index_items.append(index_item)
        
        show_cb = QtWidgets.QCheckBox()
        show_cb.setFixedWidth(40)
        show_cb.setChecked(use)
        show_cb.stateChanged.connect(partial(self.roi_show_cb_changed, show_cb))
        show_cb.setStyleSheet("background-color: transparent")
        self.setCellWidget(current_rows, 0, show_cb)
        self.roi_show_cbs.append(show_cb)

        name_item = QtWidgets.QTableWidgetItem(label)
        name_item.setText(label)
        name_item.setFlags(name_item.flags() & ~QtCore.Qt.ItemIsEditable)
        name_item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.setItem(current_rows, 2, name_item)
        self.name_items.append(name_item)

        centroid_item = QtWidgets.QTableWidgetItem(dobs)
        centroid_item.setFlags(centroid_item.flags() & ~QtCore.Qt.ItemIsEditable)
        centroid_item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.setItem(current_rows, 3, centroid_item)

        counts_item = QtWidgets.QTableWidgetItem(dcalc)
        counts_item.setFlags(counts_item.flags() & ~QtCore.Qt.ItemIsEditable)
        counts_item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.setItem(current_rows, 4, counts_item)

        fwhm_item = QtWidgets.QTableWidgetItem(ddiff)
        fwhm_item.setFlags(fwhm_item.flags() & ~QtCore.Qt.ItemIsEditable)
        fwhm_item.setTextAlignment(QtCore.Qt.AlignHCenter| QtCore.Qt.AlignVCenter)
        self.setItem(current_rows, 5, fwhm_item)

        self.setColumnWidth(0, 25)
        self.setRowHeight(current_rows, 25)
        
        if not silent:
            self.select_roi(current_rows)
            self.blockSignals(False)

    

    def del_roi(self, ind, silent=False):
        self.blockSignals(True)
        self.removeRow(ind)
        if not silent:
            self.blockSignals(False)
        #del self.roi_show_cbs[ind]
        del self.name_items[ind]
        del self.index_items[ind]
        #del self.roi_color_btns[ind]
        if not silent:
            if self.rowCount() > ind:
                self.select_roi(ind)
            else:
                self.select_roi(self.rowCount() - 1)

    def select_roi(self, ind):
        self.selectRow(ind)

    def roi_show_cb_changed(self, checkbox):
        checked = checkbox.isChecked()
        index = self.roi_show_cbs.index(checkbox)
        self.roi[index].use = checked 
        if checked: state = 1
        else: state = 0
        self.show_cb_state_changed.emit(index, state) 

    def get_selected_roi_row(self):
        selected = self.selectionModel().selectedRows()
        try:
            row = selected[0].row()
        except IndexError:
            row = -1
        return row

    def get_use(self):
        use = []
        for cb in self.roi_show_cbs:
            use.append(cb.isChecked())
        return use

