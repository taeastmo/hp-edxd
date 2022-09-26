# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from mypyeqt.pvWidgets import pvQDoubleSpinBox, pvQLineEdit, pvQLabel, pvQMessageButton, pvQOZButton, pvQProgressBar
from hpm.widgets.PltWidget import PltWidget



from hpm.widgets.CustomWidgets import FlatButton, DoubleSpinBoxAlignRight, VerticalSpacerItem, NoRectDelegate, \
    HorizontalSpacerItem, ListTableWidget, VerticalLine, DoubleMultiplySpinBoxAlignRight

import os
from .. import style_path, icons_path


class Ui_xrda(object):
    def setupUi(self, xrda):
        #xrda.setObjectName("xrda")
        xrda.resize(1100, 615)
        self.centralwidget = QtWidgets.QWidget(xrda)
        self.centralwidget.setObjectName("centralwidget")


        self._layout = QtWidgets.QVBoxLayout()
        self._main_layout = QtWidgets.QHBoxLayout()

        self._main_layout.addWidget(menuWidget(xrda))

        self.bottom_layout = QtWidgets.QHBoxLayout()


        self.splitter_widget = QtWidgets.QWidget(xrda)
        self._splitter_widget_layout = QtWidgets.QHBoxLayout(self.splitter_widget)
        self.splitter_horizontal = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter_horizontal.addWidget(QtWidgets.QTextEdit(xrda))
        self.splitter_horizontal.addWidget(QtWidgets.QTextEdit(xrda))
        #self.splitter_horizontal.setSizes([800,800])
        self._splitter_widget_layout.addWidget(self.splitter_horizontal)
        self.splitter_widget.setLayout(self._splitter_widget_layout)

        self._main_layout.addWidget(self.splitter_widget)

        self._layout.addLayout(self._main_layout)
        self._layout.addLayout(self.bottom_layout)

        self.centralwidget.setLayout(self._layout)

        xrda.setCentralWidget(self.centralwidget)
        
        self.menubar = QtWidgets.QMenuBar(xrda)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1236, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuControl = QtWidgets.QMenu(self.menubar)
        self.menuControl.setObjectName("menuControl")
        self.menuDisplay = QtWidgets.QMenu(self.menubar)
        self.menuDisplay.setObjectName("menuDisplay")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        xrda.setMenuBar(self.menubar)
        self.actionBackground = QtWidgets.QAction(xrda)
        self.actionBackground.setObjectName("actionBackground")
        self.actionSave_As = QtWidgets.QAction(xrda)
        self.actionSave_As.setEnabled(False)
        self.actionSave_As.setObjectName("actionSave_As")
        self.actionPrint = QtWidgets.QAction(xrda)
        self.actionPrint.setObjectName("actionPrint")
        self.actionPreferences = QtWidgets.QAction(xrda)
        self.actionPreferences.setObjectName("actionPreferences")
        self.actionExit = QtWidgets.QAction(xrda)
        self.actionExit.setObjectName("actionExit")
        self.actionPresets = QtWidgets.QAction(xrda)
        self.actionPresets.setObjectName("actionPresets")
        self.actionCalibrate_energy = QtWidgets.QAction(xrda)
        self.actionCalibrate_energy.setEnabled(False)
        self.actionCalibrate_energy.setObjectName("actionCalibrate_energy")
        self.actionPreferences_2 = QtWidgets.QAction(xrda)
        self.actionPreferences_2.setObjectName("actionPreferences_2")
        self.actionJCPDS = QtWidgets.QAction(xrda)
        self.actionJCPDS.setEnabled(False)
        self.actionJCPDS.setObjectName("actionJCPDS")
        self.actionFit_peaks = QtWidgets.QAction(xrda)
        self.actionFit_peaks.setObjectName("actionFit_peaks")
        self.actionAbout = QtWidgets.QAction(xrda)
        self.actionAbout.setObjectName("actionAbout")
        self.actionOpen_detector = QtWidgets.QAction(xrda)
        self.actionOpen_detector.setObjectName("actionOpen_detector")
        self.actionOpen_file = QtWidgets.QAction(xrda)
        self.actionOpen_file.setObjectName("actionOpen_file")
        self.actionCalibrate_2theta = QtWidgets.QAction(xrda)
        self.actionCalibrate_2theta.setEnabled(False)
        self.actionCalibrate_2theta.setObjectName("actionCalibrate_2theta")
        self.actionFluor = QtWidgets.QAction(xrda)
        self.actionFluor.setEnabled(False)
        self.actionFluor.setObjectName("actionFluor")
        self.actionROIs = QtWidgets.QAction(xrda)
        self.actionROIs.setEnabled(False)
        self.actionROIs.setObjectName("actionROIs")
        self.actionOverlay = QtWidgets.QAction(xrda)
        self.actionOverlay.setEnabled(False)
        self.actionOverlay.setObjectName("actionOverlay")
        self.actionExport_pattern = QtWidgets.QAction(xrda)
        self.actionExport_pattern.setEnabled(False)
        self.actionExport_pattern.setObjectName("actionExport_pattern")
        self.actionSave_next = QtWidgets.QAction(xrda)
        self.actionSave_next.setEnabled(False)
        self.actionSave_next.setObjectName("actionSave_next")
        self.actionPressure = QtWidgets.QAction(xrda)
        self.actionPressure.setEnabled(False)
        self.actionPressure.setObjectName("actionPressure")
        self.actionDisplayPrefs = QtWidgets.QAction(xrda)
        self.actionDisplayPrefs.setObjectName("actionDisplayPrefs")
        self.menuFile.addAction(self.actionOpen_file)
        self.menuFile.addAction(self.actionOpen_detector)
        self.menuFile.addAction(self.actionOverlay)
        self.menuFile.addAction(self.actionSave_next)
        self.menuFile.addAction(self.actionSave_As)
        self.menuFile.addAction(self.actionExport_pattern)
        self.menuFile.addAction(self.actionPreferences)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuControl.addAction(self.actionCalibrate_energy)
        self.menuControl.addAction(self.actionCalibrate_2theta)
        self.menuDisplay.addAction(self.actionJCPDS)
        self.menuDisplay.addAction(self.actionFluor)
        self.menuDisplay.addAction(self.actionROIs)
        self.menuDisplay.addAction(self.actionPressure)
        self.menuDisplay.addAction(self.actionDisplayPrefs)
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuControl.menuAction())
        self.menubar.addAction(self.menuDisplay.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        QtCore.QMetaObject.connectSlotsByName(xrda)

        self.menuFile.setTitle("File")
        self.menuControl.setTitle("Control")
        self.menuDisplay.setTitle("Display")
        self.menuHelp.setTitle("Help")
        self.actionBackground.setText("Background")
        self.actionSave_As.setText("Save As")
        self.actionPrint.setText("Print")
        self.actionPreferences.setText("Preferences")
        self.actionExit.setText("Exit")
        self.actionPresets.setText("Presets...")
        self.actionCalibrate_energy.setText("Calibrate energy...")
        self.actionPreferences_2.setText("Preferences...")
        self.actionJCPDS.setText("Phase")
        self.actionFit_peaks.setText("Fit peaks...")
        self.actionAbout.setText("About")
        self.actionOpen_detector.setText("Open detector...")
        self.actionOpen_file.setText("Open file...")
        self.actionCalibrate_2theta.setText("Calibrate 2theta...")
        self.actionFluor.setText("Fluorescence")
        self.actionROIs.setText("ROIs")
        self.actionOverlay.setText("Overlay")
        self.actionExport_pattern.setText("Export pattern")
        self.actionSave_next.setText("Save next")
        self.actionPressure.setText("Pressure")
        self.actionDisplayPrefs.setText("Colors options")


class menuWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
    
        
        self._menu_layout = QtWidgets.QVBoxLayout()
        self._menu_layout.setContentsMargins(5, 0, 3, 0)
        self._menu_layout.setSpacing(5)

        self.save_as_btn = FlatButton()
        self.save_as_btn.setEnabled(False)
        self.save_btn = FlatButton()
        self.save_btn.setEnabled(False)
        self.load_btn = FlatButton()
        self.undo_btn = FlatButton()
        self.reset_btn = FlatButton()
        self.export_btn = FlatButton()

        self.angle_btn = FlatButton()
        self.spectra_btn = FlatButton()
        self.atoms_btn = FlatButton()
        self.sq_btn = FlatButton('Sq')
        self.pdf_btn = FlatButton('Gr')
        self.peaks_btn = FlatButton()

        self._menu_layout.addSpacerItem(
            QtWidgets.QSpacerItem(10, 25, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self._menu_layout.addWidget(self.load_btn)
        self._menu_layout.addWidget(self.save_btn)
        self._menu_layout.addWidget(self.save_as_btn)
        self._menu_layout.addSpacerItem(
            QtWidgets.QSpacerItem(10, 30, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self._menu_layout.addWidget(self.undo_btn)
        self._menu_layout.addWidget(self.reset_btn)
        self._menu_layout.addSpacerItem(
            QtWidgets.QSpacerItem(10, 30, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self._menu_layout.addWidget(self.angle_btn)
        self._menu_layout.addWidget(self.spectra_btn)
        self._menu_layout.addWidget(self.atoms_btn)
        self._menu_layout.addWidget(self.sq_btn)
        self._menu_layout.addWidget(self.pdf_btn)
        self._menu_layout.addSpacerItem(
            QtWidgets.QSpacerItem(10, 30, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        
        self._menu_layout.addWidget(self.peaks_btn)

        self._menu_layout.addSpacerItem(VerticalSpacerItem())

        self.setLayout(self._menu_layout)

        self.style_widgets()
        self.add_tooltips()

    def style_widgets(self):

            
        button_height = 32
        button_width = 32

        icon_size = QtCore.QSize(22, 22)
        self.save_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, 'save.ico')))
        self.save_btn.setIconSize(icon_size)
        self.save_btn.setMinimumHeight(button_height)
        self.save_btn.setMaximumHeight(button_height)
        self.save_btn.setMinimumWidth(button_width)
        self.save_btn.setMaximumWidth(button_width)

        self.save_as_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, 'save_as.ico')))
        self.save_as_btn.setIconSize(icon_size)
        self.save_as_btn.setMinimumHeight(button_height)
        self.save_as_btn.setMaximumHeight(button_height)
        self.save_as_btn.setMinimumWidth(button_width)
        self.save_as_btn.setMaximumWidth(button_width)

        self.load_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, 'open.ico')))
        self.load_btn.setIconSize(icon_size)
        self.load_btn.setMinimumHeight(button_height)
        self.load_btn.setMaximumHeight(button_height)
        self.load_btn.setMinimumWidth(button_width)
        self.load_btn.setMaximumWidth(button_width)

        self.undo_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, 'undo.ico')))
        self.undo_btn.setIconSize(icon_size)
        self.undo_btn.setMinimumHeight(button_height)
        self.undo_btn.setMaximumHeight(button_height)
        self.undo_btn.setMinimumWidth(button_width)
        self.undo_btn.setMaximumWidth(button_width)

        self.reset_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, 'restore.ico')))
        self.reset_btn.setIconSize(icon_size)
        self.reset_btn.setMinimumHeight(button_height)
        self.reset_btn.setMaximumHeight(button_height)
        self.reset_btn.setMinimumWidth(button_width)
        self.reset_btn.setMaximumWidth(button_width)

        self.export_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, 'export.ico')))
        self.export_btn.setIconSize(icon_size)
        self.export_btn.setMinimumHeight(button_height)
        self.export_btn.setMaximumHeight(button_height)
        self.export_btn.setMinimumWidth(button_width)
        self.export_btn.setMaximumWidth(button_width)

        self.angle_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, 'import.ico')))
        self.angle_btn.setIconSize(icon_size)
        self.angle_btn.setMinimumHeight(button_height)
        self.angle_btn.setMaximumHeight(button_height)
        self.angle_btn.setMinimumWidth(button_width)
        self.angle_btn.setMaximumWidth(button_width)

        self.spectra_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, 'spectra.ico')))
        self.spectra_btn.setIconSize(icon_size)
        self.spectra_btn.setMinimumHeight(button_height)
        self.spectra_btn.setMaximumHeight(button_height)
        self.spectra_btn.setMinimumWidth(button_width)
        self.spectra_btn.setMaximumWidth(button_width)

        self.atoms_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, 'atoms1.ico')))
        self.atoms_btn.setIconSize(icon_size)
        self.atoms_btn.setMinimumHeight(button_height)
        self.atoms_btn.setMaximumHeight(button_height)
        self.atoms_btn.setMinimumWidth(button_width)
        self.atoms_btn.setMaximumWidth(button_width)

        #self.sq_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, 'sq1.ico')))
        self.sq_btn.setIconSize(icon_size)
        self.sq_btn.setMinimumHeight(button_height)
        self.sq_btn.setMaximumHeight(button_height)
        self.sq_btn.setMinimumWidth(button_width)
        self.sq_btn.setMaximumWidth(button_width)

        #self.pdf_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, 'pdf1.ico')))
        self.pdf_btn.setIconSize(icon_size)
        self.pdf_btn.setMinimumHeight(button_height)
        self.pdf_btn.setMaximumHeight(button_height)
        self.pdf_btn.setMinimumWidth(button_width)
        self.pdf_btn.setMaximumWidth(button_width)
    
        self.peaks_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, 'cut.ico')))
        self.peaks_btn.setIconSize(icon_size)
        self.peaks_btn.setMinimumHeight(button_height)
        self.peaks_btn.setMaximumHeight(button_height)
        self.peaks_btn.setMinimumWidth(button_width)
        self.peaks_btn.setMaximumWidth(button_width)

        

    def add_tooltips(self):
        self.load_btn.setToolTip('Open Project')
        self.save_btn.setToolTip('Save Project')
        self.save_as_btn.setToolTip('Save Project As...')
        self.undo_btn.setToolTip('Undo')
        self.reset_btn.setToolTip('Reset to last saved configuration')
        self.angle_btn.setToolTip('EDXD Files Input')
        self.spectra_btn.setToolTip('Spectra options')
        self.atoms_btn.setToolTip('Atoms options')
        self.sq_btn.setToolTip('Scattering Factor options')
        self.pdf_btn.setToolTip('PDF options')
        self.peaks_btn.setToolTip('Peak cutting')