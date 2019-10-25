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



import numpy as np


def convert_units(value, wavelength, previous_unit, new_unit):
    """
    Converts a value from a unit into a new unit
    :param value: value in old unit
    :param wavelength: in Angstrom
    :param previous_unit: possible values are '2th_deg', 'q_A^-1', 'd_A'
    :param new_unit: possible values are '2th_deg', 'q_A^-1', 'd_A'
    :return: new value or None if unit does not exist
    """
    if previous_unit == '2th_deg':
        tth = value
    elif previous_unit == 'q_A^-1':
        tth = np.arcsin(
            value * 1e10 * wavelength / (4 * np.pi)) * 360 / np.pi
    elif previous_unit == 'd_A':
        tth = 2 * np.arcsin(wavelength / (2 * value * 1e-10)) * 180 / np.pi
    else:
        tth = 0

    if new_unit == '2th_deg':
        res = tth
    elif new_unit == 'q_A^-1':
        res = 4 * np.pi * \
              np.sin(tth / 360 * np.pi) / \
              wavelength / 1e10
    elif new_unit == 'd_A':
        res = wavelength / (2 * np.sin(tth / 360 * np.pi)) * 1e10
    else:
        res = None
    return res
