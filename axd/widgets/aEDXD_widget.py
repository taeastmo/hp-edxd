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


from PyQt5 import QtCore, QtGui, QtWidgets

from  PyQt5.QtWidgets import QMainWindow, QApplication, QInputDialog, QWidget, QLabel
from hpm.widgets.CustomWidgets import FlatButton, DoubleSpinBoxAlignRight, VerticalSpacerItem, NoRectDelegate, \
    HorizontalSpacerItem, ListTableWidget, VerticalLine, DoubleMultiplySpinBoxAlignRight
from hpm.widgets.PltWidget import plotWindow
from functools import partial

class aEDXDWidget(QMainWindow):
    def __init__(self,app):
        super().__init__()
        
        self.initUi()
        self.app = app

        raw_fig_parameters = 'Spectrum', 'Counts','Energy (keV)' 
        self.raw_widget = aEDXDRawWidget(raw_fig_parameters)
        self.vertical_layout_tab_raw.addWidget(self.raw_widget)

        spectrum_fig_params = 'Spectrum', 'Intensity (arb.)','Energy (keV)'  
        self.spectrum_widget = aEDXDSpectrumWidget(spectrum_fig_params )
        self.vertical_layout_tab_spectrum.addWidget(self.spectrum_widget)

        primary_beam_fig_params = 'MA-EDXD Primary Beam Analysis', 'Intensity (arb.)','Energy (keV)'
        self.primary_beam_widget = aEDXDPrimaryBeamWidget(primary_beam_fig_params)
        self.vertical_layout_tab_primary_beam.addWidget(self.primary_beam_widget)
        
        all_spectra_fig_params = 'MA-EDXD All Spectra', 'Intensity (arb.)','Energy (keV)'
        self.all_spectra_widget = aEDXDAllSpectraWidget(all_spectra_fig_params)
        self.vertical_layout_tab_all_spectra.addWidget(self.all_spectra_widget)
        
        sq_fig_parameters = 'S(q) Merged and Smoothened', 'S(q)', 'q (A^-1)'
        self.sq_widget = aEDXDSqWidget(sq_fig_parameters)
        self.vertical_layout_tab_sq.addWidget(self.sq_widget )

        pdf_fig_parameters = 'G(r)', 'G(r)', 'r (A)' 
        self.pdf_widget = aEDXDPDFWidget(pdf_fig_parameters)
        self.vertical_layout_tab_pdf.addWidget(self.pdf_widget)

        inverse_fig_parameters = 'S(q) filtered', 'S(q)', 'q (A^-1)' 
        self.inverse_widget = aEDXDInverseWidget(inverse_fig_parameters)
        self.vertical_layout_tab_inverse.addWidget(self.inverse_widget)

   
    def raise_widget(self):
        self.show()
        #self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        #self.activateWindow()
        #self.raise_()    
    
    def closeEvent(self, QCloseEvent, *event):
        self.app.closeAllWindows()

    def initUi(self):
        
        self.resize(793, 574)
        self.centralwidget = QtWidgets.QWidget(self)

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)

        self.tab_1 = QtWidgets.QWidget()
        self.vertical_layout_tab_raw = QtWidgets.QVBoxLayout(self.tab_1)
        self.tabWidget.addTab(self.tab_1, "")

        self.tab = QtWidgets.QWidget()
        self.vertical_layout_tab_spectrum = QtWidgets.QVBoxLayout(self.tab)
        self.tabWidget.addTab(self.tab, "")

        self.tab_2 = QtWidgets.QWidget()
        self.vertical_layout_tab_all_spectra = QtWidgets.QVBoxLayout(self.tab_2)
        self.tabWidget.addTab(self.tab_2, "")

        self.tab_3 = QtWidgets.QWidget()
        self.vertical_layout_tab_primary_beam = QtWidgets.QVBoxLayout(self.tab_3)
        self.tabWidget.addTab(self.tab_3, "")

        self.tab_4 = QtWidgets.QWidget()
        self.vertical_layout_tab_sq = QtWidgets.QVBoxLayout(self.tab_4)
        self.tabWidget.addTab(self.tab_4, "")

        self.tab_5 = QtWidgets.QWidget()
        self.vertical_layout_tab_pdf = QtWidgets.QVBoxLayout(self.tab_5)
        self.tabWidget.addTab(self.tab_5, "")

        self.tab_6 = QtWidgets.QWidget()
        self.vertical_layout_tab_inverse = QtWidgets.QVBoxLayout(self.tab_6)
        self.tabWidget.addTab(self.tab_6, "")

        self.horizontalLayout.addWidget(self.tabWidget)
        self.retranslateUi()
        self.centralwidget.setLayout(self.horizontalLayout)

        self.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 793, 22))

        self.file_menu = self.menubar.addMenu('File')
        self.file_op_act = QtWidgets.QAction('Open project', self)        
        self.file_menu.addAction(self.file_op_act)
        self.file_save_act = QtWidgets.QAction('Save project', self)        
        self.file_menu.addAction(self.file_save_act)
        self.file_save_hdf5_act = QtWidgets.QAction('Save to HDF5', self)        
        #self.file_menu.addAction(self.file_save_hdf5_act)

        self.file_exp_menu = QtWidgets.QMenu('Export', self)
        self.file_exp_data_act = QtWidgets.QAction('I(q)', self) 
        self.file_exp_menu.addAction(self.file_exp_data_act)
        self.file_exp_sf_act = QtWidgets.QAction('S(q)', self) 
        self.file_exp_menu.addAction(self.file_exp_sf_act)
        self.file_exp_pdf_act = QtWidgets.QAction('G(r)', self) 
        self.file_exp_menu.addAction(self.file_exp_pdf_act)
        self.file_exp_sf_inv_act = QtWidgets.QAction('Inverse Fourier-filtered S(q)', self) 
        self.file_exp_menu.addAction(self.file_exp_sf_inv_act)
        self.file_menu.addMenu(self.file_exp_menu)
        
        self.opts_menu = self.menubar.addMenu('Options')
        self.tools_files_act = QtWidgets.QAction('Files', self)    
        self.opts_menu.addAction(self.tools_files_act)

        self.opts_proc_act = QtWidgets.QAction('Spectra', self)        
        self.opts_menu.addAction(self.opts_proc_act)
        self.tools_atoms_act = QtWidgets.QAction('Atoms', self)        
        self.opts_menu.addAction(self.tools_atoms_act)
        self.opts_sq_act = QtWidgets.QAction('Scattering factor', self)        
        self.opts_menu.addAction(self.opts_sq_act)
        self.opts_gr_act = QtWidgets.QAction('PDF', self)        
        self.opts_menu.addAction(self.opts_gr_act)

        self.tools_menu = self.menubar.addMenu('Tools')
        self.tools_peaks_act = QtWidgets.QAction('Peak cutting', self)        
        self.tools_menu.addAction(self.tools_peaks_act)
        
        self.setMenuBar(self.menubar)

        sb = self.statusBar()
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setFixedHeight(15)
        
        self.pb_widget = QWidget()
        self._pb_widget_layout = QtWidgets.QHBoxLayout()

        self._pb_widget_layout.addWidget(QtWidgets.QLabel('Progress: '))
        self._pb_widget_layout.addWidget(self.progress_bar)
        self._pb_widget_layout.setContentsMargins(10,0,0,3)
        self.pb_widget.setLayout(self._pb_widget_layout)
        sb.addWidget(self.pb_widget)
        
        '''
        self.setStyleSheet("""
            QTabBar::tab {
                background: lightgray;
                color: black;
                border: 0;
                min-width: 90px; 
                max-width: 250px;
                width: 90px; 
                height: 20px;
                padding: 5px;
            }

            QTabBar::tab:selected {
                background: gray;
                color: white;
            }
        """)
        '''
    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("aEDXDWidget", "aEDXD"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("aEDXDWidget", "Spectrum"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), _translate("aEDXDWidget", "Raw"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("aEDXDWidget", "All spectra"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("aEDXDWidget", "Incident beam"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("aEDXDWidget", "S(q)"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), _translate("aEDXDWidget", "G(r)"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_6), _translate("aEDXDWidget", "S(q) filtered"))

class customWidget(QtWidgets.QWidget):
    widget_closed = QtCore.pyqtSignal()
    def __init__(self, fig_params):
        super().__init__()
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(0,0,0,0)
        self.fig = plotWindow(*fig_params)
        self._layout.addWidget(self.fig)
        self.cursor_fast = QLabel()
        self.cursor_fast.setFixedWidth(70)
        self.cursor = QLabel()
        self.cursor.setFixedWidth(70)
        self.cursor_widget = QWidget()
        self._cursor_widget_layout = QtWidgets.QHBoxLayout()
        self._cursor_widget_layout.setContentsMargins(0,0,0,0)
        self._cursor_widget_layout.addSpacerItem(HorizontalSpacerItem())
        self._cursor_widget_layout.addWidget(self.cursor_fast)
        self._cursor_widget_layout.addWidget(self.cursor)
        self._cursor_widget_layout.addSpacerItem(HorizontalSpacerItem())
        self.cursor_widget.setLayout(self._cursor_widget_layout)
        self._layout.addWidget(self.cursor_widget)
        self.button_widget = QtWidgets.QWidget()
        self._button_widget_layout = QtWidgets.QHBoxLayout()
        self._button_widget_layout.setContentsMargins(0,0,0,0)
        self.button_widget.setLayout(self._button_widget_layout)
        self._layout.addWidget(self.button_widget)
        self.setLayout(self._layout)
        self.create_connections()

    def add_button_widget_item(self, item):
        self._button_widget_layout.addWidget(item)
    
    def add_button_widget_spacer(self):
        self._button_widget_layout.addSpacerItem(HorizontalSpacerItem())

    def create_connections(self):
        self.fig.fast_cursor.connect(self.update_fast_cursor)
        self.fig.cursor.connect(self.update_cursor)

    def raise_widget(self):
        self.show()

    def closeEvent(self, event):
        # Overrides close event to let controller know that widget was closed by user
        self.widget_closed.emit()

    def update_fast_cursor(self, pos):
        c = '%.3f' % (pos)
        self.cursor_fast.setText(c)
        self.fig.set_fast_cursor(pos)

    def update_cursor(self, pos):
        c = "<span style='color: #00CC00'>%0.3f</span>"  % (pos)
        self.cursor.setText(c)
        self.fig.set_cursor(pos)

    def setText(self, text, plot_ind):
        self.fig.set_plot_label(text,plot_ind)

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        

class aEDXDSpectrumWidget(customWidget):
    def __init__(self, fig_params):
        super().__init__(fig_params)
        
        self.cut_peak_btn = FlatButton('Add')
        self.cut_peak_btn.setFixedWidth(90)
        self.cut_peak_btn.setCheckable(True)
        self.add_button_widget_item(QtWidgets.QLabel('E cut region:'))
        self.add_button_widget_item(self.cut_peak_btn)
        self.apply_btn = FlatButton('Apply')
        self.apply_btn.setFixedWidth(90)
        self.add_button_widget_item(self.apply_btn)
        self.add_button_widget_spacer()
        

class aEDXDPrimaryBeamWidget(customWidget):
    def __init__(self, fig_params):
        super().__init__(fig_params)
        

class aEDXDSqWidget(customWidget):
    def __init__(self, fig_params):
        super().__init__(fig_params)
        

class aEDXDPDFWidget(customWidget):
    def __init__(self, fig_params):
        super().__init__(fig_params)
        

class aEDXDAllSpectraWidget(customWidget):
    def __init__(self, fig_params):
        super().__init__(fig_params)
        

class aEDXDInverseWidget(customWidget):
    def __init__(self, fig_params):
        super().__init__(fig_params)
        

class aEDXDRawWidget(customWidget):
    def __init__(self, fig_params):
        super().__init__(fig_params)
        