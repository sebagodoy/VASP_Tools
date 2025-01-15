#!/usr/bin/env python3

import numpy as  np

def OpenParsePOSCAR(_iFile):
    with open(_iFile, 'r') as f:
        cont = f.readlines()
    Factor = float(cont[1])
    Cell = np.array([[float(j)*Factor for j in i.split()] for i in cont[2:5]])
    AtNamesNums = cont[5:9]
    NAtoms = sum([int(i) for i in cont[6].split()])

    AtomNameList = []
    for i,j in enumerate(AtNamesNums[1].split()):
        [AtomNameList.append(AtNamesNums[0].split()[i]) for k in range(int(j))]
    CoordSystem = cont[8]

    AtCoordDir = np.array([[float(j) for j in i.split()[:3]] for i in cont[9:9+NAtoms]])
    AtSelDyn = np.array([[j for j in i.split()[3:]] for i in cont[9:9+NAtoms]])
    AtCoordCart = np.array([np.dot(Cell.T, i) for i in AtCoordDir])
    Tail = cont[9+NAtoms+1:]

    return Cell, AtomNameList, NAtoms, CoordSystem, AtCoordDir, AtSelDyn, AtCoordCart, Tail

print("  This tool purges a POSCAR type file, selecting atoms to keept or eliminate")
FileName = input("  > Filename (def=POSCAR) : ") or "POSCAR"

Cell, AtomNameList, _, CoordSystem, AtCoordDir, AtSelDyn, _, Tail = OpenParsePOSCAR(FileName)

#### ---- remove or preserve
qWhatToDo = input("  > Want to eliminate (def:e) some or only preserve (p) some : ")
if qWhatToDo not in ["p", "e"]: qWhatToDo = "e"

whichFocus = input("  > Which ones (atom index, eg: 1 3 5 or 3 - 12, not both ) : ")
if "-" in whichFocus:
    selAtomList = [i for i in range(int(whichFocus.split("-")[0])-1, int(whichFocus.split("-")[1]))]
else:
    selAtomList = [int(i) -1 for i in whichFocus.split()]


if qWhatToDo == "p":
    print("  > Eliminating every other atom")
    AtomNameList = np.array([j for i,j in enumerate(AtomNameList) if i in selAtomList])
    AtSelDyn = np.array([j for i,j in enumerate(AtSelDyn) if i in selAtomList])
    AtCoordDir = np.array([j for i,j in enumerate(AtCoordDir) if i in selAtomList])
elif qWhatToDo == "e":
    print("  > Preserving every other atom")
    AtomNameList = np.array([j for i, j in enumerate(AtomNameList) if i not in selAtomList])
    AtSelDyn = np.array([j for i, j in enumerate(AtSelDyn) if i not in selAtomList])
    AtCoordDir = np.array([j for i, j in enumerate(AtCoordDir) if i not in selAtomList])



#### ---- Writting
print("  > Writting POSCAR, tail will not be considered")
FileOut = input("  > Output filename (def:"+FileName+"_purg) : ") or FileName + "_purg"
with open(FileOut, 'w') as f:
    f.write(" Purged "+FileName+" ("+qWhatToDo+":"+whichFocus+") \n   1.00000000000000  \n")
    [f.write("  "+" ".join(["{:.16f}".format(j).rjust(21) for j in i]) + "\n") for i in Cell]

    outAtomTypes = list(dict.fromkeys(AtomNameList))
    f.write(" ".join([str(i+" ").rjust(5) for i in outAtomTypes]) + "\n")
    for iType in outAtomTypes:
        _counter = 0
        for _iAt in AtomNameList:
            if _iAt == iType:
                _counter += 1
        f.write(str(_counter).rjust(6))
    f.write("\nSelective dynamics\n")
    f.write(CoordSystem)

    [f.write(" " + " ".join(["{:.16f}".format(k).rjust(19) for k in AtCoordDir[i]]) +
             "  " + "  ".join([str(j).rjust(2) for j in AtSelDyn[i]]) +
             "\n") for i in range(len(AtSelDyn))]
    f.write("\n")
    [f.write(i) for i in Tail]
    f.write("\n")
