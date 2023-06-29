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

"""aEDXD_functions.py:
   Python functions for aEDXD_class.py"""
__author__    = "Changyong Park (cpark@carnegiescience.edu)"
__version__   = "1.3"
__date__      = "04 August 2015"
__copyright__ = "Copyright (c) 2015 Changyong Park"
__license__   = "LICENSE-CIW(Free)"

import numpy as np
from scipy import interpolate
from scipy.special import erfc
from scipy.optimize import curve_fit
import scipy.signal as signal
from scipy.io import loadmat
from scipy import integrate
from scipy.optimize import fsolve
from tkinter import W
from scipy.signal import firwin, filtfilt, lfilter
from scipy.fft import fft
from scipy.fftpack import fftfreq
import matplotlib.pyplot as plt
import scipy.special
import matplotlib.pyplot as plt
import random
import json


def fversion():
    return __version__

def onpick(event):
    thisline = event.artist
    xdata = thisline.get_xdata()
    ydata = thisline.get_ydata()
    ind = event.ind
    print('onpick points:'+zip(xdata[ind], ydata[ind]))

def spline_fit(x,y,w,bbox,k,s):
    spl = interpolate.UnivariateSpline(x,y,w,bbox,k,s)
    return spl

def polynomial_fit(x,y,deg):
    pln = np.polyfit(x,y,deg,rcond=None,full=False)
    return pln
    
def fastbin(data,bin_size):
    bin_means = []
    data = np.array(data)
    nbins = int(len(data)/bin_size)
    for i in range(nbins-1):
        if bin_size*(i+1) <= (len(data)-1):
            bin_means.append(data[bin_size*i:(bin_size*(i+1))].mean())
        else:
            bin_means.append(data[bin_size*i:(len(data)-1)].mean())
    return np.array(bin_means) 

def custom_fit(func,x,y,p0,yb):
    p_opt,p_cov = curve_fit(func, x, y, p0, sigma=yb)
    # calculate stdev and correlatoin matrix of estimated parameters
    p_stdev = np.sqrt(np.diag(p_cov))
    d = np.sqrt(np.abs(np.diag(p_cov)))
    d = np.matrix(d)        
    p_corp = p_cov/(d.T*d)
    yp = func(x, *p_opt)
    if yb is None :
        schi2 = np.sum((y-yp)**2)/(len(y)-len(p_opt))
    else:
        schi2 = np.sum(((y-yp)/yb)**2)/(len(y)-len(p_opt))
    r = np.corrcoef(y,yp)
    '''
    print("\nSciPy.optimize.curve_fit:"+
      "\np_opt  : \n" + str(p_opt)+
      "\np_stdev: \n" + str(p_stdev)+
      "\np_corp : \n" + str(p_corp) +
      "\nscaled chi^2 = " + str(schi2) +
      "\nr = " + str(r[0][1]))
    '''
    return p_opt,p_stdev,p_cov,p_corp,schi2,r[0][1]

def stepped_polynomial(x,*p0):
    s = p0[0]; w = p0[1]; x0 = p0[2]; pln = p0[3:]
    poly_y = []
    deg = len(pln)-1
    for i in range(len(x)):
        poly_y.append(sum(pln[deg-j]*x[i]**j for j in range(deg+1)))
    poly_y = np.array(poly_y)
    y = (1+s*erfc(1/w*(x-x0)))*poly_y
    return y

def simple_polynomial(x,*p0):
    pln = p0[0:]
    poly_y = []
    deg = len(pln)-1
    for i in range(len(x)):
        poly_y.append(sum(pln[deg-j]*x[i]**j for j in range(deg+1)))
    y = np.array(poly_y)
    return y

def I_base_calc(q,q_comp,p):
    """*par must have the following structure:
    [ Z, Atomic fraction, a1,b1,a2,b2,a3,b3,a4,b4,c, M,K,L ]
    """

    

    s = np.array(q/4/np.pi)
    s_comp = np.array(q_comp/4/np.pi)
    mean_fqsquare = np.zeros(len(q))
    mean_fq = np.zeros(len(q))
    mean_I_inc = np.zeros(len(q))
    for i in range(len(p)):

        abc = p[i][2:11]
        
        fqi = p[i][2]*np.exp(-p[i][3]*s**2)+\
              p[i][4]*np.exp(-p[i][5]*s**2)+\
              p[i][6]*np.exp(-p[i][7]*s**2)+\
              p[i][8]*np.exp(-p[i][9]*s**2)+p[i][10]
        mean_fqsquare += p[i][1]*fqi**2 # fractionized
        mean_fq += p[i][1]*fqi
        # Compton I_inc(Q')
        fqi_comp = p[i][2]*np.exp(-p[i][3]*s_comp**2)+\
              p[i][4]*np.exp(-p[i][5]*s_comp**2)+\
              p[i][6]*np.exp(-p[i][7]*s_comp**2)+\
              p[i][8]*np.exp(-p[i][9]*s_comp**2)+p[i][10]

        Z = p[i][0]
        I_inci = np.zeros(len(q))
        if len(p[i])> 16:
            # ab5 contains parameters for calculating incoherent scattering in different form than legacy MKL table
            # from Ref: H.H.M. Balyuzi, Acta Cryst. (175). A31, 600
            ab5 = [Z, *p[i][14:24]]
            I_inci = I_inc_new(s_comp, ab5)
        else:
            # 2020-09-05 added parenthesis around "p[i][0]-np.array(fqi_comp)**2/p[i][0]"
            # since they were missing in previous versions
            # Ref. F. Hajdu, Acta Cryst. (1971). A27, 73
            mkl = p[i][11:14]
            if not mkl[0] is None and not mkl[1] is None and not mkl[2] is None:
                I_inci = (Z-np.array(fqi_comp)**2/Z)*\
                        (1-p[i][11]*(np.exp(-p[i][12]*s_comp)-np.exp(-p[i][13]*s_comp)))
                
        mean_I_inc += p[i][1]*I_inci
    return mean_fqsquare, mean_fq, mean_I_inc

def I_inc_new(s, param):
    """
    s = lambda^-1 * sin(theta)
    param must have the following structure:
    [ Z, A1,	B1,	A2,	B2,	A3,	B3,	A4,	B4,	A5,	B5]
    Ref: H.H.M. Balyuzi, Acta Cryst. (175). A31, 600
    """
    Z = param[0]
    
    ab = param[1:]
    #s = np.array(q /4/np.pi)
    mean_I_inc = Z - (ab[0]*np.exp(-ab[1]*s**2)+\
                     ab[2]*np.exp(-ab[3]*s**2)+\
                     ab[4]*np.exp(-ab[5]*s**2)+\
                     ab[6]*np.exp(-ab[7]*s**2)+\
                     ab[8]*np.exp(-ab[9]*s**2))

    return mean_I_inc

    
def find_Iq_scale(Iq,sq_base):
    return np.linalg.solve(Iq,sq_base)

# to resolve py2exe error, from http://www.pyinstaller.org/ticket/596
def dependencies_for_myprogram():
    from scipy.sparse.csgraph import _validation



def is_e(val):
    
    s=str(val-int(val))
    if 'e-' in s:

        return True
    return False
  

####################### Tyler's GOF script (work in progress) ###########################3
def GOF_test(q,Sq,e):

    q = np.transpose(q)
    Sq = np.transpose(Sq)
    e = np.transpose(e)

    ########## CREATE ROIS AND CALCULATE AVERAGE SPACING BETWEEN Q-VALUES IN EACH ROI#############
    ### A few things to check:
    ### 1) Check for Sq_roi_all arrays that have null values as the last few elements and exclude them from the GOF calculation
    ### 2) Call the function in the aedxd_components.py script and get it to display on the structure factor page
    ### 3) Play around with the normalization of the global chi^2 value - for now it is normalized by the total number of data points 

    ## Split the complete S(q) into discrete regions of overlapped (call them ROIs)
    ## A new ROI begins each time a new fragment is introduced or ends
    # Find points of overlap and store those boundaries as ROI edges 
    roi = []
    for i in range(len(q[0,:])):
        roi.append(q[0,i]) 
        roi.append(q[-1,i])
    roi = np.sort(roi) # sort the values in ascending order  
    # remove first and last regions as there is no overlap there
    roi = roi[1:-1]
    # print("Number of unique overlapping regions = " + str(len(roi)))

    # Find average dq for each SF fragment (for determining bin widths) 
    dq_avg_roi = []
    for i in range(len(roi) - 1): # loops over each ROI region
        nfrags = 0 # counter to keep track of the number of S(q) fragments in a single ROI
        dq = 0
        dq_total = 0 # used to calculate the average dq spacing of a single ROI
        dq_avg = 0
        for j in range(len(q[0,:])): # loops over S(q) fragments
            roi_data_q = [] # if the S(q) fragment has data within the current ROI, those points will be stored here
            nfrags_true = False # Used as a trigger later on
            for k in range(len(q[:,j])): # loops over q in each S(q) fragment
                if q[k,j] > roi[i] and q[k,j] < roi[i + 1]: # is q value within ROI bounds?
                    roi_data_q.append(q[k,j])
                    nfrags_true = True # indicates that some portion of the current S(q) is contained in the ROI
            if nfrags_true == True:
                nfrags = nfrags + 1 
                dq = np.mean(np.diff(roi_data_q))
                dq_total = dq_total + dq
                dq_avg = dq_total/nfrags # average q-spacing of the ROI 
        dq_avg_roi.append(dq_avg)

    dq_avg_roi = np.array(dq_avg_roi)
    ## check for ROIs that have too few points and throw them out. The dq spacings for these ROIs either contain NaN or zeros
    roi_idx_del = np.nonzero(np.isnan(dq_avg_roi))
    dq_avg_roi = np.delete(dq_avg_roi,roi_idx_del[0])
    roi = np.delete(roi,roi_idx_del[0])
    roi_idx_del = np.where(dq_avg_roi == 0)
    dq_avg_roi = np.delete(dq_avg_roi,roi_idx_del)
    roi = np.delete(roi,roi_idx_del) 

    # plot the SF fragments (for debugging)
    # for i in range(len(q[0,:])):
    #     plt.scatter(q[0:len(q),i],Sq[0:len(Sq),i],s=4)
    # # plt.scatter(q[:,1],Sq[:,1])
    # for i in range(len(roi)):
    #     plt.axvline(x=roi[i],color="grey",ls = ":")
    # plt.show()

    ############# BIN THE DATA AND CALCULATE A CHI^2 VALUE #############
    CHISQ = np.zeros((len(roi)-1,1)) # stores chi^2 values for each ROI
    for i in range(len(roi)-1): # loop over each ROI
        Sq_all_roi = []; e_all_roi = []; q_all_roi = [] # arrays containing S(q) and error values for all S(q) fragments in a given ROI
        chisq_roi = [] # stores summed chi^2 values between S(q) fragments in a given ROI
        # create bins
        nbins = int(np.round((roi[i+1]-roi[i])/(1.5*dq_avg_roi[i]))) # calculates number of bins in the current ROI based on a width of 1.5x the avg q spacing
        edges = np.linspace(roi[i],roi[i+1],num = nbins + 1) # the number of edges for the binning is always nbins + 1 
        for j in range(len(q[0,:])): # loops over S(q) fragments
            Sq_bin_avg = np.zeros(len(edges)-1); e_bin_avg = np.zeros(len(edges)-1); q_bin_avg = np.zeros(len(edges)-1);  
            roi_data_q = []; roi_data_Sq = []; roi_data_e = [] # stores q, S(q), and error for values of a fragmented S(q) that lie in the ROI
            n_frags_true = False # Used as a trigger later on
            counter = 0 # used to track number of q values from each S(q) within the ROI
            for k in range(len(q[:,j])): # loops over q values in each S(q) fragment
                if q[k,j] > roi[i] and q[k,j] < roi[i+1]: # is q within the ROI bounds?
                    roi_data_q.append(q[k,j])      #
                    roi_data_Sq.append(Sq[k,j])    # collecting the data points within in the ROI
                    roi_data_e.append(e[k,j])      #
                    counter = counter + 1          # used to check if there are more than 2 data points in the ROI (filters out rogue data points on the edges of the ROIs)
            if counter > 2:
                n_frags_true = True
            else:
                n_frags_true = False # if there are only 2 or less q-values in the ROI, don't use its associated S(q) fragment for the chi^2 calculation
            # bin the y values and the error
            bin_id = np.digitize(roi_data_q,edges) # get bin index for each q in the ROI
            n_in_bin = np.bincount(bin_id) # num of data points in each bin per S(q) fragment
            if n_frags_true == True:
                for m in range(len(roi_data_q)):
                    Sq_bin_avg[bin_id[m]-1] += roi_data_Sq[m]/n_in_bin[bin_id[m]] # calculates the cumulative average S(q) value in each bin
                    e_bin_avg[bin_id[m]-1] += roi_data_e[m]/n_in_bin[bin_id[m]] # calculates the cumulative average S(q) error value in each bin
                    q_bin_avg[bin_id[m]-1] += roi_data_q[m]/n_in_bin[bin_id[m]] # calculates the cumulative average q value in each bin
                Sq_all_roi.append(Sq_bin_avg)
                e_all_roi.append(e_bin_avg)
                q_all_roi.append(q_bin_avg)

        # Check for zeros in Sq_all_roi - do not use these elements for the chi^2 calculation - COME BACK TO THIS LATER
        # indx_zero = [] # will be used to store indexes of null values 
        # Sq_all_roi = np.array(Sq_all_roi)
        # for p in range(len(Sq_all_roi)):
        #     indx_zero.append(np.where(Sq_all_roi[p,:] == 0))    

        # Calculation of chi^2 terms between the uth and wth S(q) fragment
        for u in range(len(Sq_all_roi)): 
            for w in range((u + 1),(len(Sq_all_roi)),1):
                # chisq_roi.append(np.sum(((Sq_all_roi[:][u] - Sq_all_roi[:][w])**2) / ((e_all_roi[:][u] + e_all_roi[:][w])/2)))
                chisq_roi.append(np.sum(((Sq_all_roi[:][u] - Sq_all_roi[:][w])**2) / ((q_all_roi[:][u] + q_all_roi[:][w])/2)))
        CHISQ[i] = np.sum(chisq_roi)

    # CHISQ_TOT = np.sum(CHISQ)/np.size(q) # total chisq normalized by the number of data points
    CHISQ_TOT = np.sum(CHISQ)
    return CHISQ_TOT


######### This function randomly varies the polynomial coefficients of the white beam estimation ########
#### For now, only 3rd order polynomials are possible
def rand_param(max_int,p_deg,p_init): # inputs are the maximum intensity of the highest 2theta spectrum, and the polynomial order and coefficients of the initial guess
    
    # # Calculate the bounds on the random changes to the polynomial coefficients
    # # The values are calculated according to a calibration based on the intensity of the highest 2theta spectrum
    # p_change_ratio = np.array([(1e-5*max_int - 0.0066)/100, (-1e-7*max_int + 0.0097)/100, \
    #     (-7e-6*max_int + 0.5246)/100, (7e-7*max_int + 0.0395)/100])
    # p_change_bnd = np.abs(np.multiply(p_init,p_change_ratio))
    # # Randomly change the polynomial coefficients within calibrated limits
    # p_change = np.array([p_change_bnd[0]/100*random.randrange(-100,100,1), p_change_bnd[1]/100*random.randrange(-100,100,1), \
    #     p_change_bnd[2]/100*random.randrange(-100,100,1), p_change_bnd[3]/10*random.randrange(-10,10,1)])

    #  Calculate the bounds on the random changes to the polynomial coefficients
    # The values are calculated according to a calibration based on molten Fe
    p_change_ratio = np.array([(-4.48E-04)/100, (9.68E-3)/100, \
        (5.23E-1)/100, (3.96E-2)/100])
    p_change_bnd = np.abs(np.multiply(p_init,p_change_ratio))
    # Randomly change the polynomial coefficients within calibrated limits
    p_change = np.array([p_change_bnd[0]/100*random.randrange(-100,100,1), p_change_bnd[1]/100*random.randrange(-100,100,1), \
        p_change_bnd[2]/100*random.randrange(-100,100,1), p_change_bnd[3]/10*random.randrange(-10,10,1)])

    p_new = p_init + p_change
    return p_new # returns the randomly-varied polynomial coefficients

######### Lowpass filter for removing termination ripples ##########
def lowpass(q,r,G,numtaps,cutoff,width):
    # filter parameters
    rmax = max(r) # sampling period (instead of time, this is in r-spacing)
    fs = len(G)/rmax # sampling frequency (samples/Å)
    nyq = fs/2 # nyquist frequency
    # numtaps = 401 # number of coefficients (filter order + 1)
    period = 2*np.pi/(q[-1] - q[0]) # theoretical period of the termination ripples
    # cutoff =  0.85*(1/period) # needs to be slightly less than 1/period
    # width =  1 # width of the transition region 

    # obtain filter coefficients
    coeff = firwin(numtaps,cutoff,width, fs = fs) # firwin is an FIR (finite impulse response) filter
    
    # COMMENT TO ROSS: if desired, we can allow users to plot the filter response 
    # plot the filter response
    w, h = signal.freqz(coeff)
    plt.figure(0)
    plt.plot(w*fs/(2*np.pi),20 * np.log10(abs(h)),'k')
    plt.axvline(cutoff,color = 'green',label = 'Cutoff freq.')
    plt.axvline(1/period,color = 'blue',label = "Theoretical ripple freq.")
    plt.xlabel('Frequency (cycles/Å)')
    plt.ylabel('Amplitude (dB)')
    plt.legend(loc = 'best')
    plt.show()

    # filter and return the PDF
    Gfilt = filtfilt(coeff,1,G) # the FIR filter only needs numerator coefficients, denominator coefficients (2nd argument) are set to 1

    # COMMENT TO ROSS: we can also allow users to plot the frequency distribution of the PDF before and after filtering
    Y = fft(G)
    Yfilt = fft(Gfilt)
    freq = fftfreq(len(r),r[1] - r[0])

    plt.figure(1)
    plt.plot(freq,np.abs(Y),'k',label = 'Original')
    plt.plot(freq, np.abs(Yfilt),'r',label = 'Filtered')
    plt.xlim((0,3*(1/period)))
    plt.axvline(1/period,color = 'b',linestyle = '--',label = 'Theoretical ripple freq.')
    plt.axvline(cutoff,color = 'g',linestyle = '--',label = 'Cutoff freq.')
    plt.xlabel('Frequency (1/Å)')
    plt.ylabel('Power')
    plt.legend(loc = 'best')
    plt.show()

    # Return the filtered G(r)
    return Gfilt


######## Structure factor reliability check using Rahman's method #######

# COMMENT FOR ROSS: still some work needed to understand the limitations and uses of this method, but the algorithm is working and we can implement
# this as an option in aEDXD

def rahman_check(q,Sq,rho0,L,mu):

    # Initiate arrays
    LHS = []; RHS = []; cfactor = []

    for i in range(len(mu)):
        mu_temp = mu[i]
        
        # calculate left hand side (LHS)
        j1 = np.sin(mu_temp*L)/(mu_temp*L)**2 - np.cos(mu_temp*L)/(mu_temp*L) # 1st order bessel function
        LHS.append(4*np.pi*rho0*L**3*j1/(mu_temp*L))
        
        # calculate right hand side (RHS)
        A = q*(Sq - 1)
        B = np.sin((q + mu_temp)*L) / ((q + mu_temp)*L) # 2nd order bessel function
        C = np.sin((q - mu_temp)*L) / ((q - mu_temp)*L) # 2nd order bessel function
        integrand = A*(B - C)
        RHS.append((L/(np.pi*mu_temp))*integrate.simpson(integrand,q))
        
        # solve for the correction factor
        def func(x):
            return LHS[i] - L/(np.pi*mu_temp)*integrate.simpson(q*(x*Sq - 1)*(B - C),q)
        cfactor.append(fsolve(func,1)) # the 2nd argument is the initial guess, set to 1 b/c we assume the correction factor should be within a few % of that

    return LHS, RHS, cfactor