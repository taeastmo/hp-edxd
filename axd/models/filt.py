from scipy import signal
import matplotlib.pyplot as plt
import numpy as np

'''
First we create a one second signal that is the sum
of two pure sine waves, with frequencies 5 Hz and 
250 Hz, sampled at 2000 Hz.
'''

t = np.linspace(0, 1.0, 2001)
xlow = np.sin(2 * np.pi * 5 * t)
xhigh = np.sin(2 * np.pi * 250 * t)
x = xlow + xhigh

'''
Now create a lowpass Butterworth filter with a cutoff 
of 0.125 times the Nyquist frequency, or 125 Hz, and 
apply it to x with filtfilt. The result should be 
approximately xlow, with no phase shift.
'''

b, a = signal.butter(8, 0.125
print(b)
print(a)
y = signal.filtfilt(b, a, x, padlen=150)
np.abs(y - xlow).max()

'''
We get a fairly clean result for this artificial example 
because the odd extension is exact, and with the moderately 
long padding, the filter’s transients have dissipated by 
the time the actual data is reached. In general, transient 
effects at the edges are unavoidable.

The following example demonstrates the option method="gust".
First, create a filter.
'''

#b, a = signal.ellip(4, 0.01, 120, 0.125)  # Filter to be applied.
np.random.seed(123456)

'''
sig is a random input signal to be filtered.
'''

n = 60
sig = np.random.randn(n)**3 + 3*np.random.randn(n).cumsum()

'''
Apply filtfilt to sig, once using the Gustafsson method, 
and once using padding, and plot the results for comparison.
'''

fgust = signal.filtfilt(b, a, sig, method="gust")
fpad = signal.filtfilt(b, a, sig, padlen=50)
plt.plot(sig, 'k-', label='input')
plt.plot(fgust, 'b-', linewidth=4, label='gust')
plt.plot(fpad, 'c-', linewidth=1.5, label='pad')
plt.legend(loc='best')
plt.show()