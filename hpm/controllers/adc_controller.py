
from PyQt5 import QtCore, QtGui, QtWidgets
from pyeqt.pvWidgets import pvQDoubleSpinBox, pvQLineEdit, pvQLabel, pvQMessageButton, pvQOZButton

class adcController():

    def __init__(self, record_name='16bmb:aim_adc1', file_options=None, environment_file=None):
        self.widget = adcControlWidget()
        

    



class adcControlWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)


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


    def make_AcquisitionButtons_groupbox(self, record_name='16bmb:aim_adc1'):

        groupBoxAcq = QtWidgets.QGroupBox(self.centralwidget)

        _groupBoxAcqLayout = QtWidgets.QGridLayout(groupBoxAcq)
    
        btnOn = pvQMessageButton(record_name+".STRT")
        btnOff = pvQMessageButton(record_name+".STOP")
        btnErase = pvQMessageButton(record_name+".ERAS")

        _groupBoxAcqLayout.addWidget(btnOn,0,0)
        _groupBoxAcqLayout.addWidget(btnOff,0,1)
        _groupBoxAcqLayout.addWidget(btnErase,1,0)
        groupBoxAcq.setLayout(_groupBoxAcqLayout)

        
        return groupBoxAcq

    def make_TimeElapsed_groupbox(self):

        self.groupBoxElapsed = QtWidgets.QGroupBox(self.centralwidget)
        
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.groupBoxElapsed)
        self.verticalLayout_11.setContentsMargins(10, 5, 10, 5)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.ElapsedHLayout = QtWidgets.QHBoxLayout()
        self.ElapsedHLayout.setObjectName("ElapsedHLayout")
        self.ElapsedlLblVLayout = QtWidgets.QVBoxLayout()
        self.ElapsedlLblVLayout.setObjectName("ElapsedlLblVLayout")
        self.label = QtWidgets.QLabel(self.groupBoxElapsed)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(50, 0))
        self.label.setObjectName("label")
        self.ElapsedlLblVLayout.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(self.groupBoxElapsed)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMinimumSize(QtCore.QSize(50, 0))
        self.label_2.setObjectName("label_2")
        self.ElapsedlLblVLayout.addWidget(self.label_2)
        self.ElapsedHLayout.addLayout(self.ElapsedlLblVLayout)
        self.ElapsedIndicatorVlayout = QtWidgets.QVBoxLayout()
        self.ElapsedIndicatorVlayout.setObjectName("ElapsedIndicatorVlayout")
        self.lblLiveTime = QtWidgets.QLabel(self.groupBoxElapsed)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblLiveTime.sizePolicy().hasHeightForWidth())
        self.lblLiveTime.setSizePolicy(sizePolicy)
        self.lblLiveTime.setMinimumSize(QtCore.QSize(60, 0))
        self.lblLiveTime.setMidLineWidth(2)
        self.lblLiveTime.setObjectName("lblLiveTime")
        self.ElapsedIndicatorVlayout.addWidget(self.lblLiveTime)
        self.lblRealTime = QtWidgets.QLabel(self.groupBoxElapsed)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblRealTime.sizePolicy().hasHeightForWidth())
        self.lblRealTime.setSizePolicy(sizePolicy)
        self.lblRealTime.setMinimumSize(QtCore.QSize(60, 0))
        self.lblRealTime.setObjectName("lblRealTime")
        self.ElapsedIndicatorVlayout.addWidget(self.lblRealTime)
        self.ElapsedHLayout.addLayout(self.ElapsedIndicatorVlayout)
        self.verticalLayout_11.addLayout(self.ElapsedHLayout)


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