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

# Principal author: R. Hrubiak (hrubiak@anl.gov)
# Copyright (C) 2018-2019 ANL, Lemont, USA


from math import sqrt, sin, pi, radians, atan, degrees, tan, cos

def get_collimation_depth(params):

    det_slit_size=params['dhsize']
    primary_slit_size=params['phsize']
    secondary_slit_size=params['shsize']
    incident_slit_size = min([primary_slit_size,secondary_slit_size])
    tth=params['tth']
    det_slit_distance=params['det_slit_distance']
    tip_slit_distance=params['tip_slit_distance']
    tip_slit_size=params['tip_slit_size']

    C3 = tth  
    C4 = det_slit_size
    C5 = incident_slit_size
    F5 = det_slit_distance
    F4 = tip_slit_distance
    F3 = tip_slit_size

    # 2theta (rad)
    F8 = radians(C3)
    # Virtual convergence point from det. slit (mm), f  
    F10 =  C4*(F5-F4)/(F3+C4)
    # Slit divergence angle (rad), Ʈ
    F11 = atan(C4/2/F10)
    # Slit divergence angle (degree), Ʈ
    F12 = degrees(F11)
    # Vertial upstream width (mm), Wx
    F14 = F3*(F5-F10)/(2*(F5-F4-F10))
    # Vertial downstream width (mm), Wx2
    F15 = F3*(F5-F10)/(2*(F5-F4-F10+F3/2/tan(F8)))
    # upstream collimation depth (mm)
    F17 = F14*sin(F8)+F14*cos(F8)/tan(F8-F11)
    # downstream collimation depth (mm)
    F18 = F3*(F5-F10)/(2*sin(F8)*(F5-F4-F10+F3/(2*tan(F8))))
    # incident slit size correction for upstream collimation depth (mm)
    F20 = C5/2/tan(F8-F11)
    # incident slit size correction for downstream collimation depth (mm)
    F21 = C5/2/tan(F8+F11)
    # Max. upstream collimation depth (mm)
    F23 = F17+F20
    # Max. downstream collimation depth (mm)
    F24 = F18+F21
    # D0: Collimation depth at the sample center (mm)
    C7 = F17+F18
    # Total area
    F26 = C7*C5
    # Part of Max. collimation depth length area
    F28 = F20*(C5/2)/2+F21*(C5/2)/2
    # Collimation depth length area
    F27 = F26-F28
    # Proportion of Max. collimation depth length area
    F29 = F28/F26*100
    # D1: Maximum collimation depth (mm)
    C8 = F23+F24
    
    D = {'d0':round(C7,2), 'd1':round(C8,2)}
    return D

