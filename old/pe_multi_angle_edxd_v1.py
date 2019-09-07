from epics import caget, caput
import numpy as np
import time
import sys


def MOVE_TTH(mtth, mcurrent_tth, mcurrent_beamstop):
    if mtth < mcurrent_tth and mtth < 6.95 and mcurrent_beamstop == 0:
        caput('16BMA:Unidig2Bo0', 1)
        time.sleep(10)
        START_MOVE_TTH(mtth)

    if mtth > mcurrent_tth and mtth > 6.95 and mcurrent_beamstop ==1:
        START_MOVE_TTH(mtth)
        caput('16BMA:Unidig2Bo0', 0)
        time.sleep(10.0)

    if mtth == mcurrent_tth and mtth >= 6.95:
        caput('16BMA:Unidig2Bo0', 0)
        time.sleep(10.0)
    START_MOVE_TTH(mtth)


def START_MOVE_TTH(smtth):
    temp = caget('16BMA:m5.RBV')
    if smtth < temp:
        caput('16BMA:m5.VAL', smtth)
        while temp > smtth+0.005:
            temp = caget('16BMA:m5.RBV')
            time.sleep(1.0)
    if smtth > temp:
        caput('16BMA:m5.VAL', smtth)
        while temp < smtth-0.005:
            temp = caget('16BMA:m5.RBV')
            time.sleep(1.0)


def EDXD_COLLECTING(tth, pvsize, phsize, svsize, shsize, dvsize, dhsize, stime):
    current_tth = caget('16BMA:m5.RBV')
    current_beamstop=caget('16BMA:Unidig2Bo0')

    MOVE_TTH(tth, current_tth, current_beamstop)

    #set the slit and 2theta condition
    caput('16BMA:pm14.VAL', pvsize)
    caput('16BMA:pm16.VAL', phsize)
    caput('16BMA:pm18.VAL', svsize)
    caput('16BMA:pm20.VAL', shsize)
    caput('16BMA:m40.VAL', dvsize)
    caput('16BMA:m38.VAL', dhsize)    

    #start collecting data
    caput('16BMA:aim_adc1Erase', 1)
    time.sleep(0.2)
    caput('16BMA:aim_adc1Start', 1) 
    livetime = caget('16BMA:aim_adc1.ELTM')
    while livetime < stime-0.1:
        livetime = caget('16BMA:aim_adc1.ELTM')
        time.sleep(0.2)
    caput('16BMA:aim_adc1Stop', 1)
    time.sleep(0.2)
    
if __name__ == "__main__":
    rep = int(raw_input("rep:"))
    factor = float(raw_input("factor:"))
    exp_conditions= np.array([ (3.0, 0.3, 0.1, 0.33, 0.11, 2.0, 0.1, 900*factor),
                             (4.0, 0.3, 0.1, 0.33, 0.11, 2.0, 0.1, 900*factor),
                             (5.0, 0.3, 0.1, 0.33, 0.11, 2.2, 0.1, 1000*factor),
                             (7.0, 0.3, 0.1, 0.33, 0.11, 3.3, 0.1, 1000*factor),
                             (9.0, 0.42, 0.1, 0.45, 0.11, 3.5, 0.1, 1200*factor),
                             (12.0, 0.5, 0.15, 0.53, 0.16, 3.5, 0.1, 1200*factor),
                             (16.0, 0.5, 0.25, 0.53, 0.26, 3.5, 0.1, 1200*factor),
                             (21.0, 0.5, 0.3, 0.53, 0.31, 3.5, 0.1, 1500*factor),
                             (28.0, 0.5, 0.3, 0.53, 0.31, 3.5, 0.2, 1500*factor),
                             (35.0, 0.5, 0.3, 0.53, 0.31, 3.5, 0.2, 2000*factor)])
    print "exp_cond=", exp_conditions
    sz = exp_conditions.shape
    num_angles = sz[0]
    
    #Read current positions

    twotheta0 = caget('16BMA:m5.RBV')
    Primary_vsize0 = caget('16BMA:pm14.RBV')
    Primary_hsize0 = caget('16BMA:pm16.RBV')
    Secondary_vsize0 = caget('16BMA:pm18.RBV')
    Secondary_hsize0 = caget('16BMA:pm20.RBV')
    Detector_vsize0 = caget('16BMA:m40.RBV')
    Detector_hsize0 = caget('16BMA:m38.RBV')

    for n in range(0,rep):
        print "Iteration =", n+1
        for j in range(0,num_angles):
            EDXD_COLLECTING(exp_conditions[j,0],exp_conditions[j,1],exp_conditions[j,2],
                            exp_conditions[j,3],exp_conditions[j,4],exp_conditions[j,5],
                            exp_conditions[j,6],exp_conditions[j,7])
            time.sleep(1.0)
            now = time.localtime(time.time())
            t = time.strftime("%a_%d%b%y_%H_%M", now)
            try:
                print "2th =", exp_conditions[j,0], "EDXD_COLLECTING finished at", t
            except:
                print "End of data collection"
        time.sleep(10.0)

    caput('16BMA:m5.VAL', twotheta0)
    caput('16BMA:pm14.VAL',Primary_vsize0)
    caput('16BMA:pm16.VAL',Primary_hsize0)
    caput('16BMA:pm18.VAL', Secondary_vsize0)
    caput('16BMA:pm20.VAL', Secondary_hsize0)
    caput('16BMA:m40.VAL', Detector_vsize0)
    caput('16BMA:m38.VAL', Detector_hsize0)


