
import json
from PyQt5.QtCore import pyqtSignal, Qt

import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget

from functools import partial
import copy



class PeriodicTable(QWidget):
    
    element_clicked_signal = pyqtSignal(str)
    def __init__(self, options):
        super().__init__()
        with open("utilities/elements.json") as f:
            self.data = json.load(f)
            f.close()
        self.setUI(options)
    
    def setUI(self, options):
        
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(2)
        symbols = [
        "H","","","","","","","","","","","","","","","","","He",
        "Li","Be","","","","","","","","","","","B","C","N","O","F","Ne",
        "Na","Mg","","","","","","","","","","","Al","Si","P","S","Cl","Ar","K","Ca","Sc","Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se","Br","Kr",
        "Rb","Sr","Y","Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te","I","Xe","Cs","Ba","La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er",
        "Tm","Yb","Lu","Hf","Ta","W","Re","Os","Ir","Pt","Au","Hg","T","l","Pb","Bi","Po","At","Rn","Fr","Ra","Ac","Th","Pa","U","Np","Pu","Am","Cm","Bk","Cf","Es","Fm",
        "Md","No","Lr","Rf","Db","Sg","Bh","Hs","Mt","Ds","Rg"]

        positions = [(i,j) for i in range(9) for j in range(18)]
        for position, name in zip(positions, symbols):
            if name == '':
                continue
            
            
            button = QtWidgets.QPushButton(name,self)
            button.setMaximumWidth(35)
            button.setMaximumHeight(35)
            grid.addWidget(button, *position)     
            if len(options) and not name in options:
                button.setEnabled(False)
            else:

                button.clicked.connect(partial( self.button_clicked_callback, button))
        self.setLayout(grid)
       
    def button_clicked_callback(self,button):
        e = button.text()
        
        self.element_clicked_signal.emit(e)
    


############################################################
class PeriodicTableDialog(QtWidgets.QDialog):
    def __init__(self, options):
        super( ).__init__()
        self.options = options
        self._layout = QtWidgets.QVBoxLayout()  
        self.table_widget = PeriodicTable(options)
        self._layout.addWidget(self.table_widget)
        self.setLayout(self._layout)
        self.setWindowTitle('Choose an atom')
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint )
        self.ok = ''
        self.table_widget.element_clicked_signal.connect(self.button_press)
        
    @classmethod
    def showDialog(cls,options = []):
        dialog = cls( options)
        dialog.exec_()
        ok = copy.deepcopy(dialog.ok)
        dialog.deleteLater()
        return ok

 

   ############################################################
    def button_press(self, element):
        self.ok = element

        self.close()