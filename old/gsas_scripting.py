
import gsas.GSASIIscriptable as G2sc
'''
refs = G2sc.GenerateReflections('F m 3 m', 
    (3.,3.,3.,90.,90.,90), 
    TTmax=20,wave=.5) 
#for r in refs: print(r) 
'''

spc = G2sc.G2spc

s = spc.SpcGroup('P 4')
print(s[-1]['SGSys'])
