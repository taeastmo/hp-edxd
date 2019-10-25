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

from math import sin, pi,asin
from functools import partial
from scipy.optimize import minimize
import time

#######################
# unit conversions
#######################

def d_to_q(d):
    q = 2. * pi / d
    return q

def q_to_d(q):
    d = 2. * pi / q
    return d

def tth_e_to_d(tth,e):
    λ = e_to_λ(e)
    d = λ/(2.0 * sin(0.5 * tth * 0.0174532925199433))
    return d

def d_e_to_tth(d,e):
    λ = e_to_λ(e)
    s = (λ/d)/2.0

    tth= asin(s)/(0.5 *0.0174532925199433)
    
    return tth

def tth_d_to_e(tth, d):
    λ = d*(2.0 * sin(0.5 * tth * 0.0174532925199433))
    e = λ_to_e(λ)
    return e

def e_to_λ(e): # in kev
    E = e * 1000 # to ev
    c =  299792458
    h = 4.135667516e-15
    λ = h*c/E
    return λ * 1e10 # to angstrom

def λ_to_e(λ): # in kev
    λ =λ * 1e-10 # to meters
    c =  299792458
    h = 4.135667516e-15
    E = h*c/λ
    e = E / 1000 # to kev
    return e 


def get_tth(q_low,e_low,e_high):
    d_low = q_to_d(q_low)
    tth = d_e_to_tth(d_low,e_low)
    d_high = tth_e_to_d(tth,e_high)
    q_high = q_to_d(d_high)
    return tth, q_high

def get_min_n(q_low,q_high,e_low,e_high, overlap_fract):
    q_high_i = 0
    n = 0
    while q_high_i < q_high :
        _ , q_high_i = get_tth(q_low,e_low,e_high)
        q_low = q_high_i-(q_high_i-q_low)*overlap_fract
        n = n +1
    return n

def get_seq(n,q_low,e_low,e_high, overlap_fract):
    tth = []
    tth_i =0
    q_high_i = 0
    for _ in range(n):
        q = {}
        q['q_low']=q_low
        tth_i, q_high_i = get_tth(q_low,e_low,e_high)
        q['q_high']=q_high_i
        q_low = q_high_i-(q_high_i-q_low)*overlap_fract
        q['tth']=tth_i
        tth.append(q)
    return tth

def get_seq_from_tth(tth,e_low,e_high):
    qs = []
    for t in tth:
        q = {}
        q['tth']=t
        d_low = tth_e_to_d(t,e_low)
        q_low = d_to_q(d_low)
        q['q_low']=round(q_low,1)
        d_high = tth_e_to_d(t,e_high)
        q_high = d_to_q(d_high)
        q['q_high']=round(q_high,1)
        qs.append(q)
    return qs
        

def get_q_high_diff(n,q_low,q_high,e_low,e_high, overlap_fract):
    seq = get_seq(n,q_low,e_low,e_high, overlap_fract)
    high_q = seq[-1]['q_high']
    diff= (q_high-high_q)**2
    return diff

def optimize_tth(q_low,q_high,e_low,e_high,overlap_fract):
    n = get_min_n(q_low,q_high,e_low,e_high,overlap_fract)
    func = partial(get_q_high_diff,n,q_low,q_high,e_low,e_high)
    result = minimize(func,overlap_fract)
    overlap_fract_optimal = round(float(result.x[0]),3)
    seq = get_seq(n,q_low,e_low,e_high, overlap_fract_optimal)
    t = []
    for tth in seq:
        t.append(round(tth['tth'],1))
    tth = get_seq_from_tth(t,e_low,e_high)

    return n, overlap_fract_optimal, tth