#!/usr/bin/env python3

# This script writes a csv file (that can be openes with excel or libreoffice-calc) with the
# inter-atomic distances

# Author: SGG (sebagodoy@udec.cl)
# Version: 1.0 (19, feb, 2024)

import numpy as np
import csv

def OpenParsePOSCAR(_iFile):
    with open(_iFile, 'r') as f:
        cont = f.readlines()
    Factor = float(cont[1])
    Cell = np.array([[float(j)*Factor for j in i.split()] for i in cont[2:5]])
    NAtoms = sum([int(i) for i in cont[6].split()])

    AtNamesNums = cont[5:9]
    AtomNameList = []
    for i,j in enumerate(AtNamesNums[1].split()):
        [AtomNameList.append(AtNamesNums[0].split()[i]) for k in range(int(j))]
    CoordSystem = cont[8]

    AtCoordDir = np.array([[float(j) for j in i.split()[:3]] for i in cont[9:9+NAtoms]])
    AtSelDyn = np.array([[j for j in i.split()[3:]] for i in cont[9:9+NAtoms]])
    AtCoordCart = np.array([np.dot(Cell.T, i) for i in AtCoordDir])
    Tail = cont[9+NAtoms+1:]

    return Cell, AtomNameList, NAtoms, CoordSystem, AtCoordDir, AtSelDyn, AtCoordCart, Tail

def GetDistanceMatrix(_AtCoords):
    # input coordinates in cartesian
    _NAtoms = len(_AtCoords)
    _DistMat = [[0 for _ in range(_NAtoms)] for _ in range(_NAtoms)]
    for xAt in range(_NAtoms):
        for yAt in range(_NAtoms):
            _DistMat[xAt][yAt] = np.linalg.norm(_AtCoords[xAt] - _AtCoords[yAt])
            _DistMat[yAt][xAt] = _DistMat[xAt][yAt]
    return _DistMat

def GetNeighbours(_DistMat, _disAtAt, _tol=15):
    # return _CN: list of coordination numbers for each atom and
    # _Neigh that is the list of lists of neightbours for each atom
    _CN = []; _Neigh = []
    for iAtRow in _DistMat:
        iCounter = 0; iNeig=[]
        for jAtIndex, jdist in enumerate(iAtRow):
            if _disAtAt * ( 1 - _tol/100 ) < jdist < _disAtAt * ( 1 + _tol/100 ):
                iCounter += 1
                iNeig.append(jAtIndex)
        _CN.append(iCounter)
        _Neigh.append(iNeig)
    return _CN, _Neigh

print("  This tool produces a csv file with the inter-atomic distances.\n"
      "The csv file can be opened as text, using Microsoft-excel or libreoffice-calc\n")

#### ---- Opening and parsing
FileName = input("  > Filename (def=POSCAR) : ") or "POSCAR"
Cell, _, NAtoms, _, _, _, NPatCoordCart, _ = OpenParsePOSCAR(FileName)
DistMat = GetDistanceMatrix(NPatCoordCart)
CNlist, _ = GetNeighbours(DistMat, 2.462)

#### ---- Writting
print("  > Writting obj file")
strName = FileName + "_distances.csv"
with open(strName, 'w') as f:
    csvwritter = csv.writer(f)
    csvwritter.writerow(["\\"]+["#"+str(i+1) for i in range(NAtoms)])
    csvwritter.writerows([["#"+str(idx+1)] + row for idx, row in enumerate(DistMat)])
