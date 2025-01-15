#!/usr/bin/env python3

import numpy as  np

def OpenParsePOSCAR(_iFile):
    with open(_iFile, 'r') as f:
        cont = f.readlines()
    Factor = float(cont[1])
    Cell = np.array([[float(j)*Factor for j in i.split()] for i in cont[2:5]])
    AtNamesNums = cont[5:9]
    NAtoms = sum([int(i) for i in cont[6].split()])

    AtCoordDir = np.array([[float(j) for j in i.split()[:3]] for i in cont[9:9+NAtoms]])
    AtSelDyn = np.array([[j for j in i.split()[3:]] for i in cont[9:9+NAtoms]])
    AtCoordCart = np.array([np.dot(Cell.T, i) for i in AtCoordDir])
    Tail = cont[9+NAtoms+1:]

    return Cell, AtNamesNums, NAtoms, AtCoordDir, AtSelDyn, AtCoordCart, Tail

print("  This tool applies a vector displacement to all coordinates in a POSCAR file")
FileName = input("  > Filename (def=POSCAR) : ") or "POSCAR"

Cell, AtNamesNums, NAtoms, AtCoordDir, AtSelDyn, AtCoordCart, Tail = OpenParsePOSCAR(FileName)
_VectorDispl = input("  > Displacement vector to add (format: 0. 0. 0.) : ") or "0. 0. 0."
VectorDispl = np.array([float(_VectorDispl.split()[i]) for i in range(3)])
print(f'  >> Displ: '+' '.join(['{:.4f}'.format(i) for i in VectorDispl]))

_VectorScale = input("  > Scalling vector (format: 1. 1. 1.) : ") or "1. 1. 1."
VectorScale = np.array([float(eval(_VectorScale.split()[i])) for i in range(3)])
print(f'  >> Scale: '+' '.join(['{:.4f}'.format(i) for i in VectorScale]))

#### ---- Applying transformation
AtCoordDir += VectorDispl
AtCoordDir = AtCoordDir * VectorScale 

#### ---- Writting
FileOut = input("  > Output filename (def:"+FileName+"_disp) : ") or FileName + "_disp"
with open(FileOut, 'w') as f:
    f.write(" Displaced "+FileName+" \n   1.00000000000000  \n")
    [f.write("  "+" ".join(["{:.16f}".format(j).rjust(21) for j in i]) + "\n") for i in Cell]
    [f.write(i) for i in AtNamesNums]
    [f.write(" " + " ".join(["{:.16f}".format(k).rjust(19) for k in AtCoordDir[i]]) +
             "  " + "  ".join([str(j).rjust(2) for j in AtSelDyn[i]]) +
             "\n") for i in range(NAtoms)]
    f.write("\n")
    [f.write(i) for i in Tail]
    f.write("\n")
