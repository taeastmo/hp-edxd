        
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

import numpy as Numeric
#from mcaModel import McaROI
import utilities.CARSMath as CARSMath

def computeCentroid(data, roi, return_fit=0):    
    # Compute the centroid and FWHM of each ROI
    left = roi.left
    right = roi.right+1
    total_counts = data[left:right]
    n_sel        = right - left
    sel_chans    = left + Numeric.arange(n_sel)
    left_counts  = data[left]
    right_counts = data[right]
    ave_counts = (left_counts+right_counts)/2

    bgd_counts   = (left_counts + Numeric.arange(float(n_sel))/(n_sel-1) *
                                (right_counts - left_counts))
    net_counts   = total_counts - ave_counts
    net          = Numeric.sum(net_counts)

    if ((net > 0.) and (n_sel >= 3)):
        if return_fit == 0:
            amplitude, centroid, fwhm = CARSMath.fit_gaussian(sel_chans, net_counts, return_fit=0)
        if return_fit == 1:
            [amplitude, centroid, fwhm, yfit, x_yfit] = CARSMath.fit_gaussian(sel_chans, net_counts, return_fit=1)
            
        if centroid > left and centroid < right:
            roi.yFit = yfit+ave_counts
            roi.counts = net_counts+ave_counts
            roi.x_yfit= x_yfit
            roi.centroid = centroid
            fwhm_chan = fwhm
        else:
            roi.yFit = total_counts
            roi.counts = total_counts
            roi.x_yfit= sel_chans
            roi.centroid = (left + right)/2.
            fwhm_chan = right-left
    else:
        if len(total_counts):
            roi.yFit = total_counts
            roi.x_yfit= sel_chans
            roi.counts = total_counts    
            roi.centroid = (left + right)/2.
            fwhm_chan = right-left
        else:
            print('roi total counts error')
            fwhm_chan = -1
        
        
    roi.channels =sel_chans

    return [roi, fwhm_chan]
    
       