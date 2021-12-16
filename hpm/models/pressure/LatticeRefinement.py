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

from numpy import sqrt, std, average, matrix, matmul, linalg, sin, pi, arccos, cos


class latticeRefinement():
    def __init__(self, *args, **kwargs):
        self.a = -1
        self.b = -1
        self.c = -1
        self.alpha = -1
        self.beta = -1
        self.gamma = -1
        self.esd_a = -1
        self.esd_b = -1
        self.esd_c = -1
        self.esd_alpha = -1
        self.esd_beta = -1
        self.esd_gamma = -1
        self.dhkl = []
        self.DelD = []
        self.volume = -1
        self.symmetry = ''
        self.refinement_output = dict()
        self.lattice = dict()
        self.esd_lattice = dict()

    def set_dhkl(self, dhkl):
        self.dhkl=dhkl

    def set_symmetry(self, symmetry):
        self.symmetry = symmetry
        
    def refine(self):
        if self.symmetry == 'cubic':
            l = isometric(self.dhkl)
        if self.symmetry == 'hexagonal':
            l = hexagonal(self.dhkl)
        if self.symmetry == 'tetragonal':
            l = tetragonal(self.dhkl)
        if self.symmetry == 'orthorhombic':
            l = orthorhombic(self.dhkl)
        if self.symmetry == 'monoclinic':
            l = monoclinic(self.dhkl)
        self.refinement_output = l
    
        lattice, esd_lattice = dict_to_lattice(l,self.symmetry)
        self.set_lattice(lattice, esd_lattice)
            
    def set_lattice(self, lattice, esd_lattice):
        '''
        private method
        '''
        self.lattice=lattice
        self.a = self.lattice['a']
        self.b = self.lattice['b']
        self.c = self.lattice['c']
        self.alpha = self.lattice['alpha']
        self.beta = self.lattice['beta']
        self.gamma = self.lattice['gamma']

        self.esd_lattice=esd_lattice
        self.esd_a = self.esd_lattice['a']
        self.esd_b = self.esd_lattice['b']
        self.esd_c = self.esd_lattice['c']
        self.esd_alpha = self.esd_lattice['alpha']
        self.esd_beta = self.esd_lattice['beta']
        self.esd_gamma = self.esd_lattice['gamma']

    def get_lattice(self):
        return self.lattice

    def get_volume(self):
        self.volume = cell_volume(self.lattice)
        return self.volume


def isometric(reflections):
    """
    reflections = [[d, h, k, l]]
    """
    # Python port based on excel Cubic least squares template, by:
    # G.A. Novak & A.A. Colville - 1989
    # American Mineralogist, v. 74, p. 488-490.
    Q = []
    hkl = []
    for r in reflections:
        q = 1/r[0]**2
        Q.append(q)
        hkl.append(r[1]**2+r[2]**2+r[3]**2)
    sum_hkl = sum(hkl)
    aStar2 = sum(Q)   / sum_hkl
    a = 1/ sqrt(aStar2)
    DelQ=[]
    DelD=[]
    DCalc=[]
    for i, r in enumerate(reflections):
        dcalc = 1/sqrt(hkl[i]*aStar2)
        DCalc.append(dcalc)
        deld = r[0]-dcalc
        DelD.append(deld)
        qcalc = 1/dcalc**2
        delq = Q[i]-qcalc
        DelQ.append(delq)
    stdev_q = std(DelQ)
    ave_del_d = average(DelD)
    esd = sqrt(1/(sum_hkl))*stdev_q
    esd_a = int(round(1000*(abs(a-1/sqrt(aStar2+esd)))+0.005,0))
    return {'a':a, 'esd_a':esd_a, 'ave_del_d':ave_del_d, 'stdev_q':stdev_q,'Dcalc':DCalc}

def hexagonal(reflections):
    """
    reflections = [[d, h, k, l]]
    """
    # Python port based on excel Hexagonal least squares template, by:
    # G.A. Novak & A.A. Colville - 1989
    # American Mineralogist, v. 74, p. 488-490.
    # Compute sums for Least Squares

    # l^4
    # (h^2+hk+k^2)
    # (h^2+h*k+k^2)*l^2
    # l^2Q
    # (h2+hk+k2)^2Q
    Q = []
    l4 = []
    h2hkk2 = []
    h2hkk2l2 = []
    l2Q = []
    h2hkk22Q = []
    for r in reflections:
        h = r[1]
        k = r[2]
        l = r[3]
        q = 1/r[0]**2
        Q.append(q)
        l4.append(l**4)
        h2hkk2.append((h**2+h*k+k**2)**2)
        h2hkk2l2.append((h**2+h*k+k**2)*l**2)
        l2Q.append(l**2*q)
        h2hkk22Q.append((h**2+h*k+k**2)*q)
    sum_l4 = sum(l4)
    sum_h2hkk2 = sum(h2hkk2)
    sum_h2hkk2l2 = sum(h2hkk2l2)
    sum_l2Q = sum(l2Q)
    sum_h2hkk22Q = sum(h2hkk22Q)
    x_matrix = [[sum_h2hkk2, sum_h2hkk2l2],
                [sum_h2hkk2l2, sum_l4]]
    y_matrix = [[sum_h2hkk22Q],
                [sum_l2Q]]
    #  X * A = Y thus A = X(inverse) * Y
    x_matrix_inv = linalg.inv(x_matrix)
    a_c_star2 = matmul(x_matrix_inv,y_matrix)
    aStar2= a_c_star2[0][0]
    cStar2= a_c_star2[1][0]
    a = 2/sqrt(aStar2*3)
    c =1/sqrt(cStar2)
    DelQ=[]
    DelD=[]
    DCalc=[]
    for i, r in enumerate(reflections):
        d = r[0]
        h = r[1]
        k = r[2]
        l = r[3]
        dcalc = 1/sqrt((h**2+h*k+k**2)*aStar2+l**2*cStar2)
        DCalc.append(dcalc)
        deld = d-dcalc
        DelD.append(deld)
        qcalc = 1/dcalc**2
        delq = Q[i]-qcalc
        DelQ.append(delq)
    stdev_q = std(DelQ)
    ave_del_d = average(DelD)
    esd_astar2 =stdev_q*sqrt(x_matrix_inv[0][0])
    esd_cstar2 =stdev_q*sqrt(x_matrix_inv[1][1])
    esd_a = int(round(1000*(abs(a-2/sqrt(3*(aStar2+esd_astar2))+0.005)),0))
    esd_c = int(round(1000*(abs(c-1/sqrt(cStar2+esd_cstar2)+0.005)),0))
    return {'a':a, 'c':c, 'esd_a':esd_a, 'esd_c':esd_c, 'ave_del_d':ave_del_d, 'stdev_q':stdev_q,'Dcalc':DCalc}

def tetragonal(reflections):
    """
    reflections = [[d, h, k, l]]
    """
    # l^4=
    # (h^2+k^2)^2=
    # (h^2+k^2)*l^2=
    # l^2Q=
    # (h2+K2)^2Q=
    Q = []
    l4 = []
    h2k22 = []
    h2k2l2 = []
    l2Q = []
    h2K22Q = []
    for r in reflections:
        d = r[0]
        h = r[1]
        k = r[2]
        l = r[3]
        q = 1/d**2
        Q.append(q)
        l4.append(l**4)
        h2k22.append((h**2+k**2)**2)
        h2k2l2.append((h**2+k**2)*l**2)
        l2Q.append(l**2*q)
        h2K22Q.append((h**2+k**2)*q)
    sum_l4 = sum(l4)
    sum_h2k22 = sum(h2k22)
    sum_h2k2l2 = sum(h2k2l2)
    sum_l2Q = sum(l2Q)
    sum_h2K22Q = sum(h2K22Q)
    x_matrix = [[sum_h2k22, sum_h2k2l2],
                [sum_h2k2l2, sum_l4]]
    y_matrix = [[sum_h2K22Q],
                [sum_l2Q]]
    #  X * A = Y thus A = X(inverse) * Y
    x_matrix_inv = linalg.inv(x_matrix)
    a_c_star2 = matmul(x_matrix_inv,y_matrix)
    aStar2= a_c_star2[0][0]
    cStar2= a_c_star2[1][0]
    a = 1/sqrt(aStar2)
    c =1/sqrt(cStar2)
    DelQ=[]
    DelD=[]
    DCalc=[]
    for i, r in enumerate(reflections):
        d = r[0]
        h = r[1]
        k = r[2]
        l = r[3]
        dcalc = 1/sqrt((h**2+k**2)*aStar2+l**2*cStar2)
        DCalc.append(dcalc)
        deld = d-dcalc
        DelD.append(deld)
        qcalc = 1/dcalc**2
        delq = Q[i]-qcalc
        DelQ.append(delq)
    stdev_q = std(DelQ)
    ave_del_d = average(DelD)
    esd_astar2 =stdev_q*sqrt(x_matrix_inv[0][0])
    esd_cstar2 =stdev_q*sqrt(x_matrix_inv[1][1])
    esd_a = int(round(1000*(abs(a-1/sqrt(aStar2+esd_astar2)+0.005)),0))
    esd_c = int(round(1000*(abs(c-1/sqrt(cStar2+esd_cstar2)+0.005)),0))
    return {'a':a, 'c':c, 'esd_a':esd_a, 'esd_c':esd_c, 'ave_del_d':ave_del_d, 'stdev_q':stdev_q,'Dcalc':DCalc}

def orthorhombic(reflections):
    """
    reflections = [[d, h, k, l]]
    """
    # h^4 
    # k^4
    # l^4
    # h^2k^2
    # h^2l^2
    # k^2l^2
    # h^2Q
    # k^2Q
    # l^2Q
    Q = []
    h4 = []
    k4 = []
    l4 = []
    h2k2 = []
    h2l2 = []
    k2l2 = []
    h2Q = []
    k2Q = []
    l2Q = []
    for r in reflections:
        d = r[0]
        h = r[1]
        k = r[2]
        l = r[3]
        q = 1/d**2
        Q.append(q)
        h4.append(h**4)
        k4.append(k**4)
        l4.append(l**4)
        h2k2.append(h**2*k**2)
        h2l2.append(h**2*l**2)
        k2l2.append(k**2*l**2)
        h2Q.append(h**2*q)
        k2Q.append(k**2*q)
        l2Q.append(l**2*q)
    sum_h4 = sum(h4)
    sum_k4 = sum(k4)
    sum_l4 = sum(l4)
    sum_h2k2 = sum(h2k2)
    sum_h2l2 = sum(h2l2)
    sum_k2l2 = sum(k2l2)
    sum_h2Q = sum(h2Q)
    sum_k2Q = sum(k2Q)
    sum_l2Q = sum(l2Q)
    x_matrix = [[sum_h4  , sum_h2k2, sum_h2l2],
                [sum_h2k2, sum_k4  , sum_k2l2],
                [sum_h2l2, sum_k2l2, sum_l4  ]]
    y_matrix = [[sum_h2Q],
                [sum_k2Q],
                [sum_l2Q]]
    #  X * A = Y thus A = X(inverse) * Y
    x_matrix_inv = linalg.inv(x_matrix)
    abc_star2 = matmul(x_matrix_inv,y_matrix)
    aStar2= abc_star2[0][0]
    bStar2= abc_star2[1][0]
    cStar2= abc_star2[2][0]
    a = 1/sqrt(aStar2)
    b = 1/sqrt(bStar2)
    c = 1/sqrt(cStar2)
    DelQ=[]
    DelD=[]
    DCalc=[]
    for i, r in enumerate(reflections):
        d = r[0]
        h = r[1]
        k = r[2]
        l = r[3]
        dcalc = 1/sqrt(h**2*aStar2+k**2*bStar2+l**2*cStar2)
        DCalc.append(dcalc)
        deld = d-dcalc
        DelD.append(deld)
        qcalc = 1/dcalc**2
        delq = Q[i]-qcalc
        DelQ.append(delq)
    stdev_q = std(DelQ)
    ave_del_d = average(DelD)
    esd_astar2 =stdev_q*sqrt(x_matrix_inv[0][0])
    esd_bstar2 =stdev_q*sqrt(x_matrix_inv[1][1])
    esd_cstar2 =stdev_q*sqrt(x_matrix_inv[2][2])
    esd_a = int(round(1000*(abs(a-1/sqrt(aStar2+esd_astar2)+0.005)),0))
    esd_b = int(round(1000*(abs(b-1/sqrt(bStar2+esd_bstar2)+0.005)),0))
    esd_c = int(round(1000*(abs(c-1/sqrt(cStar2+esd_cstar2)+0.005)),0))
    return {'a':a, 'b':b, 'c':c, 'esd_a':esd_a, 'esd_b':esd_b, 'esd_c':esd_c, 'ave_del_d':ave_del_d, 'stdev_q':stdev_q,'Dcalc':DCalc}

def monoclinic(reflections):
    """
    reflections = [[d, h, k, l]]
    """
    # h^4
    # k^4
    # l^4
    # h^2k^2
    # h^2l^2
    # k^2l^2
    # h^3l
    # hk^2l
    # hl^3
    # h2^Q
    # k^2Q
    # l^2Q
    # hlQ

    Q       = []
    h4      = []
    k4      = []
    l4      = []
    h2k2    = []
    h2l2    = []
    k2l2    = []
    h3l     = []
    hk2l    = []
    hl3     = []
    h2Q     = []
    k2Q     = []
    l2Q     = []
    hlQ     = []
    for r in reflections:
        d = r[0]
        h = r[1]
        k = r[2]
        l = r[3]
        q = 1/d**2
        Q.append(q)
        h4.append(h**4)
        k4.append(k**4)
        l4.append(l**4)
        h2k2.append(h**2*k**2)
        h2l2.append(h**2*l**2)
        k2l2.append(k**2*l**2)
        h3l.append(h**3*l)
        hk2l.append(h*k**2*l)
        hl3.append(h*l**3)
        h2Q.append(h**2*q)
        k2Q.append(k**2*q)
        l2Q.append(l**2*q)
        hlQ.append(h*l*q)
    sum_h4   = sum(h4)
    sum_k4   = sum(k4)
    sum_l4   = sum(l4)
    sum_h2k2 = sum(h2k2)
    sum_h2l2 = sum(h2l2)
    sum_k2l2 = sum(k2l2)
    sum_h3l  = sum(h3l)
    sum_hk2l = sum(hk2l)
    sum_hl3  = sum(hl3)
    sum_h2Q  = sum(h2Q)
    sum_k2Q  = sum(k2Q)
    sum_l2Q  = sum(l2Q)
    sum_hlQ  = sum(hlQ)
    
    x_matrix = [[sum_h4  , sum_h2k2, sum_h2l2, sum_h3l ],
                [sum_h2k2, sum_k4  , sum_k2l2, sum_hk2l],
                [sum_h2l2, sum_k2l2, sum_l4  , sum_hl3 ],
                [sum_h3l , sum_hk2l, sum_hl3 , sum_h2l2]]
 
    y_matrix = [[sum_h2Q],
                [sum_k2Q],
                [sum_l2Q],
                [sum_hlQ]]

    #  X * A = Y thus A = X(inverse) * Y
    x_matrix_inv = linalg.inv(x_matrix)
    abcp_star2= matmul(x_matrix_inv,y_matrix)
    aStar2   = abcp_star2[0][0]   # astar^2
    bStar2   = abcp_star2[1][0]   # bstar^2
    cStar2   = abcp_star2[2][0]   # cstar^2
    pStar    = abcp_star2[3][0]   # 2 astar cstar Cos(ßstar)
    
    d_100 = 1/sqrt(aStar2)
    d_001 = 1/sqrt(cStar2)
    beta  = 180-arccos(pStar/(2*(1/d_100)*(1/d_001)))*180/pi
    a = d_100 / sin(beta*pi/180)
    b = 1/sqrt(bStar2)
    c = d_001/sin(beta*pi/180)
    
    DelQ=[]
    DelD=[]
    DCalc=[]
    for i, r in enumerate(reflections):
        d = r[0]
        h = r[1]
        k = r[2]
        l = r[3]
        dcalc = 1/sqrt(h**2*aStar2+k**2*bStar2+l**2*cStar2+h*l*pStar)
        DCalc.append(dcalc)
        deld = d-dcalc
        DelD.append(deld)
        qcalc = 1/dcalc**2
        delq = Q[i]-qcalc
        DelQ.append(delq)
    stdev_q = std(DelQ)
    ave_del_d = average(DelD)
    esd_astar2 =stdev_q*sqrt(x_matrix_inv[0][0])
    esd_bstar2 =stdev_q*sqrt(x_matrix_inv[1][1])
    esd_cstar2 =stdev_q*sqrt(x_matrix_inv[2][2])
    esd_Bstar = stdev_q*sqrt(x_matrix_inv[3][3])
    
    esd_a = int(round(1000*abs(0.5*(aStar2)**(-3/2)*esd_astar2/(sin(beta*pi/180))),0))
    esd_b = int(round(1000*abs(0.5*(bStar2)**(-3/2)*esd_bstar2),0))
    esd_c = int(round(1000*abs(0.5*(cStar2)**(-3/2)*esd_cstar2/(sin(beta*pi/180))),0))
    esd_beta = int(round(1000*((1/(2*(1/d_100)*(1/d_001))*180/pi)/sqrt(1-(((pStar/(2*(1/d_100)*(1/d_001)))*2)**180/pi)))*esd_Bstar+0.5,0))
    return {'a':a, 'b':b, 'c':c, 'beta':beta, 'esd_a':esd_a, 'esd_b':esd_b, 'esd_c':esd_c, 'esd_beta':esd_beta, 'ave_del_d':ave_del_d, 'stdev_q':stdev_q,'Dcalc':DCalc}

def triclinic(reflections):
    pass

def dict_to_lattice(dictionary:'dict', symmetry:'str'='') :
        lattice = dict()
        esd_lattice = dict()
        if 'a' in dictionary.keys():
            lattice['a']= dictionary['a']
            if 'b' in dictionary.keys():
                lattice['b']= dictionary['b']
            else:
                lattice['b']=lattice['a']
            if 'c' in dictionary.keys():
                lattice['c']= dictionary['c']
            else:
                lattice['c']=lattice['a']
            if 'alpha' in dictionary.keys():
                lattice['alpha']= dictionary['alpha']
            else:
                lattice['alpha']=90
            if 'beta' in dictionary.keys():
                lattice['beta']= dictionary['beta']
            else:
                lattice['beta']=90
            if 'gamma' in dictionary.keys():
                lattice['gamma']= dictionary['gamma']
            else:
                if symmetry == 'hexagonal':
                    lattice['gamma']=120
                else:
                    lattice['gamma']=90
            
            if 'esd_a' in dictionary.keys():
                esd_lattice['a']= dictionary['esd_a']
            if 'esd_b' in dictionary.keys():
                esd_lattice['b']= dictionary['esd_b']
            else:
                esd_lattice['b']=esd_lattice['a']
            if 'esd_c' in dictionary.keys():
                esd_lattice['c']= dictionary['esd_c']
            else:
                esd_lattice['c']=esd_lattice['a']
            if 'esd_alpha' in dictionary.keys():
                esd_lattice['alpha']= dictionary['esd_alpha']
            else:
                esd_lattice['alpha']=0
            if 'esd_beta' in dictionary.keys():
                esd_lattice['beta']= dictionary['esd_beta']
            else:
                esd_lattice['beta']=0
            if 'esd_gamma' in dictionary.keys():
                esd_lattice['gamma']= dictionary['esd_gamma']
            else:
                esd_lattice['gamma']=0
            return lattice, esd_lattice

        else:
            return None

def cell_volume(lattice):
        a = lattice['a']
        b = lattice['b']
        c = lattice['c']
        alpha = lattice['alpha']
        beta = lattice['beta']
        gamma = lattice['gamma']
        V = a*b*c* (1- cos(alpha*pi/180)**2 - \
                        cos(beta*pi/180)**2 - \
                        cos(gamma*pi/180)**2+ \
                        2*(cos(alpha*pi/180)* \
                        cos(beta*pi/180)* \
                        cos(gamma*pi/180)))**(1/2)
        return V



#################################################
# unit tests:
#################################################

'''

iso_dhkl = [[2.030, 1, 1, 0],
            [1.435, 2, 0, 0],
            [1.170, 1, 1, 2],
            [1.014, 2, 2, 0],
            [0.906, 3, 1, 0]]

hex_dhkl = [[2.8369, 0, 0, 1],
            [1.7795, 1, 1, 1],
            [1.6227, 2, 0, 1],
            [1.4199, 0, 0, 2]]  

tet_dhkl = [[4.400, 0, 0, 2],
            [4.290, 2, 0, 0],
            [3.016, 2, 2, 0]]  

ort_dhkl = [[8.897, 0, 2, 0],
            [9.307, 2, 0, 0],
            [4.899, 1, 1, 1],
            [4.448, 2, 1, 1],
            [2.342, 3, 2, 2]]  

mon_dhkl = [[2.990, 2, 2, -1],
            [2.529, 0, 0,  2],
            [2.529, 2, 0, -2],
            [2.892, 3, 1, -1],
            [2.517, 1, 1, -2],
            [2.517, 2, 2,  1],
            [3.225, 2, 2,  0],
            [2.948, 3, 1,  0],
            [1.626, 2, 2, -3],
            [1.626, 5, 3, -1]]






i_cell = isometric(iso_dhkl)
print ('isometric: a = ' +'%.3f'%(i_cell['a']) + ' ('+str(i_cell['esd_a'])+') A')

h_cell = hexagonal(hex_dhkl)
print ('hexagonal: a = ' +'%.3f'%(h_cell['a']) + ' ('+str(h_cell['esd_a'])+') A'+ \
                '; c = '+'%.3f'%(h_cell['c'])+ ' ('+str(h_cell['esd_c'])+') A')

t_cell = tetragonal(tet_dhkl)
print ('tetragonal: a = ' +'%.3f'%(t_cell['a']) + ' ('+str(t_cell['esd_a'])+') A'+ \
                 '; c = '+'%.3f'%(t_cell['c'])+ ' ('+str(t_cell['esd_c'])+') A')            

o_cell = orthorhombic(ort_dhkl)
print ('orthorhombic: a = ' +'%.3f'%(o_cell['a']) + ' ('+str(o_cell['esd_a'])+') A'+ \
                 '; b = '+'%.3f'%(o_cell['b'])+ ' ('+str(o_cell['esd_b'])+') A'+ \
                 '; c = '+'%.3f'%(o_cell['c'])+ ' ('+str(o_cell['esd_c'])+') A')

m_cell = monoclinic(mon_dhkl)
print ('monoclinic: a = ' +'%.3f'%(m_cell['a']) + ' ('+str(m_cell['esd_a'])+') A'+ \
                 '; b = '+'%.3f'%(m_cell['b'])+ ' ('+str(m_cell['esd_b'])+') A'+ \
                 '; c = '+'%.3f'%(m_cell['c'])+ ' ('+str(m_cell['esd_c'])+') A'+ \
                 '; beta = '+'%.3f'%(m_cell['beta'])+ ' ('+str(m_cell['esd_beta'])+') deg') 
 
'''
