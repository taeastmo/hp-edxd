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

import os.path, sys

from PyQt5.QtCore import QObject
import numpy as np
from functools import partial

from sxdm.widgets.sxdmWidget import sxdmWidget

from .. import style_path
from .. import home_path

############################################################

class sxdmController(QObject):
    def __init__(self, app=None):
        super().__init__()

        self.window = sxdmWidget()
        self.initData()
        
        self.make_connections()

    def initData(self):
        self.width = 21
        self.height = 21
        ## Create random image

        ## Set initial view bounds
        self.window.set_view_range(0, 0, self.width, self.height)
        data = np.random.normal(size=(30, self.width, self.height), loc=1024, scale=64).astype(np.uint16)
        
        self.window.setData(data)


    def make_connections(self):
        self.window.btn1.clicked.connect(self.btn1callback)
        self.window.btn2.clicked.connect(self.btn2callback)
        self.window.btn3.clicked.connect(self.btn3callback)

    def btn1callback(self):
        self.window.updateView(0)

    def btn2callback(self):
        self.window.updateView(1)

    def btn3callback(self):
        self.window.updateView(2)

    def showWindow(self):
        self.window.raise_widget()