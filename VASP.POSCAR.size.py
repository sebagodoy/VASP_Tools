#!/usr/bin/env python3
# Ver.: 1.0 (25/dic/2023 - Merry Xmas)
# Author: SAGG (sebagodoy@udec.cl)

import numpy as np
print('  Geometric parameters for POSCAR/CONTCAR-type VASP file')

#### Open file ------------------------------------------------------------------------------------------------
filename = input('  > Filename (def=POSCAR)    : ') or 'POSCAR'
try:
    with open(filename, 'r') as f:
        cont = f.readlines()
except FileNotFoundError:
    quit(' ... wait a second, you don\'t have that file! bye liar')
#### Read cell ------------------------------------------------------------------------------------------------
CellFactor = float(cont[1])
CellBox = [[float(j)*CellFactor for j in i.split()] for i in cont[2:5]]

#### Compute al possible areas (for fun) ----------------------------------------------------------------------
def AreaVectors(aa, bb):
    return np.linalg.norm(np.cross(aa, bb))
def VolumeCell(aa, bb, cc):
    # just checking
    #print(np.dot(np.cross(aa,bb), cc))
    #print(np.dot(np.cross(bb,cc), aa))
    #print(np.dot(np.cross(aa,cc), bb))
    return np.dot(np.cross(aa,bb), cc)
def AngleVectors(aa, bb):
    return np.arccos(np.dot(aa, bb)/(np.linalg.norm(aa)*np.linalg.norm(bb)))

VectorNames = ['a','b','c']
VectorPairs = [(0,1),(0,2),(1,2)] # There is probably a better way but, blehh
#### Vector lengths
_txt='    Vector lengths   '
for j, i in enumerate(VectorNames):
    _txt += str(i)+' : '
    print(_txt.rjust(33), end='')
    print("{:.4f}".format(np.linalg.norm(CellBox[j])).rjust(18)+ ' A' )
    _txt=''
#### Areas
_txt='    Area between vectors '
for i, j in VectorPairs:
    _txt += str(VectorNames[i])+','+str(VectorNames[j])+' : '
    print(_txt.rjust(33), end='')
    print("{:.4f}".format(AreaVectors(CellBox[i], CellBox[j])).rjust(18)+ ' A2' )
    _txt=''
#### Molecular Surface Densities 
_txt=' Molecular Surf. Densities '
for i, j in VectorPairs:
    _txt += str(VectorNames[i])+','+str(VectorNames[j])+' : '
    print(_txt.rjust(33), end='')
    print("{:.4f}".format(1/AreaVectors(CellBox[i], CellBox[j])).rjust(8)+ '(x1)', end = '' )
    print("{:.4f}".format(2/AreaVectors(CellBox[i], CellBox[j])).rjust(8)+ '(x2)', end = '' )
    print("{:.4f}".format(3/AreaVectors(CellBox[i], CellBox[j])).rjust(8)+ '(x3)', end = '' )
    print(" 1/A2")

    _txt=''

#### Angles
_txt='     Angle between vectors '
for i, j in VectorPairs:
    _txt += str(VectorNames[i])+','+str(VectorNames[j])+' : '
    print(_txt.rjust(33), end='')
    _ang = AngleVectors(CellBox[i], CellBox[j])
    print("{:.6f}".format(_ang).rjust(9)+ ' rad = ' , end='')
    print("{:.2f}".format(_ang * 360 / (2 * np.pi)).rjust(6)+ '°')
    _txt=''
#### Volume
print('Volume cell'.rjust(30)+' : ' +
      '{:.4f}'.format(VolumeCell(CellBox[0], CellBox[1], CellBox[2])).rjust(18)+ ' A3')
