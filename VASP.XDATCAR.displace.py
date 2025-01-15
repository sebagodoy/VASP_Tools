#!/usr/bin/env python3

import numpy as  np

def OpenParseXDATCAR(_iFile):
    with open(_iFile, 'r') as f:
        cont = f.readlines()
    Factor = float(cont[1])
    Cell = np.array([[float(j)*Factor for j in i.split()] for i in cont[2:5]])
    AtNamesNums = cont[5:7]
    NAtoms = sum([int(i) for i in cont[6].split()])

    GeomCollection = []
    GeomCounter = 0
    while True:
        try:
            base = GeomCounter*(NAtoms+1)
            cont[8+NAtoms+base] # check final atom of this block, this fails if outside list
            AtCoordDir = np.array([[float(j) for j in i.split()[:3]] for i in cont[(base + 8):(base+8+NAtoms)]])
            GeomCollection.append(AtCoordDir)
            #print(AtCoordDir)
            GeomCounter += 1
            #input("continue : ")
        except:
            break
    print(f"  >> Got {GeomCounter} configurations")
    if GeomCounter == 0:
        raise ImportError
        quit()
    return Cell, AtNamesNums, NAtoms, GeomCollection, GeomCounter


print("  This tool applies a vector displacement and scale to all coordinates in an XDATCAR file")
FileName = input("  > Filename (def=XDATCAR) : ") or "XDATCAR"

Cell, AtNamesNums, NAtoms, GeomCollection, GeomCounter  = OpenParseXDATCAR(FileName)
_VectorDispl = input("  > Displacement vector to add (format: 0. 0. 0.) : ") or "0. 0. 0."
VectorDispl = np.array([float(eval(_VectorDispl.split()[i])) for i in range(3)])
print(f'  >> Displ: '+' '.join(['{:.4f}'.format(i) for i in VectorDispl]))

_VectorScale = input("  > Scalling vector (format: 1. 1. 1.) : ") or "1. 1. 1."
VectorScale = np.array([float(eval(_VectorScale.split()[i])) for i in range(3)])
print(f'  >> Scale: '+' '.join(['{:.4f}'.format(i) for i in VectorScale]))

#### ---- Applying transformations
GeomCollection = [i + VectorDispl for i in GeomCollection]
GeomCollection = [i * VectorScale for i in GeomCollection]

AddTailConfig = input("  > Add tailing additional config ? (for vmd, def False) : ") or False

#### ---- Writting
FileOut = input("  > Output filename (def:"+FileName+"_disp) : ") or FileName + "_disp"
with open(FileOut, 'w') as f:
    f.write(" Displaced "+FileName+" \n   1.0  \n")
    [f.write("  "+" ".join(["{:.6f}".format(j).rjust(11) for j in i]) + "\n") for i in Cell]
    [f.write(i) for i in AtNamesNums]

    for idxConf, iConf in enumerate(GeomCollection):
        f.write("Direct configuration=     "+ str(idxConf+1) + '\n')
        [f.write("  " + " ".join(["{:.8f}".format(k).rjust(11) for k in iConf[i]]) +
                 "\n") for i in range(NAtoms)]
    if AddTailConfig:
        f.write("Direct configuration=     " + str(GeomCounter + 1))
    f.write("\n")
