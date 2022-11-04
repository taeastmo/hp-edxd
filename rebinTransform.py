from itertools import count
import numpy as np

import time
CAL_OFFSET = 0.401
CAL_SLOPE = .95

x_size = 20

X = np.asarray(range(x_size))
Y = np.sin(X/2)

xp = X * 1 + CAL_OFFSET

xp_mp5 = xp - 0.00001
xp_pp5 = xp + 1

delta_r = CAL_SLOPE

now = time.time()
upper_bin_index = np.floor(xp_pp5/delta_r)
lower_bin_index = np.floor(xp_mp5/delta_r)
upper_bin_area =  (xp_pp5- (np.floor(xp_pp5/delta_r)*delta_r)) 
lower_bin_area =  (np.ceil(xp_mp5/delta_r)*delta_r - xp_mp5) 
sum_outer_bin_areas = upper_bin_area + lower_bin_area

split_pixel = ((upper_bin_index - lower_bin_index) >= 1) * 1
inner_bins = ((upper_bin_index - lower_bin_index) > 1) * 1
number_of_inner_bins = abs((upper_bin_index - lower_bin_index) - 1)
inner_bins_areas = (1 - sum_outer_bin_areas) / number_of_inner_bins

inner_bins_areas = inner_bins_areas * inner_bins
inner_bins_areas[np.isnan(inner_bins_areas)] = 0

#print ('upper_bin_index ' + str(upper_bin_index))
#print ('lower_bin_index ' + str(lower_bin_index))
#print ('upper_bin_area ' + str(upper_bin_area))
#print ('lower_bin_area ' + str(lower_bin_area))
#print ('sum_outer_bin_areas ' + str(sum_outer_bin_areas))
#print ('split_pixel ' + str(split_pixel))
#print ('inner_bins ' + str(inner_bins))
#print ('number_of_inner_bins ' + str(number_of_inner_bins))
#print ('inner_bins_areas ' + str(inner_bins_areas))



output_bins_use = []
output_bins_area = []

nbin = 1
ib = nbin == number_of_inner_bins
low_up_diff = lower_bin_index + nbin  != upper_bin_index
coerse = lower_bin_index + nbin 

inner_bin_index = coerse #* low_up_diff
inner_bin_areas = inner_bins_areas#* low_up_diff

after = time.time()
diff = after - now
print(diff)

#print(indices)
#print(counts)

R = range (int(x_size / CAL_SLOPE))
R_vals = np.zeros(len(R))
now = time.time()
for r in R:
    ind = np.round(lower_bin_index) == r
    vals = Y[ind]*lower_bin_area[ind]
    val = np.sum(vals)
    R_vals[r] = R_vals[r]+val

for r in R:
    ind = np.round(inner_bin_index) == r
    vals = Y[ind]*inner_bin_areas[ind]
    val = np.sum(vals)
    R_vals[r] = R_vals[r]+ val

for r in R:
    ind = np.round(upper_bin_index) == r
    vals = Y[ind]*upper_bin_area[ind]
    val = np.sum(vals)
    R_vals[r] = R_vals[r]+val

R = np.asarray(R) * CAL_SLOPE - CAL_OFFSET
R_vals = R_vals / CAL_SLOPE

after = time.time()
diff = after - now
print(diff)

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg

#QtGui.QApplication.setGraphicsSystem('raster')
app = QtGui.QApplication([])
#mw = QtGui.QMainWindow()
#mw.resize(800,800)

win = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")
win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: Plotting')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

p4 = win.addPlot(title="Parametric, grid enabled")
x = X
y = Y
p4.plot(x, y)
p4.showGrid(x=True, y=True)


p4.plot(R, R_vals, pen=(200,200,200), symbolBrush=(255,0,0), symbolPen='w')

p4.plot(inner_bins_areas, pen=(200,200,200), symbolBrush=(0,200,0), symbolPen='w')


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
