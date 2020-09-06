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
import os
from .. import data_path

class aEDXDAtomicParameters():
    
    def __init__(self):
        self.MKL = read_ascii_table(os.path.join(data_path, "MKL.dat"))
        self.abc = read_ascii_table(os.path.join(data_path, "ABC.dat"))
        self.ab5 = read_ascii_table(os.path.join(data_path, "AB5.dat"))

    def _lookup_oxidation_states_abc(self,atomic_symbol):
        atoms = self.abc['str_data'][:,:1]
        indeces = [i for i, x in enumerate(atoms) if x==atomic_symbol]
        oxidation_states = self.abc['str_data'][indeces,[1]]
        return oxidation_states, indeces

    def _lookup_oxidation_states_ab5(self,atomic_symbol):
        atoms = self.ab5['str_data']
        indeces = [i for i, x in enumerate(atoms) if x==atomic_symbol]
        oxidation_states = self.ab5['str_data'][indeces]
        return oxidation_states, indeces

    def _lookup_oxidation_states_MKL(self,atomic_symbol):
        atoms = self.MKL['str_data']
        indeces = [i for i, x in enumerate(atoms) if (
                                            atomic_symbol == x or 
                                            atomic_symbol+'-' == x or
                                            atomic_symbol+'+' == x)]
        oxidation_states = self.MKL['str_data'][indeces]
        return oxidation_states, indeces

    def _get_abc(self,index):
        abc = self.abc['num_data'][[index],:][0]
        return abc

    def _get_MKL(self,index):
        MKL = self.MKL['num_data'][[index],:][0]
        return MKL

    def _get_ab5(self,index):
        ab5 = self.ab5['num_data'][[index],:][0]
        return ab5

    def get_abc_options(self,atomic_symbol):
        ox, indices = self._lookup_oxidation_states_abc(atomic_symbol)
        options = dict()
        for i, ind in enumerate(indices):
            key = ox[i].split(':')[0]
            options[key]=self._get_abc(ind)
        return options

    def get_ab5_options(self,atomic_symbol):
        ox, indices = self._lookup_oxidation_states_ab5(atomic_symbol)
        options = dict()
        for i, ind in enumerate(indices):
            key = ox[i].split(':')[0]
            options[key]=self._get_ab5(ind)
        return options

    def get_MKL_options(self,atomic_symbol):
        ox, indices = self._lookup_oxidation_states_MKL(atomic_symbol)
        options = dict()
        for i, ind in enumerate(indices):
            options[ox[i]]=self._get_MKL(ind)
        return options

    def lookup_atom_by_sq_par(self,sq_par):
        atom_abc_note = None
        atom_MKL_note = None
        atom =None
        abc = sq_par[2:-3]
        mkl = sq_par[-3:]
        frac = sq_par[1]
        atoms_abc = self.abc['str_data']#[:,:]
        atoms_MKL = self.MKL['str_data']#[:]
        atoms_ab5 = self.ab5['str_data']
        for i, a in enumerate(self.abc['num_data']):
            if (abc==a[1:]).all():
                atom = atoms_abc[i][0]
                atom_abc_note = atoms_abc[i][1].split(':')[0]
        for i, m in enumerate(self.MKL['num_data']):
            if (mkl==m[1:-1]).all():
                atom_MKL_note = atoms_MKL[i]
        return  atom, atom_abc_note, atom_MKL_note, frac
        

def read_ascii_table(filename):
    f = open(filename,'r')
    header = f.readline()
    words = header.split('\t')[:-1]
    l1 = f.readline()
    columns = l1.split('\t')[:-1]
    num_cols = []
    str_cols = []
    
    for i, c in enumerate(columns):
        if c.replace('.','',1).replace('-','',1).replace('e','',1).isdigit():
            num_cols.append(i)
        else: 
            str_cols.append(i)
    f.seek(0,0)
    l1 = f.readline()
    d = np.loadtxt(f, delimiter='\t', usecols=tuple(num_cols))
    f.seek(0,0)
    f.readline()
    s = np.loadtxt(f, delimiter='\t', usecols=tuple(str_cols),dtype='str')
    return {'header':header, 'str_cols':str_cols,'num_cols':num_cols,  'str_data':s,'num_data':d }
    
