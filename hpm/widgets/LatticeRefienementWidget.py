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
import hpm.models.jcpds as jcpds
import copy
import functools
import math
import pyqtgraph as pg
from hpm.widgets.CustomWidgets import FlatButton, DoubleSpinBoxAlignRight, VerticalSpacerItem, NoRectDelegate, \
    HorizontalSpacerItem, ListTableWidget, VerticalLine, DoubleMultiplySpinBoxAlignRight

class LatticeRefinementWidget(QtWidgets.QWidget):
    widget_closed = QtCore.pyqtSignal()
    show_cb_state_changed = QtCore.pyqtSignal(int, int)
    name_item_changed = QtCore.pyqtSignal(int, str)

    def __init__(self, jcpds_directory=''):
        super().__init__()
        self.setWindowTitle("Lattice refinement")
        self.setMinimumWidth(600)
        self.roi = []
        self.jcpds_directory = jcpds_directory
        self._layout = QtWidgets.QVBoxLayout()  
        self.button_widget = QtWidgets.QWidget(self)
        self.button_widget.setObjectName('rois_control_button_widget')
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

        '''self._tth_lbl = QtWidgets.QLabel(u'2θ:')
        self._tth_unit_lbl = QtWidgets.QLabel('deg')
        self.tth_lbl = DoubleSpinBoxAlignRight()
        self.tth_step = DoubleMultiplySpinBoxAlignRight()
        self.get_tth_btn = QtWidgets.QPushButton('Get')

        self._wavelength_lbl = QtWidgets.QLabel(f'\N{GREEK SMALL LETTER LAMDA}:')
        self._wavelength_unit_lbl = QtWidgets.QLabel(f'\N{LATIN CAPITAL LETTER A WITH RING ABOVE}')
        self.wavelength_lbl = DoubleSpinBoxAlignRight()
        self.wavelength_step = DoubleMultiplySpinBoxAlignRight()
        self.get_wavelength_btn = QtWidgets.QPushButton('Get')


        self.edx_widgets= [self._tth_lbl, self._tth_unit_lbl, self.tth_lbl,self.tth_step,self.get_tth_btn]
        self.adx_widgets= [self._wavelength_lbl, self._wavelength_unit_lbl, self.wavelength_lbl,self.wavelength_step,self.get_wavelength_btn]
        '''

        self._button_layout.addWidget(t)
        self.button_widget.setLayout(self._button_layout)
        self._layout.addWidget(self.button_widget)
        self.phase_file_label = QtWidgets.QLabel()
        self._layout.addWidget(self.phase_file_label)
        self.phases_lbl=QtWidgets.QTextEdit('')
        self.phases_lbl.setAcceptRichText(True)
        self._body_layout = QtWidgets.QHBoxLayout()
        self._layout.addLayout(self._body_layout)


        self._horizontal_layout = QtWidgets.QHBoxLayout()
        self.init_reflections_list_view()
        self.init_output_view()


        
        self._body_layout.addLayout(self._horizontal_layout)
        self.setLayout(self._layout)
        self.style_widgets()

    def update_roi(self, ind, dcalc, ddiff):
        self.roi_tw.blockSignals(True)
        counts_item = self.roi_tw.item(ind, 4)
        counts_item.setText('%.4f' % dcalc)
        fwhm_item = self.roi_tw.item(ind, 5)
        fwhm_item.setText('%.4f' % ddiff)
        self.roi_tw.blockSignals(False)

    def set_rois(self, rois):
        self.roi = rois
        self.nrois = len(self.roi)
        fname_label = 'Phase file not found. Please close this \nwindow and load the corresponding phase file (.jcpds) first.'
        if len(self.roi):
            roi = self.roi[0]
            label = roi.label
            temp = label.split()
            if len(temp) >= 2:
                file = temp[0]
                item = jcpds.find_fname(self.jcpds_directory, file, file+'.jcpds')
                if item is not None:
                    fname_label = 'Phase: ' + file
        self.phase_file_label.setText(fname_label)
        self.populate_rois()

    def clear_rois(self, *args, **kwargs):
        """
        Deletes all rois from the GUI
        """
        
        while self.roi_tw.rowCount() > 0:
            self.roi_removed(self.roi_tw.rowCount()-1)
        
        self.roi_show_cbs = []
        self.name_items = []
        self.index_items = []
        
        
        

    def roi_removed(self, ind):
        self.del_roi(ind)

    def set_jcpds_directory(self, jcpds_directory):
        self.jcpds_directory = jcpds_directory

    
    def init_output_view(self):
        self._horizontal_layout.addWidget(self.phases_lbl)
   

    def populate_rois(self):
        nrois = self.nrois
        #### display rois parameters
        for i in range(nrois):
            row=i+1
            use = self.roi[i].use==1
            label = self.roi[i].label.split(' ')[-1]
            dobs = '%.4f' % self.roi[i].d_spacing
            dcalc = '%.4f' % 0.0
            ddiff = '%.4f' % 0.0
            self.add_roi(row, use, label, dobs, dcalc, ddiff)


    ################################################################################################
    # Now comes all the roi tw stuff
    ################################################################################################

    

    def add_roi(self, row, use, label, dobs ,dcalc, ddiff, silent=False):

        self.roi_tw.blockSignals(True)
        current_rows = self.roi_tw.rowCount()
        self.roi_tw.setRowCount(current_rows + 1)

        index_item = QtWidgets.QTableWidgetItem(str(row))
        #index_item.setText(str(ind))
        index_item.setFlags(index_item.flags() & ~QtCore.Qt.ItemIsEditable)
        index_item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.roi_tw.setItem(current_rows, 1, index_item)
        self.index_items.append(index_item)
        
        show_cb = QtWidgets.QCheckBox()
        show_cb.setFixedWidth(40)
        show_cb.setChecked(use)
        show_cb.stateChanged.connect(partial(self.roi_show_cb_changed, show_cb))
        show_cb.setStyleSheet("background-color: transparent")
        self.roi_tw.setCellWidget(current_rows, 0, show_cb)
        self.roi_show_cbs.append(show_cb)

        name_item = QtWidgets.QTableWidgetItem(label)
        name_item.setText(label)
        name_item.setFlags(name_item.flags() & ~QtCore.Qt.ItemIsEditable)
        name_item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.roi_tw.setItem(current_rows, 2, name_item)
        self.name_items.append(name_item)

        centroid_item = QtWidgets.QTableWidgetItem(dobs)
        centroid_item.setFlags(centroid_item.flags() & ~QtCore.Qt.ItemIsEditable)
        centroid_item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.roi_tw.setItem(current_rows, 3, centroid_item)

        counts_item = QtWidgets.QTableWidgetItem(dcalc)
        counts_item.setFlags(counts_item.flags() & ~QtCore.Qt.ItemIsEditable)
        counts_item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.roi_tw.setItem(current_rows, 4, counts_item)

        fwhm_item = QtWidgets.QTableWidgetItem(ddiff)
        fwhm_item.setFlags(fwhm_item.flags() & ~QtCore.Qt.ItemIsEditable)
        fwhm_item.setTextAlignment(QtCore.Qt.AlignHCenter| QtCore.Qt.AlignVCenter)
        self.roi_tw.setItem(current_rows, 5, fwhm_item)

        self.roi_tw.setColumnWidth(0, 25)
        self.roi_tw.setRowHeight(current_rows, 25)
        
        if not silent:
            self.select_roi(current_rows)
            self.roi_tw.blockSignals(False)

    def init_reflections_list_view(self):

        self.roi_show_cbs = []
        self.name_items = []
        self.index_items = []
    
        #### display column headings    
        
    
        self.roi_tw = ListTableWidget(columns=6)
        self.roi_tw.setMinimumWidth(400)
        header_view = QtWidgets.QHeaderView(QtCore.Qt.Horizontal, self.roi_tw)
        self.roi_tw.setHorizontalHeader(header_view)
        header_view.setResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header_view.setResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header_view.setResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header_view.setResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.default_header = ['Use','ROI','HKL',
            'd obs','d calc',f'\N{GREEK CAPITAL LETTER DELTA} d']
        self.header = copy.deepcopy(self.default_header)
        self.roi_tw.setHorizontalHeaderLabels(self.header)
        self.roi_tw.setItemDelegate(NoRectDelegate())
        self._horizontal_layout.addWidget(self.roi_tw)

    '''def set_tw_header_unit(self, unit, unit_=''):
        if unit_ !='':
            unit_=' ('+unit_+')'
        self.header[3] = unit + " " + self.default_header[3]
        self.header[4] = unit + " " + self.default_header[4]
        self.header[5] =  self.default_header[5] + " " + unit
        self.roi_tw.setHorizontalHeaderLabels(self.header)'''

    def del_roi(self, ind, silent=False):
        self.roi_tw.blockSignals(True)
        self.roi_tw.removeRow(ind)
        if not silent:
            self.roi_tw.blockSignals(False)
        #del self.roi_show_cbs[ind]
        del self.name_items[ind]
        del self.index_items[ind]
        #del self.roi_color_btns[ind]
        if not silent:
            if self.roi_tw.rowCount() > ind:
                self.select_roi(ind)
            else:
                self.select_roi(self.roi_tw.rowCount() - 1)

    def select_roi(self, ind):
        self.roi_tw.selectRow(ind)

    def roi_show_cb_changed(self, checkbox):
        checked = checkbox.isChecked()
        index = self.roi_show_cbs.index(checkbox)
        self.roi[index].use = checked 
        if checked: state = 1
        else: state = 0
        self.show_cb_state_changed.emit(index, state) 

    def get_selected_roi_row(self):
        selected = self.roi_tw.selectionModel().selectedRows()
        try:
            row = selected[0].row()
        except IndexError:
            row = -1
        return row

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

 






