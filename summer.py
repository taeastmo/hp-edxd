from hpm.models.mcaModel import MCA
from os import listdir
from os.path import isfile, join
import numpy as np

from PyQt5 import QtWidgets
##  WARNING do not run this unless you are sure

files = ['/Users/hrubiak/Desktop/dt/GSD/sio2/20221204_Cd109Co57_3600sec_067.dat.mca',
'/Users/hrubiak/Desktop/dt/GSD/20221203_Cd109-Co57_5400sec_gain100kev_004.dat.mca'
]

file_out = '/Users/hrubiak/Desktop/dt/GSD/20221203_Cd109-Co57_5400sec_gain100kev_summed.hpmca'

def sum_files(files, file_out):



    mca = MCA()

    
    for i, file in enumerate(files):
        
        [file, ok] = mca.read_file(file)
        data = mca.get_data()
        if i == 0:
            summed_data = np.zeros(data.shape)
        summed_data = summed_data + data
        mca.data = summed_data

    mca.write_file(file_out)
   
app = QtWidgets.QApplication([])

sum_files(files, file_out)