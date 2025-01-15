#!/usr/bin/env python3
from collections import Counter

# Version 0.1
import numpy as np

import os
import subprocess

#### Source filelist
FileList = []
FileAdd = input("  >> Add frequency calculation directory : ") or "."
while FileAdd:
    if os.path.isfile(FileAdd+"/POSCAR") and os.path.isfile(FileAdd+"/OUTCAR"):
        FileList.append(FileAdd)
    else:
        print(" That is not a directory containing a POSCAR and OUTCAR files")
        print(f"  (!!) Checked ,{FileAdd}/POSCAR")
        print(f"  (!!) Checked ,{FileAdd}/OUTCAR")
    FileAdd = input("  >> Add frequency calculation directory : ")


# Compare number of atoms
ComparativeDic = {"NAtoms":[], "AtomTypes":[], "AtomGroups":[]}

#### Get
print("-"*40+"\n Comparing POSCAR files:")
for iFolder in FileList:
    iPOSCAR = iFolder+"/POSCAR"

    try:
        with open(iPOSCAR, 'r') as f:
            POSCAR = f.readlines()
        NAtoms = sum([int(i) for i in POSCAR[6].split()]) # total number of atoms
        AtomTypes = POSCAR[5].split() # types of atoms
        AtomGroups = POSCAR[6].split() # number of atoms per type
        # Add to comparative dictionary
        ComparativeDic["NAtoms"].append(NAtoms)
        ComparativeDic["AtomTypes"].append(AtomTypes)
        ComparativeDic["AtomGroups"].append(AtomGroups)
        _ = ",".join(AtomTypes)
        print(f" >> Found POSCAR with {NAtoms} atoms ({_}) in {iPOSCAR}")
    except:
        raise TypeError("Somethig went wrong when reading the " + iPOSCAR + " file as a full vasp-POSCAR format!")

#### Check POSCAR compatibility
if all(i == ComparativeDic["NAtoms"][0] for i in ComparativeDic["NAtoms"]) and \
    all(i == ComparativeDic["AtomTypes"][0] for i in ComparativeDic["AtomTypes"]) and \
    all(i == ComparativeDic["AtomGroups"][0] for i in ComparativeDic["AtomGroups"]):
    print(" (*) Number and type of atoms coincides in all POSCAR files")
else:
    raise TypeError("The number and tipe of atoms is not the same on all the requested folders !!! Check manually.")

#### Get
# Almanaq of all calculations
Almanaq = {}
# Architeqture: Almanaq[directory][step][E0 / PosBlock / ForceBlock]

print("-"*40+"\n Parsing OUTCAR files:")
for iFolder in FileList:
    # Open OUTCAR
    iOUTCAR = iFolder+"/OUTCAR"
    with open(iOUTCAR, 'r') as f:
        OUTCAR = f.readlines()

    # Confirm number of atoms in OUTCAR
    NAtoms2 = 0; _counter = 10; _found_line = 0;
    while True:
        if "position of ions in cartesian coordinates" in OUTCAR[_counter]:
            _found_line += 1
            _counter += 1
        if _found_line == 1:
            if len(OUTCAR[_counter].split()) == 3:
                NAtoms2 += 1
            else:
                _found_line += 1
        if _found_line == 2:
            break
        _counter += 1

    # report coincidence of NAtoms
    print(" >> Found " + str(NAtoms2) + " atoms in " + iOUTCAR + " that\'s ", end="")
    if NAtoms == NAtoms2:
        print("good")
    else:
        print("not good.")
        raise TypeError("The POSCAR's and " + iOUTCAR + " (OUTCAR format) number of atoms do not coincide")

    # Quick extract of positions, forces and energies
    ExtractOUTCAR = subprocess.check_output("grep TOTAL " + iOUTCAR + " -A " + str(NAtoms + 15), shell=True,
                                            text=True).split('\n')

    # Parse positions and forces
    _step = -1;  _subAlmanaq = {}; _i = 0 # line reading
    while _i < len(ExtractOUTCAR):
        iLine = ExtractOUTCAR[_i]
        # print(f"Checking : {ExtractOUTCAR[_i]}")
        # Encounter a force block
        if "TOTAL-FORCE (eV/Angst)" in iLine:
            # print("Got one")
            _step += 1; _i += 2
            _Forces = [[float(_j) for _j in kline.split()[3:]] for kline in ExtractOUTCAR[_i:_i + NAtoms]]
            _Positions = [[float(_j) for _j in kline.split()[:3]] for kline in ExtractOUTCAR[_i:_i + NAtoms]]
            _TOTEN = float(ExtractOUTCAR[_i + NAtoms + 10].split()[-2])

            #### Adding to subAlmanac
            _subAlmanaq[_step] = {}
            _subAlmanaq[_step]["PosBlock"] = _Positions
            _subAlmanaq[_step]["ForceBlock"] = _Forces
            _subAlmanaq[_step]["TOTEN"] = _TOTEN
            
            # Continue parsing extracted
            _i += NAtoms

        else: # next line        
            _i += 1
        

    # Report and continue
    print(f" >> Extracted Forces, Positions and energies for {_step} steps (+ initial), added to almanaq")
    #for _i in list(_subAlmanaq.keys()):
    #    print(f"Step {_i}")
    #    print(_subAlmanaq[_i])
    Almanaq[iOUTCAR] = _subAlmanaq


#### Compare initial geometries for all in Almanaq, should be the same
print("-"*40+"\n Checking consistency between directories:")
ComparativeDic["TOTEN_0"] = []
ComparativeDic["Geom_0"] = []
ComparativeDic["Force_0"] = []
for iDir in list(Almanaq.keys()):
    ComparativeDic["TOTEN_0"].append(Almanaq[iDir][0]["TOTEN"])
    ComparativeDic["Geom_0"].append(Almanaq[iDir][0]["PosBlock"])
    ComparativeDic["Force_0"].append(Almanaq[iDir][0]["ForceBlock"])
## Check energy consistence
MaxDifE0 = max([i - j for i in ComparativeDic["TOTEN_0"] for j in ComparativeDic["TOTEN_0"]])
if MaxDifE0 > 1e-7:
    raise TypeError(" (!!) The initial configurations on the directories have very different energies.\n"
                    f" (*) Max diference in initial config energy : {MaxDifE0}"
                    "      These calculations should not be concatenated for frequency.")
else:
    print(f" (*) Max diference in initial config energy : {MaxDifE0} (nice, can continue)")
# Check geometry consistency
if not all([i == ComparativeDic["Geom_0"][0] for i in ComparativeDic["Geom_0"]]):
    raise TypeError(" (!!) The initial geometries in the OUTCAR files are not consistent (prec:1e-5 AA)."
                    "      These should not be considered together for frequency calculations.")
else:
    print(f" (*) Initial geometries in all OUTCAR files are consistent (prec:1e-5 AA). Yay!")

# Check forces consistency
# flaten list of lists (geom or forces)
def flatarange(iList):
    return [x for xs in iList for x in xs]

_ForceDiff = [max([abs(_i - _j) for _i,_j in zip(flatarange(ComparativeDic["Force_0"][0]), flatarange(iFile))])
              for iFile in ComparativeDic["Force_0"]]
# if not all([i == ComparativeDic["Force_0"][0] for i in ComparativeDic["Force_0"]]): # Criteria strict
if max(_ForceDiff) > 1e-5:
    raise TypeError(" (!!) The estimated forces for the initial geometries in the OUTCAR files (prec:1e-6 eV/AA) \n"
                    "      are not consistent. These could indicate different calculation conditions/parameters \n"
                    "      were used, therefore these should not be considered together for frequency calculations.")
else:
    print(f" (*) Estimated forces in the initial geometries in all OUTCAR files \n"
          f"     are consistent (prec:1e-6 eV/AA, max:{'{:.4E}'.format(max(_ForceDiff))}). Yay!")

#### Parse almanaq to displacements
print("-"*40+"\n Consolidating displacements :")
# Separate Initial
TOTEN_0 = ComparativeDic["TOTEN_0"][0]
Geom_0 = flatarange(ComparativeDic["Geom_0"][0])
Forces_0 = flatarange(ComparativeDic["Force_0"][0])

# Almanaq for displacements, compiled from almanaq without the initial points
# format:  AlmanaqDisplacements["atom|XYZ|+/-"] = { "TOTEN": float,
#                                                   "Geom": flat list,
#                                                   "Forces": flat list,
#                                                   "Displ": float (displacement)}
# example: AlmanaqDisplacements["1|X|+"] = {}
# initialized for all posible displacements, so displacements repeated between calculations are overwritten
# this avoids having a + from one and a - from other (if NFREE=2 is used, that's assumed here)
AlmanaqDisplacements = {f"{i+1}|{j}|{k}":{} for i in range(NAtoms) for j in ["X", "Y", "Z"] for k in ["+","-"]}

#### Loop files, loop steps (avoid initial, starting from one), identify displacement and save in AlmanaqDisplacements
# identify displaced DoF
def DoF_identity(_iGeom, _refGeom):
    _CoordDic = {0:"X", 1:"Y", 2:"Z"}

    _GeomDif = [i - j for i, j in zip(_iGeom, _refGeom)]    # list of position differences from reference geom
    _idxDif = np.argmax([abs(i) for i in _GeomDif])         # index of maximum
    _NAtom = int(_idxDif/3)+1                               # displaced-atom number
    _Coord = _CoordDic[_idxDif - (_NAtom - 1)*3]            # displaced coordinate
    _dispdirection = "+" if _GeomDif[_idxDif] > 0. else "-" # direction of displacement

    return {"label":f"{_NAtom}|{_Coord}|{_dispdirection}",  # format "1|X|+" for AlmanaqDisplacements
            "Atom":_NAtom,
            "Coord":_Coord,
            "direction":_dispdirection,
            "displ_idx":_idxDif,
            "displ": _GeomDif[_idxDif]}

for iFile in list(Almanaq.keys()):
    print(f"  >> Parsing {iFile}")
    for iStep in Almanaq[iFile]:
        # avoid the initial step
        if iStep == 0:
            continue
        # Analyze step
        iGeom = flatarange(Almanaq[iFile][iStep]["PosBlock"])
        dispdic = DoF_identity(iGeom, Geom_0)                   # Identified and generated dictionary

        print(f"   >>> Step #{str(iStep).ljust(4)} ({dispdic['label']}): displace atom {dispdic['Atom']},"
              f" {dispdic['Coord']}{dispdic['direction']}"
              f" by {dispdic['displ']} A ")
        # Populate AlmanaqDisplacements
        AlmanaqDisplacements[dispdic['label']] = {"TOTEN": Almanaq[iFile][iStep]["TOTEN"],
                                                  "Geom": Almanaq[iFile][iStep]["PosBlock"],
                                                  "Forces": Almanaq[iFile][iStep]["ForceBlock"],
                                                  "Displ": dispdic['displ']}

# JUST FOR TESTING
# for k in ["1230|X|+", "1230|X|-", "1230|Y|+", "1230|Y|-", "1230|Z|+", "1230|Z|-"]:
#     AlmanaqDisplacements[k]={}
# AlmanaqDisplacements["1240|X|+"]={1:1}
# AlmanaqDisplacements["1240|X|-"]={}
# AlmanaqDisplacements["1250|X|+"]={}
# AlmanaqDisplacements["1250|X|-"]={1:1}
#for iTag in list(AlmanaqDisplacements.keys()):
#    print(f"{iTag} : {str(AlmanaqDisplacements[iTag])}")
#print("-"*80)

#### clean AlmanaqDisplacements
# remove empty dictionaries
for iTag in list(AlmanaqDisplacements.keys()):
    if AlmanaqDisplacements[iTag] == {}:
        del AlmanaqDisplacements[iTag]
# remove entries that are not paired +/- (after deleting all empty)
PairDirectionDic = {'+':'-', '-':'+'}
for iTag in list(AlmanaqDisplacements.keys()):
    if not iTag[:-1]+PairDirectionDic[iTag[-1]] in AlmanaqDisplacements.keys():
        del AlmanaqDisplacements[iTag]

# for iTag in list(AlmanaqDisplacements.keys()):
#     print(f"{iTag} : {str(AlmanaqDisplacements[iTag])}")

#Report
_AlmanaqReport = {i.split("|")[0]:{} for i in list(AlmanaqDisplacements.keys())}
for i in list(AlmanaqDisplacements.keys()):
    _AlmanaqReport[i.split("|")[0]][i.split("|")[1]] = 0
_txt = "|".join([i + "("+",".join([j for j in list(_AlmanaqReport[i].keys())])+")"
                  for i in list(_AlmanaqReport.keys())])
_txt2 = ""
_txt3 = f" (*) Complete list of degrees of freedom compiled: {_txt.split('|')[0]}"
for i in _txt.split('|')[1:]:
    if len(_txt3) + len(i) > 80:
        _txt2 += _txt3 + ",\n"
        _txt3 = "      "+i
    else:
        _txt3 += ", "+i
print(_txt2 + _txt3)

# Check displaced distances are the same (with tolerance)
_prec = 1e-5
ComparativeDic["Displacements"] = [abs(AlmanaqDisplacements[iTag]['Displ'])
                                   for iTag in list(AlmanaqDisplacements.keys())]
Displ_0 = float("{:.5f}".format( sum(ComparativeDic["Displacements"])/len(ComparativeDic["Displacements"]) ) )
if not all([abs(i - Displ_0) <_prec  for i in ComparativeDic["Displacements"]]):
    raise TypeError(f" (!!) Not all displacements are equal (prec:{str(_prec)}), average {Displ_0}, results "
                    "     could still be used but a different displacement should be used in each "
                    "     degree of freedom, which I have not programed yet.")
else:
    print(f" (*) All displacements are the same: {Displ_0} (prec:1e-5 AA). Yay!")

#### Construct new Hessian from forces
print("-"*40+"\n Constructing Hessian Matrix :")
# Number of Degrees of Freedom
nDoF = len(AlmanaqDisplacements)/2
if not nDoF == int(nDoF):
    raise TypeError(f" (!!) The number of available calculations should be par, but it is {len(AlmanaqDisplacements)}, "
                    f"      somethins is strange")
else:
    nDoF = int(nDoF)

# Create Hessian
DoF_names = [i[:-2] for i in list(AlmanaqDisplacements.keys()) if i[-1] == "+"]
HessianRaw = np.zeros((int(len(AlmanaqDisplacements)/2), int(len(AlmanaqDisplacements)/2)), dtype=float)
HessianSymm = np.zeros((int(len(AlmanaqDisplacements)/2), int(len(AlmanaqDisplacements)/2)), dtype=float)
HessianWeight = np.zeros((int(len(AlmanaqDisplacements)/2), int(len(AlmanaqDisplacements)/2)), dtype=float)

DoF2CoordDic = {'X':0, "Y":1, "Z":2}
def DoF_2_indexBlock(iDoF):
    # iDoF = 'Atom number | coordinate (optional: | + / -)'
    _nAtom = int(iDoF.split('|')[0])-1
    _nCoord = DoF2CoordDic[iDoF.split('|')[1]]
    return (_nAtom, _nCoord)

# Populate Hessian
for i, iName in enumerate(DoF_names):
    # hessian row is outer coordinate derivative d/d(i)(... )
    for j, jName in enumerate(DoF_names):
        # hessian column is inner coordinate derivative dE/d(i) = -F(i) force in coordinate i
        # Forces are negative de dE/dq, requires negative at some part to go back to energy field
        #print(iName+";"+jName)
        _atCoord = DoF_2_indexBlock(jName)
        HessianRaw[i][j] += AlmanaqDisplacements[iName+'|+']['Forces'][_atCoord[0]][_atCoord[1]]
        HessianRaw[i][j] -= AlmanaqDisplacements[iName+'|-']['Forces'][_atCoord[0]][_atCoord[1]]
        HessianRaw[i][j] *= (-.5/Displ_0)

def ShowHessian(iHessian):
    [print(str(j).rjust(12).ljust(15), end = "  ") for j in ['']+DoF_names]; print()
    for i, k in zip(iHessian, DoF_names):
        print(k.rjust(12).ljust(15), end="  ")
        [print("{:.6f}".format(j).rjust(12).ljust(15), end = "  ") for j in i]
        print("")

if input(" >> Populated Hessian Matrix (not symmetrized). Show it ? (def:no) : "):
    ShowHessian(HessianRaw)

# Symmetrizing
for i, _HessRow in enumerate(HessianRaw):
    for j, _j in enumerate(_HessRow):
        HessianSymm[i][j] = (HessianRaw[i][j] + HessianRaw[j][i])/2
        #HessianSymm[j][i] = HessianSymm[i][j]

if input(" >> Symmetrized Hessian Matrix.                 Show it ? (def:no) : "):
    ShowHessian(HessianSymm)


#### Mass wighted
print(" >> Checking POTCAR to get atomic masses (should be in the same order as POSCAR!)")
# compare POTCARs to extract masses
ComparativeDic["AtomTypes_POTCAR"] = []
for iFolder in FileList:
    ComparativeDic["AtomTypes_POTCAR"].append(
        [i.split('=')[1].split(':')[0].strip()
         for i in
         subprocess.check_output("grep VRHFIN " + iFolder + "/POTCAR", shell=True, text=True).strip().split('\n')]
    )

if not all([i == ComparativeDic["AtomTypes"][0] for i in ComparativeDic["AtomTypes_POTCAR"]]):
    for k, l in zip(ComparativeDic["AtomTypes"], ComparativeDic["AtomTypes_POTCAR"]):
        print(k)
        print(l)
    raise TypeError(" (!!) Atom types in POTCAR do not coincide with atom types in POSCAR files !!")
else:
    print(" (*) Atom types in POTCAR do coincide with atom types in POSCAR files. Going well!")

# extract masses
AtomMasses = [float(i.split('=')[1].split(';')[0]) for i in
         subprocess.check_output("grep POMASS " + FileList[0] + "/POTCAR", shell=True, text=True).strip().split('\n')]
print(" >> Got atom masses: " + " , ".join([i+":"+str(j) for i,j in zip(ComparativeDic["AtomTypes_POTCAR"][0], AtomMasses)]))

# list of masses for DoF
AllAtomMases = [i for i,j in zip(AtomMasses, ComparativeDic["AtomGroups"][0]) for k in range(int(j))]
DoF_mases = [AllAtomMases[int(i.split("|")[0])-1] for i in DoF_names]

# Mass weighted
for i, _HessRow in enumerate(HessianSymm):
    for j, _j in enumerate(_HessRow):
        HessianWeight[i][j] = HessianSymm[i][j]/DoF_mases[i]
if input(" >> Hessian weighted by row.                    Show it ? (def:no) : "):
    ShowHessian(HessianWeight)

#### Eigenvalues
print("-"*40+"\n Recalculating frequencies :")
print(" >> Computing eigenvalues and eigenvectors")
eigVal, eigVec = np.linalg.eig(HessianWeight)

############ Recalculation of frequencies

eV2J = 1.602176634e-19	# J/eV
Nav = 6.02214076e23		# Part/mol
cc = 299792458 			# m/s
hh			= 6.62606957E-34
def fZPVEi(iFreq):
    return (iFreq * hh * cc * 100) / (eV2J)			# cm1 -> /(eV)

eVal = [k * eV2J * Nav * 1e3 * 1e20 for k in eigVal]	# [1/s^2],

# Linear frequencies [1/s = Hz]
FqReal = [((iVal)**.5)/(2*np.pi) for iVal in eVal if iVal > 0]
FqImg  = [((-iVal)**.5)/(2*np.pi) for iVal in eVal if iVal < 0]

# Order frequencies
FqReal.sort(reverse=True)
FqImg.sort(reverse=True)

# Spectral frequencies [cm-1]
FqRealcm = [iFq/(100*cc) for iFq in FqReal]
FqImgcm  = [iFq/(100*cc) for iFq in FqImg]



print( f" (*) Got {str(len(FqRealcm))} real frequencies and {str(len(FqImgcm))} imaginary frequencies")
# print(f"Real : {' , '.join('{:.4f}'.format(i).rjust(10) for i in FqRealcm)}")
# print(f"Img  : {' , '.join('{:.4f}'.format(i).rjust(10) for i in FqImgcm)}")

def PrintList(_left, _ilist, _width):
    if len(_ilist) == 0:
        return _left + ' (None)'

    _txt = _left + _ilist[0]
    _txtOUT = ''
    for iItem in _ilist[1:]:
        if len(_txt) + len(str(iItem)) > _width:
            _txtOUT += _txt + '\n'
            _txt = ' '*len(_left) + str(iItem)
        else:
            _txt += str(iItem)
    return _txtOUT + _txt

print(PrintList('     Real : ',['{:.4f}'.format(i).rjust(10) for i in FqRealcm], 80))
print(PrintList('     Img  : ',['{:.4f}'.format(i).rjust(10) for i in FqImgcm], 80))

if not bool(input(" >> Write eigenvalues in file (def:no) : ")):
    FileOUT = "Frequencies"
    with open(FileOUT, 'w') as f:
        f.write(" Eigenvectors and eigenvalues of the dynamical matrix\n"
                " ----------------------------------------------------\n \n \n")
        _counter = 0
        for iValTHz, iValcm, iVect in zip(FqReal + FqImg, FqRealcm + FqImgcm, eigVec):
            _counter += 1
            f.write(f"{str(_counter).rjust(5)} f{'/i' if _counter > len(FqRealcm) else '  '}=")
            f.write(f"{'{:.6f}'.format(iValTHz/1e12).rjust(12)} THz ")
            f.write(f"{'{:.6f}'.format(2*np.pi*iValTHz/1e12).rjust(12)} 2PiTHz ")
            f.write(f"{'{:.6f}'.format(iValcm).rjust(11)} cm-1 ")
            f.write(f"{'{:.6f}'.format(fZPVEi(iValcm)*1000).rjust(12)} meV ")

            f.write("\n             X         Y         Z           dx          dy          dz\n")
            _vect = [[0. for _k in range(3)] for _i in range(NAtoms)]
            for k,kName in zip(iVect, DoF_names):
                _ii, _jj = DoF_2_indexBlock(kName)
                _vect[_ii][_jj] = k

            for k, j in zip(_vect, ComparativeDic["Geom_0"][0]):
                f.write(' '*7+' '.join(['{:.6f}'.format(_l).rjust(9) for _l in j]) + ' ')
                f.write(' '+' '.join(['{:.6f}'.format(_l).rjust(11) for _l in k]) + '\n')
            f.write('\n')