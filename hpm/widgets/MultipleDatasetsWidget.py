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
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5 import QtWidgets, QtCore
import copy
import numpy as np
import pyqtgraph as pg
from hpm.widgets.CustomWidgets import FlatButton, DoubleSpinBoxAlignRight, VerticalSpacerItem, NoRectDelegate, \
    HorizontalSpacerItem, ListTableWidget, VerticalLine, DoubleMultiplySpinBoxAlignRight


class MultiSpectraWidget(QtWidgets.QWidget):

    color_btn_clicked = QtCore.pyqtSignal(int, QtWidgets.QWidget)
    #env_btn_clicked = QtCore.pyqtSignal(int)
    show_cb_state_changed = QtCore.pyqtSignal(int, int)
    pv_item_changed = QtCore.pyqtSignal(int, str)
    widget_closed = QtCore.pyqtSignal()
    key_signal = pyqtSignal(str)
    plotMouseMoveSignal = pyqtSignal(float)  
    plotMouseCursorSignal = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self._layout = QtWidgets.QVBoxLayout()  
        self.setWindowTitle('Multiple spectra view')
        self.button_widget = QtWidgets.QWidget(self)
        self.button_widget.setMaximumHeight(40)
        self.button_widget.setObjectName('multispectra_control_button_widget')
        self._button_layout = QtWidgets.QHBoxLayout()
        self._button_layout.setContentsMargins(0, 0, 0, 0)
        self._button_layout.setSpacing(6)
        self.add_btn = FlatButton('Open folder')
        self.add_btn.setMaximumWidth(90)
        self.edit_btn = FlatButton('Edit')
        self.delete_btn = FlatButton('Delete')
        self.clear_btn = FlatButton('Clear')
        self._button_layout.addWidget(self.add_btn)
        self._button_layout.addSpacerItem(HorizontalSpacerItem())
        self.button_widget.setLayout(self._button_layout)
        self._layout.addWidget(self.button_widget)
        self.folder_widget = QtWidgets.QWidget(self)
        self._folder_layout = QtWidgets.QHBoxLayout()
        self._folder_layout.setContentsMargins(0, 0, 0, 0)
        self._folder_layout.setSpacing(6)
        self._folder_layout.addWidget(QtWidgets.QLabel('Folder   '))
        self.file_folder = QtWidgets.QLabel('')
        self.file_folder.setAlignment(QtCore.Qt.AlignRight)
        self._folder_layout.addWidget(self.file_folder)
        self.folder_widget.setLayout(self._folder_layout)
        self._layout.addWidget(self.folder_widget)
        self.filter_widget = QtWidgets.QWidget(self)
        self._filter_layout = QtWidgets.QHBoxLayout()
        self._filter_layout.setContentsMargins(0, 0, 0, 0)
        self._filter_layout.setSpacing(6)
        self._filter_layout.addWidget(QtWidgets.QLabel('Filter   '))
        self.file_filter = QtWidgets.QLineEdit('')
        self.file_filter.setAlignment(QtCore.Qt.AlignRight)
        self.file_filter_refresh_btn = QtWidgets.QPushButton("Reload")
        self._filter_layout.addWidget(self.file_filter)
        self._filter_layout.addWidget(self.file_filter_refresh_btn)
        self.filter_widget.setLayout(self._filter_layout)
        self._layout.addWidget(self.filter_widget)
        self._body_layout = QtWidgets.QHBoxLayout()
        self.file_view_tabs= QtWidgets.QTabWidget(self)
        self.file_view_tabs.setObjectName("file_view_tabs")
        self.make_img_plot()
        self.plot_widget = self.win
        self.file_view_tabs.addTab(self.plot_widget, 'Spectra')
        self.file_list_view = QtWidgets.QListWidget()
        self.file_view_tabs.addTab(self.file_list_view, 'Files')
        self._body_layout.addWidget(self.file_view_tabs)
        self._layout.addLayout(self._body_layout)
        self.file_name = QtWidgets.QLabel('')
        self.file_name_fast = QtWidgets.QLabel('')
        self.file_name_fast.setObjectName("file_name_fast")
        self._layout.addWidget(self.file_name_fast)
        self.file_name_fast.setStyleSheet("""
                color: #909090;
        """)
        self._layout.addWidget(self.file_name)
        self.setLayout(self._layout)
        self.style_widgets()
        self.env_show_cbs = []
        self.pv_items = []
        self.index_items = []
        self.resize(300,633)

    def get_selected_row(self):
        selected  = self.file_list_view.selectionModel().selectedRows()
        if len(selected):
            row = selected[0].row()
        else:
            row = -1
        return row

    def reload_files(self, files):
        if len(files):
            row =  self.get_selected_row()
            self.file_list_view.blockSignals(True)
            self.file_list_view.clear()
            self.file_list_view.addItems(files)
            self.file_list_view.blockSignals(False)
            if row < 0 or row >= len(files):
                row = 0
            self.file_list_view.setCurrentRow(row)
        else:
            self.file_list_view.clear()

    def set_spectral_data(self, data):
        if len(data):
            img_data = np.log10( data+.5)
            self.img.setImage(img_data)
        else:
            self.img.clear()

    def select_file(self,index):
        self.file_list_view.blockSignals(True)
        self.file_list_view.setCurrentRow(index)
        self.file_list_view.blockSignals(False)

    def select_spectrum(self, index):
        self.set_cursor_pos(index, None)

    def select_channel(self, E):
        self.set_cursor_pos(None, E)
      
    def make_img_plot(self):
        ## Create window with GraphicsView widget
        self.win = pg.PlotWidget(parent=self)
        self.win.getPlotItem().setLabel(axis='left', text='Channel')
        self.win.getPlotItem().setLabel(axis='bottom', text='File index')

        #self.plot = pg.PlotItem(self.win)
        self.view = self.win.getViewBox()
        self.view.setMouseMode(pg.ViewBox.RectMode)
        self.view.setAspectLocked(False)
        ## Create image item
        self.img = pg.ImageItem(border='w')
        #self.img.setScaledMode()
        self.view.addItem(self.img)

        self.vLine = pg.InfiniteLine(movable=False, pen=pg.mkPen(color=(200, 200, 200), width=2 , style=QtCore.Qt.DashLine))
        self.hLine = pg.InfiniteLine(movable=False, angle = 0, pen=pg.mkPen(color=(0, 255, 0), width=2 , style=QtCore.Qt.DashLine))
        self.vLineFast = pg.InfiniteLine(movable=False,pen=pg.mkPen({'color': '606060', 'width': 1, 'style':QtCore.Qt.DashLine}))
        self.proxy = pg.SignalProxy(self.win.scene().sigMouseMoved, rateLimit=20, slot=self.fastCursorMove)

        #self.vLine.sigPositionChanged.connect(self.cursor_dragged)
        
        self.cursors = [self.vLine, self.vLineFast]
        self.cursorPoints = [(np.nan,np.nan),(np.nan,np.nan)]
        
        self.view.addItem(self.vLine, ignoreBounds=True)
        self.view.addItem(self.hLine, ignoreBounds=True)
        self.view.addItem(self.vLineFast, ignoreBounds=True)
        self.view.mouseClickEvent = self.customMouseClickEvent


    def fastCursorMove(self, evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self.view.sceneBoundingRect().contains(pos):
            mousePoint = self.view.mapSceneToView(pos)
            index = mousePoint.x()
            if index >= 0:
                self.vLineFast.setPos(index)
                self.plotMouseMoveSignal.emit(index)

    def customMouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton:
            self.view.enableAutoRange(enable=1) 
        elif ev.button() == QtCore.Qt.LeftButton: 
            pos = ev.pos()  ## using signal proxy turns original arguments into a tuple
            mousePoint = self.view.mapToView(pos)
            index= int(mousePoint.x())
            E = mousePoint.y()
            if index >=0 :
                self.set_cursor_pos(int(index), E)
                self.plotMouseCursorSignal.emit([index, E])  
        ev.accept()

    def set_cursorFast_pos(self, index, E):
        self.vLine.blockSignals(True)
        self.vLine.setPos(int(index)+0.5)
        self.cursorPoints[1] = (index,E)
        self.vLineFast.blockSignals(False)


    def set_cursor_pos(self, index = None, E=None):
        if E != None:
            self.hLine.blockSignals(True)
            self.hLine.setPos(E)
            self.hLine.blockSignals(False)
            self.cursorPoints[0] = (self.cursorPoints[0][0],E)
        if index != None:
            self.vLine.blockSignals(True)
            self.vLine.setPos(int(index)+0.5)
            self.cursorPoints[0] = (index,self.cursorPoints[0][1])
            self.vLine.blockSignals(False)
        
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

    def style_widgets(self):
        self.setStyleSheet("""
            #env_control_button_widget FlatButton {
                min-width: 90;
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

  
