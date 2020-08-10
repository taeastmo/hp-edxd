
from PyQt5 import QtCore, QtGui, QtWidgets
from pyeqt.pvWidgets import pvQDoubleSpinBox, pvQLineEdit, pvQLabel, pvQMessageButton, pvQOZButton

class adcController():

    def __init__(self, record_name='16bmb:aim_adc1', file_options=None, environment_file=None):
        self.widget = adcControlWidget()
        

    



class adcControlWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ElapsedPresetVlayout = QtWidgets.QVBoxLayout()
        self.ElapsedPresetVlayout.setObjectName("ElapsedPresetVlayout")
        self.PRTM_pv = pvQDoubleSpinBox(self.record_name+".PRTM")
        self.PLTM_pv = pvQDoubleSpinBox(self.record_name+".PLTM")
        self.PLTM_pv.setDecimals(2)
        self.PRTM_pv.setDecimals(2)
        self.ElapsedPresetVlayout.addWidget(self.PRTM_pv)
        self.ElapsedPresetVlayout.addWidget(self.PLTM_pv)
        self.ElapsedHLayout.addLayout(self.ElapsedPresetVlayout)
        self.setLayout(self.ElapsedPresetVlayout)

    def set_controls_state(self, state):
        self.blockSignals(True)
        if state == 'on' or state == 1:
            self.btnOn.setEnabled(False)
            self.btnOn.setChecked(True)
            self.btnOff.setEnabled(True)
        if state == 'off' or state == 0:
            self.btnOn.setEnabled(True)
            self.btnOn.setChecked(False)
            self.btnOff.setEnabled(False)
        self.blockSignals(False)