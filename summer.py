from hpm.models.mcaModel import MCA
from os import listdir
from os.path import isfile, join
import numpy as np

from PyQt5 import QtWidgets
##  WARNING do not run this unless you are sure

files = [
    '/Volumes/data/16bmb/PEC/Data/2023-1/HPCAT/Ross/20230414_detectors/GSD/20230417_Cd109-C057-W_7200sec_031.dat.mca',
    '/Volumes/data/16bmb/PEC/Data/2023-1/HPCAT/Ross/20230414_detectors/GSD/20230417_Cd109-C057-W_7200sec_032.dat.mca'    ,
    '/Volumes/data/16bmb/PEC/Data/2023-1/HPCAT/Ross/20230414_detectors/GSD/20230417_Cd109-C057-W_7200sec_033.dat.mca'
]

file_out = '/Users/hrubiak/Desktop/20230417_Cd109-C057-W_7200sec_031_033.dat.hpmca'

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