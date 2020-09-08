from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
import copy 

from functools import partial


def spectra_baseline(sig, Wn, iterations, method = 'pad'):
    sig_work = copy.copy(sig)
    if method == 'pad':
        pad = len(sig_work)-1
        filt_func = partial(filt_pad, pad)
    else:
        filt_func = filt_gust
 
    b, a = signal.butter(1, Wn)
    for i in range(int(round(iterations))-1):
        
        f = filt_func(b, a, sig_work)
        less = f <= sig_work
        sig_work[less] = f[less]
    
    f = filt_func(b, a, sig_work)
    return f

def filt_pad(padlen, b, a, sig_work ):
    return (signal.filtfilt(b, a, sig_work, padlen=padlen))
    
def filt_gust(b, a, sig_work):
    return (signal.filtfilt(b, a, sig_work, method='gust'))
    
