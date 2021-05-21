# -*- coding: utf8 -*-

from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from mypyeqt.CustomWidgets import HorizontalSpacerItem, VerticalSpacerItem, FlatButton
from functools import partial
import time
from mypyeqt.pv_model import PV
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QComboBox, QDoubleSpinBox, QCheckBox, QPushButton, QAction

from mypyeqt.pvServer import pvServer
import numpy as np
from epics import PV, caget, caput
from mypyeqt.epicsMonitor import epicsMonitor
import pyqtgraph as pg

class pvQWidget(QWidget):
    def __init__(self, pvName=None, autoconnect = True):
       
        self.setEnabled( False)
        self.pv_name = pvName
        self.connected = False
        self.pv_server = None
        if autoconnect and self.pv_name is not None:
            self.connect()

    def connect(self, pvName=None):
        if not self.connected:
            if pvName is None:
                pvName = self.pv_name
    
            if pvName is not None:    
                self.pv_name = pvName
                if self.pv_server is None:
                    self.pv_server = pvServer()
                self.pv = self.pv_server.get_pv(pvName)
                
                self.monitor = self.pv_server.get_pv_monitor(pvName)
                self.status = self.pv.status
                if self.status is not None:
                    self.setEnabled( True)
                    val = self.pv.get()
                    self.monitorCallback(val)
                self.connect_pv()

    def disconnect(self):
        if self.connected:
            self.disconnect_pv()
            
            
        
    def connect_pv(self):
        if not self.connected:
            self.monitor.callback_triggered.connect(self.monitorCallback)
            self.monitor.connection_callback_triggered.connect(self.connectionChanged)
            self.setToolTip(self.pv_name)
            self.connectionChanged(True)

    def disconnect_pv(self):
        if self.connected:
            self.monitor.connection_callback_triggered.disconnect(self.connectionChanged)
            self.monitor.callback_triggered.disconnect(self.monitorCallback)
            self.setToolTip('')
            self.connectionChanged(False)
           
    def connectionChanged(self, conn):
        # prototype function, can be offerridden 
        # to show whether widgets are connected 
        # conn is a bool
        self.connected = conn
        self.setEnabled(conn)
        
    def WidgetValueChangedCallback(self,value):
        if self.connected:
            # value must be a string !!!
            self.pv.put(value)
            #print('caput ' + self.pv_name + ' ' +value)
       
    # set value is called when monitor detects a change
    def monitorCallback(self, value):
        if self.connected:
            self.updateView(value)
            #print(self.pv_name + " " + str(value))

    def updateView(self, value):
        # prototype, children override this funciton
        pass

class pvQDoubleSpinBox(QDoubleSpinBox, pvQWidget):
    def __init__(self, pvname=None, autoconnect = True):
        QDoubleSpinBox.__init__(self)
        
        widget = self
        QDoubleSpinBox.setGroupSeparatorShown(widget, True)
        minimum = -10000000000000000.0
        maximum = 10e16      
                    
        QDoubleSpinBox.setMinimum(widget, minimum)
        QDoubleSpinBox.setMaximum(widget, maximum)
        '''QDoubleSpinBox.setDecimals(widget, 3)
        QDoubleSpinBox.setSingleStep(widget, 0.001)'''

        pvQWidget.__init__(self, pvname, autoconnect)

        QDoubleSpinBox.setKeyboardTracking(widget, False)

        self.valueChanged.connect(self.valueChangedCallbackPreTreat)
        


    def valueChangedCallbackPreTreat(self, val):
        val = round(val,3)
        val = str(val)
        self.WidgetValueChangedCallback(val )


    # set value is called when monitor detects a change
    def updateView(self, value):
        
        # make sure that the db record has a PREC field set, 
        # otherwise the prescision of the values returned by the monitor is arbitrary
        value = float(value)
        widget = self
        QDoubleSpinBox.blockSignals(widget, True)
        QDoubleSpinBox.setValue(widget, float(value))
        QDoubleSpinBox.blockSignals(widget, False)  
        

class pvQLineEdit(QLineEdit, pvQWidget):
    def __init__(self, pvname=None, autoconnect = True):
        widget = self
        QLineEdit.__init__(widget)
        pvQWidget.__init__(widget, pvname, autoconnect)
        
        self.editingFinished.connect(lambda:self.valueChangedCallbackPreTreat(self.text()))


    def valueChangedCallbackPreTreat(self, val):
        if len(val)>39:
            val = str(val)[:39]
            self.updateView(val)
        self.WidgetValueChangedCallback(val )          

    def updateView(self, value):
        widget = self
        QLineEdit.blockSignals(widget, True)
        QLineEdit.setText(widget, str(value))
        QLineEdit.blockSignals(widget, False)    

class pvQLabel(QLabel, pvQWidget):
    def __init__(self, pvname=None, autoconnect = True):
        widget = self
        QLabel.__init__(widget)
        pvQWidget.__init__(widget, pvname, autoconnect)
        
        
    def updateView(self, value):
        widget = self
        QLabel.setText(widget, str(value))



class pvStripChart(pg.PlotWidget, pvQWidget):
    def __init__(self, pvname=None, autoconnect = True):
        widget = self
        pg.PlotWidget.__init__(widget)
        
        pvQWidget.__init__(widget, pvname, autoconnect)

        self.plotForeground = pg.PlotDataItem([], title="",
                antialias=True, pen=pg.mkPen(color=(255,255,255), width=1) )
        self.addItem(self.plotForeground)

        self.data_array = []

        
    def updateView(self, value):
        widget = self
        value = float(value)
        try:
            self.data_array.append(value)
            self.plotForeground.setData(np.asarray(self.data_array))
        except:
            pass



class pvQMessageButton(QPushButton, pvQWidget):
    def __init__(self, pvname=None, message = '', autoconnect = True):
        widget = self
        QPushButton.__init__(widget)
        pvQWidget.__init__(widget, pvname)
 
        self.setMessage(message)
        
        self.clicked.connect(self.valueChangedCallbackPreTreat)

    def setMessage(self, message =''):
        self.message = str(message)
        QPushButton.setText(self, self.message)

    def valueChangedCallbackPreTreat(self, val):
        val = str(self.message)
        self.WidgetValueChangedCallback(val )    

class pvQOZButton(QPushButton, pvQWidget):
    def __init__(self, pvname=None, autoconnect = True):
        widget = self
        QPushButton.__init__(widget)
        pvQWidget.__init__(widget, pvname, autoconnect)
        onam = pvname+'.ONAM'
        znam = pvname+'.ZNAM'
        self.onam = caget(onam)
        self.znam = caget(znam)
        QPushButton.setCheckable(widget, True)
        self.clicked.connect(self.valueChangedCallbackPreTreat)
        
    def valueChangedCallbackPreTreat(self, val):
        if val :
            val = '1'
        else:
            val = '0'
        self.WidgetValueChangedCallback(val )    

    def updateView(self, value):
        if type(value) == str:
            value = value == self.onam or value == '1'
        widget = self
        QPushButton.blockSignals(widget, True)
        QPushButton.setChecked(widget, value)
        QPushButton.blockSignals(widget, False)    
        

class pvQCheckBox(QCheckBox, pvQWidget):

    def __init__(self, pvname=None, autoconnect = True):
        QCheckBox.__init__(self)
        pvQWidget.__init__(self, pvname, autoconnect)
        onam = pvname+'.ONAM'
        znam = pvname+'.ZNAM'
        desc = pvname+'.DESC'
        self.desc = caget(desc)
        self.onam = caget(onam)
        self.znam = caget(znam)

        widget = self
        QCheckBox.setCheckable(widget, True)
        QCheckBox.setText(widget, self.desc)
        
        self.clicked.connect(self.valueChangedCallbackPreTreat)
       

    def valueChangedCallbackPreTreat(self, val):
        if val :
            val = '1'
        else:
            val = '0'
        self.WidgetValueChangedCallback(val )  

    def updateView(self, value):
        if type(value) == type(''):
            value = value == self.onam or value == '1'
        widget = self
        QCheckBox.blockSignals(widget, True)
        QCheckBox.setChecked(widget, value)
        QCheckBox.blockSignals(widget, False)    

class pvQComboBox(QComboBox, pvQWidget):
    def __init__(self, myPV):
        QComboBox.__init__(self)
        pvQWidget.__init__(self, myPV)
        widget = self
        items = myPV._items
        for item in items:
            QComboBox.addItem(widget, item)
        val = myPV._val            
        self.setValue(widget, [val])
        self.currentTextChanged.connect(self.valueChangedCallback)

    def setValue(self, tag, value):
        pvQWidget.setValue(self, value)
        value = self.val
        self.blockSignals(True)
       
        widget = self
        current_value = widget.currentText()
        if value != current_value:
            QComboBox.setCurrentText(widget, str(value))
        self.blockSignals(False)    





