from axd.models.aEDXD_functions import I_base_calc, I_inc_new
import numpy as np
import matplotlib
from axd.models.aEDXD_atomic_parameters import aEDXDAtomicParameters


sq_par_k = [[


]]
sq_par_fe= [[
            26.0,1.0,11.7695,4.7611,7.3573,0.3072,3.5222,15.3535,2.3045,76.8805,1.0369,0.62157,0.94225,9.8927
]]

sq_par_ca = [[20,1.0,8.6266,10.4421,7.3873,0.6599,1.5899,85.7484,1.0211,178.437,1.3751,0.50934,0.9172, 14.7943]]

qp = range(5000)


qp = np.asarray(qp)/50




mean_fqsquare,mean_fq,mean_I_inc = I_base_calc(qp,qp, sq_par_ca)



ca = [
        0.018,
        0.072,
        1.375,
        3.105,
        4.401,
        5.690,
        7.981,
        9.790,
        11.157,
        12.163,
        12.953,
        13.635,
        14.256,
        14.830,
        16.921,
        17.970,
        18.906,
        19.411,
        19.698,
        19.961
]

k = [
        0.016,
        0.062,
        1.105,
        2.500,
        3.905,
        5.301,
        7.652,
        9.405,
        10.650,
        11.568,
        12.329,
        13.014,
        13.645,
        14.220,
        16.212,
        17.152,
        18.020,
        18.494,
        18.752,
        18.970
]

fe  = [ 0.012,
        0.05,
        1.06,
        2.891,
        4.405,
        5.781,
        8.432,
        10.733,
        12.687,
        14.343,
        15.716,
        16.831,
        17.737,
        18.488,
        21.097,
        22.704,
        24.216,
        24.887,
        25.31,
        25.856]

fe_s = [0.005,
        0.01,
        0.05,
        0.1,
        0.15,
        0.2,
        0.3,
        0.4,
        0.5,
        0.6,
        0.7,
        0.8,
        0.9,
        1,
        1.5,
        2,
        3,
        4,
        5,
        8
        ]
fe_s = np.asarray(fe_s)
fe_q = fe_s * 4 * np.pi


ap = aEDXDAtomicParameters()
symbol = 'Ca'
opt = ap.get_ab5_options(symbol)[symbol]
print(opt)
i_inc = I_inc_new(qp/4/np.pi, opt)


import matplotlib.pyplot as plt
plt.plot(qp, mean_I_inc)
#plt.plot(qp, mean_fq)
plt.plot(qp, i_inc)
plt.plot(fe_q, ca,'ro')
#plt.plot(qp, mean_fqsquare)
plt.show()