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
from PyQt5.QtCore import pyqtSignal

from  PyQt5.QtWidgets import QMainWindow, QApplication, QInputDialog, QWidget, QLabel
from hpmca.widgets.CustomWidgets import FlatButton, DoubleSpinBoxAlignRight, VerticalSpacerItem, NoRectDelegate, \
    HorizontalSpacerItem, ListTableWidget, VerticalLine, DoubleMultiplySpinBoxAlignRight, HorizontalLine
from hpmca.widgets.PltWidget import plotWindow
from functools import partial
import copy

class aEDXDFilesWidget(QWidget):
    color_btn_clicked = pyqtSignal(int, QtWidgets.QWidget)
    x_btn_clicked = pyqtSignal(int, QtWidgets.QWidget)
    cb_state_changed_signal = pyqtSignal(list, list, bool)
    file_dragged_in = pyqtSignal(list)
    widget_closed = pyqtSignal()
    top_level_selection_changed_signal = pyqtSignal(int,float)
    file_selection_changed_signal = pyqtSignal(list, list)
    delete_clicked_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setupUi()
   
    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.raise_()    
    
    def setupUi(self):
        self._layout = QtWidgets.QVBoxLayout()
        self.setWindowTitle('Files control')
        self.button_widget = QtWidgets.QWidget(self)
        self.button_widget.setObjectName('files_control_button_widget')
        self._button_layout = QtWidgets.QHBoxLayout()
        self._button_layout.setContentsMargins(0, 0, 0, 0)
        self._button_layout.setSpacing(15)
        self.add_tth_btn = FlatButton('Add '+f'2\N{GREEK SMALL LETTER THETA}')
        self._button_layout.addWidget(self.add_tth_btn,0)
        self.add_btn = FlatButton('Add files')
        self._button_layout.addWidget(self.add_btn,0)
        self.del_btn = FlatButton('Delete')
        self._button_layout.addWidget(self.del_btn,0)
        self.clear_btn = FlatButton('Clear')
        self._button_layout.addWidget(self.clear_btn,0)
        #self.from_config_btn = QtWidgets.QPushButton('From config.')
        #self._button_layout.addWidget(self.from_config_btn,0)
        #self._button_layout.addWidget(VerticalLine())
        self._button_layout.addSpacerItem(HorizontalSpacerItem())
        #self._button_layout.addWidget(VerticalLine())
        self.button_widget.setLayout(self._button_layout)
        self._body_layout = QtWidgets.QHBoxLayout()
        self.file_tw = ListTableWidget(columns=4)
        header_view = QtWidgets.QHeaderView(QtCore.Qt.Horizontal, self.file_tw)
        self.file_tw.setHorizontalHeader(header_view)
        header_view.setResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header_view.setResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header_view.setResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header_view.setResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.file_trw = QtWidgets.QTreeWidget()
        self.file_trw.setHeaderLabels([' ' + 'Spectra',' ' + f'2\N{GREEK SMALL LETTER THETA}'])
        #self.file_trw.setAlternatingRowColors(True)
        #self.file_trw.setItemDelegate(NoRectDelegate())
        self.file_trw.currentItemChanged.connect(self.file_selection_changed)
        header = self.file_trw.header()
        header.setResizeMode(QtWidgets.QHeaderView.Fixed)
        self._body_layout.addWidget(self.file_trw )
        self.setAcceptDrops(True) 
        self._layout.addWidget(self.button_widget)
        self._layout.addLayout(self._body_layout)

        
        self.button_2_widget = QtWidgets.QWidget(self)
        self.button_2_widget.setObjectName('files_control_button_2_widget')
        self._button_2_layout = QtWidgets.QHBoxLayout()
        self._button_2_layout.setContentsMargins(0, 0, 0, 0)
        self._button_2_layout.setSpacing(6)
        self.apply_btn = FlatButton('Apply')
        self._button_2_layout.addWidget(self.apply_btn,0)
        #self._button_2_layout.addWidget(VerticalLine())
        self._button_2_layout.addSpacerItem(HorizontalSpacerItem())
        #self._button_2_layout.addWidget(VerticalLine())
        self.button_2_widget.setLayout(self._button_2_layout)
        self._layout.addWidget(HorizontalLine())
        self._layout.addWidget(self.button_2_widget)
        

        self.clear_arrays()

        self.setLayout(self._layout)
        self.retranslateUi(self)
        self.style_widgets()

        self.del_btn.clicked.connect(self.delete_clicked)

    def clear_arrays(self):
        self.top_level_color_btns = []
        self.top_level_items = []
        self.file_items = []
        self.file_show_cbs = []
        self.tth_items = []
        self.files = {}

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, QtWidgets.QTreeWidgetItem)
    def file_selection_changed(self, current, previous):
        if len(self.top_level_items):
            ind,files = self.identify_item(current)

            if len(ind)==1:
                self.top_level_selection_changed_signal.emit(ind[0],files[0])
            if len(ind)==2:
                self.file_selection_changed_signal.emit(ind,files)

    def delete_clicked(self):
        trw = self.file_trw
        if len(self.top_level_items):
            si=trw.selectedItems()
            if len(si):
                item = si[0]
                ind, files = self.identify_item(item)
                self.delete_clicked_signal.emit({'ind':ind, 'files':files, 'item':item})

    def get_selected_tth(self):
        trw = self.file_trw
        if len(self.top_level_items):
            si=trw.selectedItems()
            if len(si):
                item = si[0]
                ind, files = self.identify_item(item)
                tth = files[0]
                return tth
            else :
                return None
        else :
            return None



    def file_cb_changed(self, checkbox):
        i = self.file_show_cbs.index(checkbox)
        file_item=self.file_items[i]
        ind, files = self.identify_item(file_item)
        self.cb_state_changed_signal.emit(ind, files, checkbox.isChecked())


    def identify_item(self,item):
        ind=[0]
        if item in self.top_level_items:
            p_ind = self.top_level_items.index(item)
            ind = [p_ind]
        if item in self.file_items:
            p = item.parent()
            c_ind = p.indexOfChild(item)
            p_ind = self.top_level_items.index(p)
            ind = [p_ind,c_ind]
        tth = float(self.tth_items[ind[0]].text()) 
        files = [tth]
        if len(ind)==2:
            filename = self.files[str(tth)][ind[1]]
            files.append(filename)
        return ind, files

    def remove_trw_item(self, item):
        trw = self.file_trw
        root = trw.invisibleRootItem()
        (item.parent() or root).removeChild(item)


    def clear_trw(self):
        self.file_trw.blockSignals(True)
        root = self.file_trw.invisibleRootItem()
        for item in self.top_level_items:
            (item.parent() or root).removeChild(item)
        self.file_trw.blockSignals(False)
        self.clear_arrays()

    def del_file(self, file_item ):
        self.file_trw.blockSignals(True)
        ind, files = self.identify_item(file_item)
        tth = files[0]
        filename = files[1]
        i = self.file_items.index(file_item)
        del self.file_items[i]
        del self.file_show_cbs[i]
        for t in self.files:
            if str(tth) == t:
                for i, f in enumerate(self.files[t]):
                    if filename == f:
                        del self.files[t][i]
        file_item.parent() .removeChild(file_item)
        self.file_trw.blockSignals(False)
        
        
                
    def del_group(self, top_item ):
        #self.file_trw.blockSignals(True)
        ind, files = self.identify_item(top_item)
        tth = files[0]
        i = self.top_level_items.index(top_item)
        root = self.file_trw.invisibleRootItem()
        for item in self.top_level_items:
            if top_item==item:
                del self.top_level_color_btns[i]
                del self.top_level_items[i]
                del self.tth_items[i]
                if str(tth) in self.files:
                    del self.files[str(tth)]
                (item.parent() or root).removeChild(item)
                break
        #self.file_trw.blockSignals(False)
        
    # ###############################################################################################
    # Now comes all the file tw stuff
    ################################################################################################

    def add_file_group(self, filenames, color, tth,use):
        self.file_trw.blockSignals(True)
        current_rows = self.file_trw.currentIndex()
        h = QtWidgets.QTreeWidgetItem()
        h.setExpanded(True)
        self.top_level_items.append(h)
        self.file_trw.addTopLevelItem(h)
        color_button = FlatButton()
        color_button.setStyleSheet("background-color: " + color)
        color_button.setMaximumHeight(20)
        color_button.clicked.connect(partial(self.file_color_btn_click, color_button))
        self.top_level_color_btns.append(color_button)
        self.file_trw.setItemWidget(h,0,color_button)
        tth_item = QtWidgets.QLabel('   ' + tth)
        tth_item.setStyleSheet("background-color: transparent")
        self.file_trw.setItemWidget(h,1,tth_item)
        self.tth_items.append(tth_item)
        for i, filename in enumerate(filenames):
            file_use = use[i]
            self.add_file(filename,file_use,tth)
        self.file_trw.setColumnWidth(0, 60)
        self.select_file(current_rows)
        self.file_trw.blockSignals(False)

    def add_file(self, filename,file_use,tth):
        tths = []
        for tth_i in self.tth_items:
            tths.append(float(tth_i.text()))
        ind = tths.index(float(tth))
        top_level_item = self.top_level_items[ind]
        file_item = QtWidgets.QTreeWidgetItem(top_level_item)
        self.file_items.append(file_item)
        show_cb = QtWidgets.QCheckBox()
        show_cb.setChecked(file_use)
        show_cb.stateChanged.connect(partial(self.file_cb_changed, show_cb))
        show_cb.setStyleSheet("background-color: transparent")
        self.file_trw.setItemWidget(file_item, 0, show_cb)
        self.file_show_cbs.append(show_cb)
        file_label = QLabel('   ' + filename)
        file_label.setStyleSheet("background-color: transparent")
        self.file_trw.setItemWidget(file_item,1,file_label)
        if tth in self.files:
            self.files[tth].append(filename)
        else:
            self.files[tth]=[filename]

    def style_widgets(self):
        self.file_trw.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.file_trw.setMinimumWidth(380)
        
        self.file_trw.setMinimumHeight(120)
        self.setStyleSheet("""
            
            #files_control_button_widget FlatButton {
                min-width: 70;
                max-width: 70;
            }
            #files_control_button_2_widget FlatButton {
                min-width: 70;
                max-width: 70;
            }
        """)

    def select_file(self, ind):
        self.file_trw.setCurrentIndex(ind)

    def get_selected_file_row(self):
        selected = self.file_tw.selectionModel().selectedRows()
        try:
            row = selected[0].row()
        except IndexError:
            row = -1
        return row

    
    def rename_file(self, ind, name):
        name_item = self.file_tw.item(ind, 2)
        name_item.setText(name)
    
    def set_file_tth(self, ind, P):
        tth_item = self.file_tw.item(ind, 3)
        try:
            tth_item.setText("{0:.2f} GPa".format(P))
        except ValueError:
            tth_item.setText("{0} GPa".format(P))

    def get_file_tth(self, ind):
        tth_item = self.file_tw.item(ind, 3)
        tth = float(str(tth_item.text()).split()[0])
        return tth

    def change_tth_color(self, ind, color):
        self.top_level_color_btns[ind].setStyleSheet('background-color:' + color.name())
    
    def file_color_btn_click(self, button):
        self.color_btn_clicked.emit(self.top_level_color_btns.index(button), button)
        
    
    def file_show_cb_set_checked(self, ind, state):
        checkbox = self.file_show_cbs[ind]
        checkbox.setChecked(state)

    def file_show_cb_is_checked(self, ind):
        checkbox = self.file_show_cbs[ind]
        return checkbox.isChecked()

    def retranslateUi(self, aEDXDWidget):
        pass

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    aEDXDWidget = aEDXDFilesWidget()
    aEDXDWidget.show()
    app.exec_()