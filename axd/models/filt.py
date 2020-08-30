from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
import copy 




def spectra_baseline(sig, Wn, iterations):
    sig_work = copy.copy(sig)
    b, a = signal.butter(2, Wn)
    for i in range(iterations-1):
        fgust = signal.filtfilt(b, a, sig_work,  method="gust")
        less = fgust <= sig_work
        sig_work[less] = fgust[less]
    fgust = signal.filtfilt(b, a, sig_work,  method="gust")
    return fgust

n = 600
np.random.seed(123456)
sig = np.random.randn(n)**3 + 3*np.random.randn(n).cumsum()

plt.plot(sig, 'k-', label='input')
it = 50
Wn = 0.1

fgust = spectra_baseline(sig,Wn,it)

sig = sig - fgust

plt.plot(sig, 'g-', label='input')

plt.plot(fgust, 'r-', linewidth=1.0, label='gust')

plt.show()