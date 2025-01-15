#!/usr/bin/env python3

################################################################
################################ V.0

import matplotlib.pyplot as plt

def CodeStatus(inStr, **kwargs): print(' '*kwargs.get('l',4) + '> '+ inStr, end=kwargs.get('end','\n'))
def CodeError(inStr, **kwargs): print(' '*kwargs.get('l',2) + 'Error: >>>> '+ inStr)

def FolderFormat(iNum):
	return '{:02d}'.format(iNum)

def FixNumBlanck(ifloat, **kwargs):
	dec = '{:.'+str(kwargs.get('d',4))+'f}'
	length = kwargs.get('l', 10)
	strout = dec.format(ifloat)
	if len(strout)<length: strout = ' '*(length-len(strout))+strout
	return strout

def FixBlanck(iStr, **kwargs):
	length = kwargs.get('l', 10)
	strout = iStr
	if len(strout)<length: strout = ' '*(length-len(strout))+strout
	return strout

########################################################################################################################
########################################################################################################################

print(' '*4+'Checking progress of relaxation')

FileName = input(' '*4+'>> Filename of forces   (def=OUTCAR)    : ') or "OUTCAR"
POSName =  input(' '*4+'>> Filename of geometry (def=CONTCAR)   : ') or "CONTCAR"

#### -------------------------------------------------------------------------------------------------------------------
# POSCAR file is used to get the number of atoms and check which atom
# coordinates are free to be relaxed.
try:
	with open(POSName, 'r') as f:
		POSCAR = f.readlines()
	# Get atom numbers
	NAtoms = sum([int(i) for i in POSCAR[6].split()])
	# Get which coordinates are to be relaxed (True)
	def FreeCoord(i):
		if i == "F":
			return False
		elif i == "T":
			return True
		else:
			raise TypeError()
	RelaxCoord=[[FreeCoord(k) for k in iLine.split()[3:]] for iLine in POSCAR[9:9+NAtoms]]
	# TODO: THIS DOES NOT DETECT WHEN SELECTIVE DYNAMICS IS NOT CONSIDERED, IT JUMPS THE FIRST
	# TODO: ATOM AND RelaxCoord IS LIST OF EMPTY LISTS.
	CodeStatus("Found "+str(NAtoms)+" atoms and their degrees of freedom from "+POSName)
	#Debug: print("RelaxCoord")
	#Debug: [print(k) for k in RelaxCoord]
except:
	raise TypeError("Somethig went wrong when reading the "+POSName+" file as a full vasp-POSCAR format!")
# Got RelaxCoord = [ [False, False, False] , ... , [True, True, True]] as activated relaxation list
# per atom and coordinate


#### -------------------------------------------------------------------------------------------------------------------
# OUTCAR file is from the forces in every step are read

# Collectors
StepCounter = -1
StepDict = {0:[]}
RelaxConverg = False

#### Opening file
with open(FileName, 'r') as f:
		OUTCAR = f.readlines()

#### Confirm Atom Number
NAtoms2 = 0; _counter=10; _found_line=0;
while True:
	if "position of ions in" in OUTCAR[_counter]:
		_found_line+=1
		_counter+=1

	if _found_line == 1:
		if len(OUTCAR[_counter].split())==3:
			NAtoms2+=1
			#print(_counter)
		else:
			_found_line+=1

	if _found_line==2:
		break
	_counter += 1

#### Conv Forces
EDIFFG = False; _counter=10
while not EDIFFG:
	if "EDIFFG" in OUTCAR[_counter]:
		EDIFFG = float(OUTCAR[_counter].split()[2])
		if EDIFFG <0:
			_tx="{:.3}".format(EDIFFG)+"eV/A (max force coord.)"
		else:
			_tx = "{:.8}".format(EDIFFG) + "eV (max E change between steps)"
		CodeStatus("Got required convergence: "+_tx)
	else:
		_counter +=1

#### Consistency POSCAR-OUTCAR
CodeStatus("Found "+str(NAtoms2)+" atoms in "+FileName+" that\'s ", end="")
if NAtoms == NAtoms2:
	print("good")
else:
	print("not good.")
	raise TypeError("The "+POSName+"(POSCAR format) and "+FileName+" (OUTCAR format) do not coincide")


# Quick extract of forces
import subprocess
ForcesExtracted = subprocess.check_output("grep TOTAL "+FileName+" -A "+ str(NAtoms + 4) , shell=True, text=True).split('\n')
OUTCAR = ForcesExtracted

#### Getting data points
_i = 0
while _i < len(OUTCAR):
	iLine = OUTCAR[_i]
	# Encounter a force block
	if "TOTAL-FORCE (eV/Angst)" in iLine:
		StepCounter += 1; _i += 2

		# All the force block
		_ForceRaw = [[float(_j) for _j in kline.split()[3:]] for kline in OUTCAR[_i:_i+NAtoms]]
		# Frozen coordinates are zero in this one
		_ForceFree = [[ii*jj for ii, jj in zip(iii, jjj)] for iii, jjj in zip(_ForceRaw, RelaxCoord)]

		# Atom Force magnitude (all atoms)
		_ForceMagRaw = [(k[0] ** 2 + k[1] ** 2 + k[2] ** 2) ** (.5) for k in _ForceRaw]
		# Atom Force magnitude (Free coordinates)
		_ForceMagFree = [(k[0] ** 2 + k[1] ** 2 + k[2] ** 2) ** (.5) for k in _ForceFree]

		# Max forces coordinates (free coordinates)
		# maximum force (_MaxForceCoordFree, signed) in a coordinate for an atom (_MaxForceCoordFree_AtomN, index + 1)
		_MaxForceCoordFree = 0
		for _AtomMax, _iAtomMax in enumerate(_ForceFree):
			for _iCoordMax in _iAtomMax:
				if abs(_iCoordMax) > abs(_MaxForceCoordFree):
					_MaxForceCoordFree = _iCoordMax
					_MaxForceCoordFree_AtomN = _AtomMax + 1

		# Max force magnitude (free coordinates)
		# maximum force magnitude (_MaxForceMagFree, magnitude:+) and its atom (_MaxForceMagFree_AtomN, index + 1)
		_MaxForceMagFree = 0
		for _iAtomMag, _AtomMag in enumerate(_ForceMagFree):
			if abs(_AtomMag) > abs(_MaxForceMagFree):
					_MaxForceMagFree = _AtomMag
					_MaxForceMagFree_AtomN = _iAtomMag + 1

		## Compile and add to almanac dictionary
		StepDict[StepCounter] = {"Forces": _ForceRaw, # [atom [coords] ] force block (all)
								 "FreeForces":_ForceFree, # [atom [coords] ] force block (Free degrees of freedom, DoF)
								 "Magnitudes":_ForceMagRaw, # [force magnitude] all force block
								 "FreeMagnitudes":_ForceMagFree, # [force magnitude] all force block
								 "Max-ForceCoordinate":_MaxForceCoordFree, # Max force in coordinate (free DoF)
								 "Max-ForceCoordinate-Atom":_MaxForceCoordFree_AtomN,
								 "Max-ForceMagnitude":_MaxForceMagFree, # Max force magnitude (free DoF)
								 "Max-ForceMagnitude-Atom": _MaxForceCoordFree_AtomN,
								 }
		#Debug: print("="*90)
		#Debug: [print(k) for k in _StepForceRaw]
		#Debug: print("." * 90)
		#Debug: [print(k) for k in _ForceFree]
		#Debug: print("Max Step Force: "+str(_MaxForceCoordFree)+", in atom #"+str(_MaxForceCoordFree_AtomN))

		# Move counter over the atomic block
		_i += NAtoms

	if "reached required accuracy - stopping structural energy minimisation" in iLine:
		RelaxConverg = True
		break

	# next line
	_i += 1

CodeStatus('Found '+str(list(StepDict.keys())[-1] + 1)+'steps with force information')


#### -------------------------------------------------------------------------------------------------------------------
#### Plotting questions
print(' '*4+'> Options parsed to plot :')
print(" " * 8 + '------------------------------------ by coordinate ------- ')
print(" " * 8 + '(1) Forces -all coords. ; (2) Forces      -Deg. of Freedom ')
print(" " * 8 + '(3) F. Mag -all coords. ; (4) F. Mag.     -Deg. of Freedom ')
print(" " * 8 + ' ----------------------------------- --------------------- ')
print(" " * 8 + '                          (5) Max Force   -Deg. of Freedom ')
print(" " * 8 + '                          (6) Max F. Mag. -Deg. of Freedom ')
print(" " * 8 + ' ----------------------------------- selecting atoms ----- ')
print(" " * 8 + '(8) Total force per atom  (9) Force per atom coordinates   ')

print(" " * 8 + '**only 4, 5, 3, 8 programed for now, others maybe latter')

PlotThese = input(' '*4+'>> Plot (default = 5) : ') or "5"

#### Create
fig, ax = plt.subplots(1,1, figsize=(6.5,4.), dpi=80)
plt.subplots_adjust(right=.95, top=.97, bottom=.12)
#ax.set_position([.15, .12, .8, .85])

if PlotThese in ['8', '9']:
	WhichAtom = input(' '*4+'>> Which atoms? (def: 1 2) : ') or '1 2'
	# parse
	try:
		if WhichAtom == "0":
			WhichAtom = [i+1 for i in range(NAtoms2)]
		else:
			_ParseAtomList = WhichAtom.split()
			_AtomList = []
			while '-' in _ParseAtomList:
				_idx = _ParseAtomList.index('-')
				_range = [int(_ParseAtomList[_idx-1]), int(_ParseAtomList[_idx + 1])]
				_AtomList += [_k for _k in range(min(_range), max(_range) + 1 )]
				_ParseAtomList = _ParseAtomList[:_idx-1] + _ParseAtomList[_idx+2:]
			for i in _ParseAtomList:
				if int(i) not in _AtomList:
					_AtomList.append(int(i))

			_AtomList.sort() # sort
			WhichAtom = list(dict.fromkeys(_AtomList)) # remove duplicates
	except:
		raise NameError(" Something went wrong while parsing the atom list")

	# check in range
	for _iAt in WhichAtom:
		if _iAt > NAtoms:
			raise TypeError("Asked for an atom that is not in the POSCAR/OUTCAR list")

	if PlotThese == '8':
		# extract to create dictionary
		_PlotList = {_iAt: [] for _iAt in WhichAtom}
		for _iDic in list(StepDict.keys()):
			for _jAtom in WhichAtom:
				_PlotList[_jAtom].append(StepDict[_iDic]["Magnitudes"][_jAtom-1])

	elif PlotThese == '9':
		# extract to create dictionary
		WhichAtomXYZ = [str(i)+j for i in WhichAtom for j in ['x', 'y', 'z']]
		_PlotList = {_iAt: [] for _iAt in WhichAtomXYZ}
		for _iDic in list(StepDict.keys()):
			for _jAtom in WhichAtom:
				for _kAxis, _kName in enumerate(['x','y','z']):
					_PlotList[str(_jAtom)+_kName].append(StepDict[_iDic]["Forces"][_jAtom-1][_kAxis])

	# Add atom name left?
	_qry = input(' '*4 + ">> Add index (False/*)") or "y"
	if _qry == "False":
		_qry = False


	# Add to plot
	PlotCount = 0
	for _kAtom in list(_PlotList.keys()):
		PlotCount += 1
		ax.plot([i + 1 for i in list(StepDict.keys())],
				_PlotList[_kAtom],
				marker='+', markeredgecolor='k', linewidth=1.1, label=str(_kAtom))
		if _qry:
			plt.annotate(str(_kAtom),
						 xy = (.99, _PlotList[_kAtom][-1]), xycoords = ('figure fraction', 'data'),
						 fontsize='small', ha='right', va='center')

	_ncols = max(int((PlotCount) ** .5), 1)

	if not input(" "*4 + ">> Hide legend ? ") or False:
		leg = plt.legend(ncols=_ncols)
		for line in leg.get_lines():
			line.set_linewidth(3)
		leg.set_draggable(True)
	



# Maximum force in any coordinate
if "3" in PlotThese:
	CodeStatus(" Plotting Maximum of force coordinates in atoms per step")
	ax.plot([i+1 for i in list(StepDict.keys())],
			[StepDict[i]["Max-ForceCoordinate"] for i in list(StepDict.keys())],
			marker='+', markeredgecolor='k', linewidth=.5, label='Max. F. by coord')
	if input(" "*4+">> Add atom number for plot-option(4) (def=true): ") or True:
		for iStep in range(len(list(StepDict.keys()))):
			plt.annotate(str(StepDict[iStep]["Max-ForceCoordinate-Atom"]),
						 (iStep+1, StepDict[iStep]["Max-ForceCoordinate"]))

# Maximum force magntude
if "5" in PlotThese:
	CodeStatus(" Plotting Maximum of force magnitude in atoms (DOF only) per step")
	ax.plot([i+1 for i in list(StepDict.keys())],
			[StepDict[i]["Max-ForceMagnitude"] for i in list(StepDict.keys())],
			marker='+', markeredgecolor='k', linewidth=.5, label='Max. F. by coord')
	if input(" "*4+">> Add atom number for plot-option(5) (def=true): ") or True:
		for iStep in range(len(list(StepDict.keys()))):
			plt.annotate(str(StepDict[iStep]["Max-ForceMagnitude-Atom"]),
						 (iStep+1, StepDict[iStep]["Max-ForceMagnitude"]))

# Force magnitude, all atoms
if "4" in PlotThese:
	CodeStatus(" Plotting force magnitude in all atoms per step")
	ax.plot([i+1 for i in list(StepDict.keys())],
			[StepDict[i]["FreeMagnitudes"] for i in list(StepDict.keys())],
			marker='+', markeredgecolor='k', linewidth=.5, label='Max. F. by coord')
	if input(" "*4+">> Add atom number for plot-option(5) (def=true): ") or True:
		for iStep in range(len(list(StepDict.keys()))):
			plt.annotate(str(StepDict[iStep]["FreeMagnitudes"]),
						 (iStep+1, StepDict[iStep]["FreeMagnitudes"]))

#### Limit
if EDIFFG < 0:
	ax.axhline(-EDIFFG, color='r', linewidth=.5, linestyle='--')
	plt.annotate(str(-EDIFFG),(.02, -EDIFFG),
				 xycoords=('axes fraction', 'data'),ha='left', va='top', color='r')
	if PlotThese in ["3", "9"]:
		ax.axhline(EDIFFG, color='r', linewidth=.5, linestyle='--')
		plt.annotate(str(EDIFFG),(.02, EDIFFG),
					 xycoords=('axes fraction', 'data'),ha='left', va='bottom', color='r')
		ax.axhspan(EDIFFG, -EDIFFG, color='g', alpha=.2, zorder=0)
	else:
		ax.axhspan(-EDIFFG, 0., color='g', alpha=.2, zorder=0)


	plt.axhline(y=0, linewidth=.5, color='k', zorder=1)


# Title
if RelaxConverg:
	ax.set_title('Relaxation\nconverged', x=.95, y=.95, ha='right', va='top')
	ax.plot([i+1 for i in list(StepDict.keys())][-1],
			[StepDict[i]["Max-ForceMagnitude"] for i in list(StepDict.keys())][-1],
			marker='o',  markerfacecolor='none', markeredgecolor='g', markersize=8)
else:
	ax.set_title('Relaxation\nnot converged', x=.95, y=.95, ha='right', va='top')

# nice
ax.grid(which='both', linewidth=.5)

plt.xlabel('Iteration')
plt.ylabel('Force , eV/A')



plt.show()
