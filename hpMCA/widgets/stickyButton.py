from PyQt5 import QtWidgets, QtCore

class StickyButton(QtWidgets.QPushButton):
    clicked_signal = QtCore.pyqtSignal()
    pressed_signal = QtCore.pyqtSignal()
    repeat_signal = QtCore.pyqtSignal()
    release_signal = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        QtWidgets.QPushButton.__init__(self, *args, **kwargs)
        self.setAutoRepeat(True)
        self.setAutoRepeatDelay(1000)
        self.setAutoRepeatInterval(1000)
        self.clicked.connect(self.handleClicked)
        self._state = 0

    def handleClicked(self):
        if self.isDown():
            if self._state == 0:
                self._state = 1
                self.setAutoRepeatInterval(100)
                self.pressed_signal.emit()
            else:
                self.repeat_signal.emit()
        elif self._state == 1:
            self._state = 0
            self.setAutoRepeatInterval(1000)
            self.release_signal.emit()
        else:
            self.clicked_signal.emit()

if __name__ == '__main__':

    import sys
    app = QtWidgets.QApplication(sys.argv)
    button = StickyButton('Test Button')
    button.show()
    sys.exit(app.exec_())