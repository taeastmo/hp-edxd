

from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from pyeqt.CustomWidgets import HorizontalSpacerItem, VerticalSpacerItem, FlatButton
from functools import partial
import time
from pyeqt.pv_model import PV
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QComboBox, QDoubleSpinBox, QCheckBox, QPushButton, QAction

from pyeqt.pvServer import pvServer

from epics import PV, caget, caput
from pyeqt.epicsMonitor import epicsMonitor


class pvQWidget(QWidget):
    def __init__(self, pvName):
        #super().__init__(self)
        self.setEnabled( False)
        self.pv_server = pvServer()
        self.pv = self.pv_server.get_pv(pvName)
        self.pv_name = pvName
        self.setToolTip(self.pv_name)
        self.monitor = self.pv_server.get_pv_monitor(self.pv_name)
        self.status = self.pv.status
        if self.status is not None:
            self.setEnabled( True)
            val = self.pv.get()
            self.monitorCallback(val)
        self.connect_pv()
        
    def connect_pv(self):
        self.monitor.callback_triggered.connect(self.monitorCallback)
        self.monitor.connection_callback_triggered.connect(self.connectionChanged)

    def disconnect_pv(self):
        self.monitor.connection_callback_triggered.disconnect(self.connectionChanged)
        self.monitor.callback_triggered.disconnect(self.monitorCallback)

    def connectionChanged(self, conn):
        # prototype function, can be offerridden 
        # to show whether widgets are connected 
        # conn is a bool
        self.setEnabled(conn)
        
    def WidgetValueChangedCallback(self,value):
        # value must be a string !!!
        self.pv.put(value)
        print('caput ' + self.pv_name + ' ' +value)
       
    # set value is called when monitor detects a change
    def monitorCallback(self, value):
        self.updateView(value)
        print(self.pv_name + " " + str(value))

    def updateView(self, value):
        # prototype, children override this funciton
        pass

class pvQDoubleSpinBox(QDoubleSpinBox, pvQWidget):
    def __init__(self, pvname):
        QDoubleSpinBox.__init__(self)
        
        pvQWidget.__init__(self, pvname)

        widget = self
        QDoubleSpinBox.setGroupSeparatorShown(widget, True)
        minimum = -10000000000000000.0
        maximum = 10e16        
                    
        QDoubleSpinBox.setMinimum(widget, minimum)
        QDoubleSpinBox.setMaximum(widget, maximum)
        
        QDoubleSpinBox.setKeyboardTracking(widget, False)
        

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
    def __init__(self, pvname):
        widget = self
        QLineEdit.__init__(widget)
        pvQWidget.__init__(widget, pvname)
        
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
    def __init__(self, pvname):
        widget = self
        QLabel.__init__(widget)
        pvQWidget.__init__(widget, pvname)
        
        
    def updateView(self, value):
        widget = self
        QLabel.setText(widget, str(value))

class pvQMessageButton(QPushButton, pvQWidget):
    def __init__(self, pvname, message = ''):
        widget = self
        QPushButton.__init__(widget)
        pvQWidget.__init__(widget, pvname)
 
        self.message = str(message)
        QPushButton.setText(widget, self.message)
        self.clicked.connect(self.valueChangedCallbackPreTreat)

    def setMessage(self, message =''):
        self.message = str(message)

    def valueChangedCallbackPreTreat(self, val):
        val = str(self.message)
        self.WidgetValueChangedCallback(val )    

class pvQOZButton(QPushButton, pvQWidget):
    def __init__(self, pvname):
        widget = self
        QPushButton.__init__(widget)
        pvQWidget.__init__(widget, pvname)
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

    def __init__(self, pvname):
        QCheckBox.__init__(self)
        pvQWidget.__init__(self, pvname)
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





