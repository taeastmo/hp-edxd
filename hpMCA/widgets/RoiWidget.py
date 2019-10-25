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
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5 import QtWidgets, QtCore
import copy
import pyqtgraph as pg
from hpMCA.widgets.CustomWidgets import FlatButton, DoubleSpinBoxAlignRight, VerticalSpacerItem, NoRectDelegate, \
    HorizontalSpacerItem, ListTableWidget, VerticalLine, DoubleMultiplySpinBoxAlignRight


class RoiWidget(QtWidgets.QWidget):

    color_btn_clicked = QtCore.pyqtSignal(int, QtWidgets.QWidget)
    #roi_btn_clicked = QtCore.pyqtSignal(int)
    show_cb_state_changed = QtCore.pyqtSignal(int, int)
    name_item_changed = QtCore.pyqtSignal(int, str)
    widget_closed = QtCore.pyqtSignal()
    key_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self._layout = QtWidgets.QVBoxLayout()  
        self.setWindowTitle('ROIs control')
        self.button_widget = QtWidgets.QWidget(self)
        self.button_widget.setObjectName('rois_control_button_widget')
        self._button_layout = QtWidgets.QHBoxLayout()
        self._button_layout.setContentsMargins(0, 0, 0, 0)
        self._button_layout.setSpacing(6)
        #self.add_btn = FlatButton('Add')
        #self.edit_btn = FlatButton('Edit')
        self.delete_btn = FlatButton('Delete')
        self.clear_btn = FlatButton('Clear')
        self.show_fit_btn = FlatButton('Show fit')
        self.pressure_btn = FlatButton('Pressure')
        self.save_peaks_btn = FlatButton('Save List')

        #self._button_layout.addWidget(self.add_btn)
        #self._button_layout.addWidget(self.edit_btn)
        self._button_layout.addWidget(self.delete_btn)
        self._button_layout.addWidget(self.clear_btn)
        self._button_layout.addWidget(self.show_fit_btn)
        #self._button_layout.addWidget(self.pressure_btn)
        self._button_layout.addWidget(self.save_peaks_btn)

        self.button_widget.setLayout(self._button_layout)
        self._layout.addWidget(self.button_widget)
        self._body_layout = QtWidgets.QHBoxLayout()
        self.roi_tw = ListTableWidget(columns=5)
        self._body_layout.addWidget(self.roi_tw, 10)
        self._layout.addLayout(self._body_layout)

        

        self.setLayout(self._layout)

        self.style_widgets()
        self.roi_show_cbs = []
        self.name_items = []
        self.index_items = []
        #self.roi_color_btns = []
        self.show_parameter_in_pattern = True
        header_view = QtWidgets.QHeaderView(QtCore.Qt.Horizontal, self.roi_tw)
        self.roi_tw.setHorizontalHeader(header_view)
        header_view.setResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        
        header_view.setResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header_view.setResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header_view.setResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.default_header = ['#', 'Name','Centroid', 'Counts', 'fwhm']
        self.header = copy.deepcopy(self.default_header)
        self.roi_tw.setHorizontalHeaderLabels(self.header)
        #header_view.hide()
        self.roi_tw.setItemDelegate(NoRectDelegate())
        self.roi_tw.itemChanged.connect(self.roi_name_item_changed)

    def keyPressEvent(self, e):
        sig = None
        if e.key() == Qt.Key_Up:
            sig = 'up'
        if e.key() == Qt.Key_Down:
            sig = 'down'                
        if e.key() == Qt.Key_Delete:
            sig = 'delete'
        if e.key() == Qt.Key_Right:
            sig = 'right'   
        if e.key() == Qt.Key_Left:
            sig = 'left'   
        if e.key() == Qt.Key_Backspace:
            sig = 'delete'  
        if sig is not None:
            self.key_signal.emit(sig)
        else:
            super().keyPressEvent(e)

    def set_tw_header_unit(self, unit, unit_=''):
        if unit_ !='':
            unit_=' ('+unit_+')'
        self.header[2] = self.default_header[2] + ', '+unit+unit_
        self.roi_tw.setHorizontalHeaderLabels(self.header)

    def style_widgets(self):
        self.roi_tw.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.roi_tw.setMinimumWidth(450)
        self.roi_tw.setMinimumHeight(110)
        self.setStyleSheet("""
            #roi_control_button_widget FlatButton {
                min-width: 90;
            }
        """)


    ################################################################################################
    # Now comes all the roi tw stuff
    ################################################################################################

    def add_roi(self, use, name, centroid,fwhm, ind, counts, silent=False):
        self.roi_tw.blockSignals(True)
        current_rows = self.roi_tw.rowCount()
        self.roi_tw.setRowCount(current_rows + 1)

        index_item = QtWidgets.QTableWidgetItem(str(ind))
        #index_item.setText(str(ind))
        index_item.setFlags(index_item.flags() & ~QtCore.Qt.ItemIsEditable)
        index_item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.roi_tw.setItem(current_rows, 0, index_item)
        self.index_items.append(index_item)

        '''
        show_cb = QtWidgets.QCheckBox()
        show_cb.setChecked(True)
        show_cb.stateChanged.connect(partial(self.roi_show_cb_changed, show_cb))
        show_cb.setStyleSheet("background-color: transparent")
        self.roi_tw.setCellWidget(current_rows, 1, show_cb)
        self.roi_show_cbs.append(show_cb)
        '''

        name_item = QtWidgets.QTableWidgetItem(name)
        name_item.setText(name)
        #name_item.setFlags(name_item.flags() & ~QtCore.Qt.ItemIsEditable)
        name_item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.roi_tw.setItem(current_rows, 1, name_item)
        self.name_items.append(name_item)

        centroid_item = QtWidgets.QTableWidgetItem(centroid)
        centroid_item.setFlags(centroid_item.flags() & ~QtCore.Qt.ItemIsEditable)
        centroid_item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.roi_tw.setItem(current_rows, 2, centroid_item)

        counts_item = QtWidgets.QTableWidgetItem(counts)
        counts_item.setFlags(counts_item.flags() & ~QtCore.Qt.ItemIsEditable)
        counts_item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.roi_tw.setItem(current_rows, 3, counts_item)

        fwhm_item = QtWidgets.QTableWidgetItem(fwhm)
        fwhm_item.setFlags(fwhm_item.flags() & ~QtCore.Qt.ItemIsEditable)
        fwhm_item.setTextAlignment(QtCore.Qt.AlignHCenter| QtCore.Qt.AlignVCenter)
        self.roi_tw.setItem(current_rows, 4, fwhm_item)

        self.roi_tw.setColumnWidth(0, 25)
        #self.roi_tw.setColumnWidth(1, 20)
        self.roi_tw.setRowHeight(current_rows, 25)
        
        if not silent:
            self.select_roi(current_rows)
            self.roi_tw.blockSignals(False)

    def closeEvent(self, event):
        # Overrides close event to let controller know that widget was closed by user
        self.widget_closed.emit()
        
    def select_roi(self, ind):
        self.roi_tw.selectRow(ind)
        
    def get_selected_roi_row(self):
        selected = self.roi_tw.selectionModel().selectedRows()
        try:
            row = selected[0].row()
        except IndexError:
            row = -1
        return row

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.raise_()

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

    def rename_roi(self, ind, name):
        self.roi_tw.blockSignals(True)
        name_item = self.roi_tw.item(ind, 1)
        name_item.setText(name)
        self.roi_tw.blockSignals(False)

    def update_roi(self, ind, use, name, centroid,fwhm,counts):
        self.roi_tw.blockSignals(True)
        index_item = self.roi_tw.item(ind, 0)
        index_item.setText(str(ind))

        #show_cb = self.roi_show_cbs[ind]
        #show_cb.setChecked(use)
        name_item = self.roi_tw.item(ind, 1)
        name_item.setText(name)
        centroid_item = self.roi_tw.item(ind, 2)
        centroid_item.setText(centroid)
        counts_item = self.roi_tw.item(ind, 3)
        counts_item.setText(counts)
        fwhm_item = self.roi_tw.item(ind, 4)
        fwhm_item.setText(fwhm)
        self.roi_tw.blockSignals(False)

    def roi_show_cb_changed(self, checkbox):
        checked = checkbox.isChecked()
        if checked: state = 1
        else: state = 0
        self.show_cb_state_changed.emit(self.roi_show_cbs.index(checkbox), state)

    def roi_name_item_changed(self, nameitem):
        
        selected = self.get_selected_roi_row()
        self.name_item_changed.emit(selected, self.name_items[selected].text())
        #print ('roi_name_item_changed: ' +str(selected))


class plotFitWindow(QtWidgets.QWidget):
    widget_closed = QtCore.Signal()
    def __init__(self):
        super().__init__()
        
        self._layout = QtWidgets.QVBoxLayout()  
        self._layout.setContentsMargins(0,0,0,0)
        self.setWindowTitle('Fit plot')
        self.win = pg.GraphicsLayoutWidget()
             
        self.win.setWindowTitle('Peak fit plot')
        self.fitPlots = self.win.addPlot(title="Peak fit")
        self.win.setBackground(background=(255,255,255))
        self.fitPlot = self.fitPlots.plot([],[], 
                        pen=(0,0,0), name="Gaussian peak fit", 
                        antialias=True)
        self.dataPlot =  self.fitPlots.plot([],[], 
                        pen = None, symbolBrush=(255,0,0), 
                        symbolPen='k', name="Data",antialias=True)
        self.fitPlots.setLabel('left','counts')
        self.fitPlots.setLabel('bottom', 'channel')

        self._layout.addWidget(self.win)
        self.setLayout(self._layout)

        #self.resize(400,400)
        

    def closeEvent(self, event):
        # Overrides close event to let controller know that widget was closed by user
        self.widget_closed.emit()

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.raise_()

    def set_data(self,x_fit=[],fit=[],label='',x=[],counts=[],unit='',unit_=''):
        self.fitPlot.setData(x_fit,fit)
        self.fitPlots.setTitle(label)
        self.dataPlot.setData(x,counts)
        self.fitPlots.setLabel('bottom', unit+' ('+unit_+')')
        self.fitPlots.getViewBox().enableAutoRange()
        