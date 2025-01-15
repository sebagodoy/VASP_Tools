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

print("  This tool transforms a POSCAR coord. direct w/Selective dynamics to Cartesian")
FileName = input("  > Filename (def=POSCAR) : ") or "POSCAR"

Cell, AtNamesNums, NAtoms, AtCoordDir, AtSelDyn, AtCoordCart, Tail = OpenParsePOSCAR(FileName)

#### ---- Writting
FileOut = input("  > Output filename (def:"+FileName+"_cart) : ") or FileName + "_cart"
with open(FileOut, 'w') as f:
    f.write(" Direct to Cartesian of "+FileName+" \n   1.00000000000000  \n")
    [f.write("  "+" ".join(["{:.16f}".format(j).rjust(21) for j in i]) + "\n") for i in Cell]
    [f.write(i) for i in AtNamesNums[:-1]]
    f.write("Cartesian\n")
    [f.write(" " + " ".join(["{:.16f}".format(k).rjust(19) for k in AtCoordCart[i]]) +
             "  " + "  ".join([str(j).rjust(2) for j in AtSelDyn[i]]) +
             "\n") for i in range(NAtoms)]
    f.write("\n")
    [f.write(i) for i in Tail]
    f.write("\n")
