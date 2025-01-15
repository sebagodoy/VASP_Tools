#!/usr/bin/env python3

################################################################
################################ V.0

import matplotlib.pyplot as plt
import os, re, subprocess

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



################################################################################################################################
################################################################################################################################

print(' '*4+'Checking the progression through multiple runs\n')

#### ---- get folder lists
_FolderList = []; FolderList = []
for iFolder in [iFolder for iFolder in os.listdir('.') if os.path.isdir(iFolder)]:
	# Check previous run folders
	if iFolder in ['Prev_runs','Prev_run']:
		_FolderList.append((-1, iFolder))
	# Omit non/relaxation folders
	elif '_CHG' in iFolder or '_fq' in iFolder or iFolder[0] == '.':
		continue
	# Consider run folders
	elif 'run' in iFolder:
		try:
			_FolderList.append( (int(iFolder[3:].split('_')[0]), iFolder) )
		except:
			try:
				_FolderList.append( (int(iFolder[3:].split('run')[1].split('_')[0]), iFolder) )
			except:
				continue

			continue
	else:
		continue
FolderList = [x for _,x in sorted(_FolderList)]

#### ---- Ask if the folders are Ok, remove folders if requested
print(' Found folders: ', end='')
print(' , '.join(FolderList))
print()
QRemove = input(' > Include these in that order (def=y) : ')
while QRemove:
	removeThis = input('  Remove which one? : ') or ''
	FolderList = [iFolder for iFolder in FolderList if not iFolder == removeThis]
	print(' Ok, new folder list is : ', end='')
	print(' , '.join(FolderList))
	QRemove = input(' > Include these in that order (def=y) :')

#### ---- Gather files to include
print('\n Will gather atomic force blocks for each geometric steps in OUTCAR-type files')
print(' and which degrees of freedom were allowed from the corresponding POSCAR files\n')
FileList = []
GeomList = []
for iDir in FolderList:
	_Filelist = []
	_GeomList = []
	for kFile in os.listdir(iDir):
		if "OUTCAR_" in kFile and "run" in kFile:
			_Filelist.append((int(kFile.split("run")[1]), kFile))
		elif kFile == "OUTCAR":
			_Filelist.append((999, kFile))
		if "POSCAR_" in kFile and "run" in kFile:
			_GeomList.append((int(kFile.split("run")[1]), kFile))
		elif kFile == "POSCAR":
			_GeomList.append((999, kFile))

	_SortedFileList = [x for _, x in sorted(_Filelist)]
	_SortedGeomList = [x for _, x in sorted(_GeomList)]
	for iFile in _SortedFileList:
		if input(' > Include file (*=no / def True) '+iDir+'/'+iFile+' : '):
			print('  ** File not included! continuing')
		else:
			FileList.append(iDir+'/'+iFile)
	for iFile in _SortedGeomList:
		if input(' > Include geom (*=no / def True) '+iDir+'/'+iFile+' : '):
			print('  ** File not included! continuing')
		else:
			GeomList.append(iDir+'/'+iFile)

########################################################################################################################
# Get NAtoms from first geom
print('='*80)
with open(GeomList[0], 'r') as f:
	POSCAR = f.readlines()
NAtoms = sum([int(i) for i in POSCAR[6].split()])
print(f'\n Found {NAtoms} in first POSCAR file.')

#### Plotting questions
print()
print(' '*2+'> Options parsed to plot :')
print(" " * 6 + '------------------------------------ by coordinate ----------- ')
print(" " * 6 + '(1) Forces -all     ; (2) Forces      -active Deg. of Freedom  ')
print(" " * 6 + '(3) F. Mag -all     ; (4) F. Mag.     -active Deg. of Freedom  ')
print(" " * 6 + ' ----------------------------------- ------------------------- ')
print(" " * 6 + '                      (5) Max Force   -active Deg. of Freedom  ')
print(" " * 6 + '                      (6) Max F. Mag. -active Deg. of Freedom  ')
print(" " * 6 + ' ----------------------------------- selecting atoms --------- ')
print(" " * 6 + '(8) Total force per atom        -all available                 ')
print(" " * 6 + '(9) Force per atom coordinates  -all available                 ')

print(" " * 8 + '** only 5 and 8 programed for now, others maybe latter\n')

PlotThese = input(' '*4+'>> Plot (default = 5) : ') or "5"

if PlotThese in ['8', '9']:
	WhichAtom = input(' ' * 4 + '>> Which atoms? (def: 1 2) : ') or '1 2'
	# parse
	try:
		if WhichAtom == "0":
			WhichAtom = [i + 1 for i in range(NAtoms2)]
		else:
			_ParseAtomList = WhichAtom.split()
			_AtomList = []
			while '-' in _ParseAtomList:
				_idx = _ParseAtomList.index('-')
				_range = [int(_ParseAtomList[_idx - 1]), int(_ParseAtomList[_idx + 1])]
				_AtomList += [_k for _k in range(min(_range), max(_range) + 1)]
				_ParseAtomList = _ParseAtomList[:_idx - 1] + _ParseAtomList[_idx + 2:]
			for i in _ParseAtomList:
				if int(i) not in _AtomList:
					_AtomList.append(int(i))

			_AtomList.sort()  # sort
			WhichAtom = list(dict.fromkeys(_AtomList))  # remove duplicates
	except:
		raise NameError(" Something went wrong while parsing the atom list")

	# check in range
	for _iAt in WhichAtom:
		if _iAt > NAtoms:
			raise TypeError("Asked for an atom that is not in the POSCAR/OUTCAR list")




#####################################################################################################
#### Now parsing data ###############################################################################

#### ---- Get Forces energies
ForceList = []; ConfigCounter = 0;
EDIFFGlist = []; EDIFFlist = []; IBRIONlist=[]; ConvergenceList = []

print('='*80)
print(' Searching files ... ', end='')
for iDirFile, iDirGeom in zip(FileList, GeomList):
	#### ----------- Enter File Level
	print()
	print(" "*5 + "(*)" +iDirFile.ljust(30) + " : ", end='')

	# Confirm NAtoms
	with open(iDirGeom, 'r') as f:
		POSCAR = f.readlines()
	_NAtoms = sum([int(i) for i in POSCAR[6].split()])
	if not NAtoms == _NAtoms:
		raise NameError(" The number of atoms does not coincide in " + iDirGeom)
		quit()
	else:
		print("NAt Ok", end='')

	# Check IBRION
	try:
		_IBRIONcheck = subprocess.check_output("grep IBRION " + iDirFile,shell=True, text=True).split('\n')[1].split()[2]
		IBRIONlist.append(_IBRIONcheck)
		print(", IB Ok", end='')
	except:
		IBRIONlist.append("?")
		print(", IB ? ", end='')


	# Check EDIFFG
	try:
		_ForceConvCheck = subprocess.check_output("grep 'stopping-criterion for IOM' " + iDirFile,
												shell=True, text=True).split('\n')[0].split()[2]
		EDIFFGlist.append(-float(_ForceConvCheck))
		print(", EDIFFG Ok", end='')

	except:
		EDIFFGlist.append(0.)
		print(", EDIFFG ? ", end='')

	# Check EDIFF
	try:
		_ElecConvCheck = subprocess.check_output("grep 'stopping-criterion for ELM' " + iDirFile,
												shell=True, text=True).split('\n')[0].split()[2]
		EDIFFlist.append(-float(_ElecConvCheck))
		print(", EDIFF Ok", end='')
	except:
		EDIFFlist.append(0.)
		print(", EDIFF ? ", end='')

	# Check force convergence archieved
	try:
		_txt = "'reached required accuracy - stopping structural energy minimisation'"
		_ConvergedCheck = subprocess.check_output("grep " + _txt + " " + iDirFile,
												  shell=True, text=True).split('\n')[0]
		if "reached" in _ConvergedCheck:
			_Converged = True
			print(", Conv Ok", end='')
		else:
			print(", Conv No", end='')

	except:
		_Converged = False
		print(", Conv ? ", end='')
	ConvergenceList.append(_Converged)


	# Getting the degrees of freedom
	# POSCAR file is used to get the number of atoms and check which atom
	# coordinates are free to be relaxed.
	try:
		with open(iDirGeom, 'r') as f:
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


		RelaxCoord = [[FreeCoord(k) for k in iLine.split()[3:]] for iLine in POSCAR[9:9 + NAtoms]]
		DoF = 0
		for _i in RelaxCoord:
			for _j in _i:
				if _j:
					DoF +=1
		print(', DoF:'+str(DoF), end='')

		# TODO: THIS DOES NOT DETECT WHEN SELECTIVE DYNAMICS IS NOT CONSIDERED, IT JUMPS THE FIRST
		# TODO: ATOM AND RelaxCoord IS LIST OF EMPTY LISTS.
		#CodeStatus("Found " + str(NAtoms) + " atoms and their degrees of freedom from " + iDirGeom)
	# Debug: print("RelaxCoord")
	# Debug: [print(k) for k in RelaxCoord]
	except:
		raise TypeError("Something went wrong when reading the " + iDirGeom + " file as a full vasp-POSCAR format!")
	# Got RelaxCoord = [ [False, False, False] , ... , [True, True, True]] as activated relaxation list
	# per atom and coordinate






	# Extract forces block
	ForcesExtracted = subprocess.check_output("grep TOTAL " + iDirFile + " -A " + str(NAtoms + 4),
											  shell=True,
											  text=True).split('\n')
	print(", GotForce blocks", end='')

	# Parsing forces blocks in this file
	OUTCAR = ForcesExtracted
	StepDict = {0: []}
	StepCounter = -1	# Step in this file
	_i = 0				# line number in Force blocks named OUTCAR
	while _i < len(OUTCAR):
		iLine = OUTCAR[_i]
		# Encounter a force block
		if "TOTAL-FORCE (eV/Angst)" in iLine:
			StepCounter += 1; _i += 2

			# All the force block
			_ForceRaw = [[float(_j) for _j in kline.split()[3:]] for kline in OUTCAR[_i:_i + NAtoms]]
			# Frozen coordinates are zero in this one
			_ForceFree = [[ii * jj for ii, jj in zip(iii, jjj)] for iii, jjj in zip(_ForceRaw, RelaxCoord)]

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
			StepDict[StepCounter] = {"Forces": _ForceRaw,  # [atom [coords] ] force block (all)
									 "FreeForces": _ForceFree,
									 # [atom [coords] ] force block (Free degrees of freedom, DoF)
									 "Magnitudes": _ForceMagRaw,  # [force magnitude] all force block
									 "FreeMagnitudes": _ForceMagFree,  # [force magnitude] all force block
									 "Max-ForceCoordinate": _MaxForceCoordFree,  # Max force in coordinate (free DoF)
									 "Max-ForceCoordinate-Atom": _MaxForceCoordFree_AtomN,
									 "Max-ForceMagnitude": _MaxForceMagFree,  # Max force magnitude (free DoF)
									 "Max-ForceMagnitude-Atom": _MaxForceCoordFree_AtomN,
									 }

			# Move counter over the atomic block
			_i += NAtoms
			ConfigCounter += 1

		# next line
		_i += 1
	ForceList.append(StepDict)
	print(f', got {len(list(StepDict.keys()))}', end='')



print('\n >> Got '+str(ConfigCounter)+' entries in total from '+str(len(ForceList)) + ' files')

#### ---- Plotting
# Create
fig, ax = plt.subplots(1,1, figsize=(6.5,4.), dpi=80)
ax.set_position([.15, .1, .8, .85])

# Relative scale?
plt.ylabel('Force [eV/A]')
ax.ticklabel_format(useOffset=False, axis='y')

# Add convergence
if not input(' > Add convergence text? : '):
	AddConvText = True

########################################################################################################################
########################################################################################################################
#### Parsing to plot

# Plotting
print(' Plotting!')
Xstarter = 0; heighvary = .08; heigh = .65
ax.axhline(y=0., xmin = 0, color = 'k', lw = 0.5)
PlotCount = 0

for j, iForceList in enumerate(ForceList):
	# Convergence limits
	plt.axvline(x=Xstarter-.5, alpha=.5, lw = .5)
	ax.fill_between([Xstarter-.25, Xstarter+len(iForceList)-.75], [EDIFFGlist[j], EDIFFGlist[j]],
					color = 'g', zorder=0, alpha = .2)
	if PlotThese in ["9"]:
		ax.fill_between([Xstarter - .25, Xstarter + len(iForceList) - .75], [-EDIFFGlist[j], -EDIFFGlist[j]],
						color='g', zorder=0, alpha=.2)
	# Add convergence text
	if AddConvText:
		plt.annotate('#:'+str(j+1)+'\nIB:' + IBRIONlist[j]+'\nel:' + str(EDIFFlist[j])+'\ng:'+str(EDIFFGlist[j]),
					 xy=(Xstarter+len(iForceList)-.75,heigh+heighvary),
					 xycoords=('data', 'axes fraction'),
					 fontsize='small', ha='right', bbox=dict(boxstyle="round", alpha=0.1))
		heighvary *= -1

	#### Preparing plot

	# Maximum force magnitude
	if "5" in PlotThese:
		CodeStatus(" Plotting Maximum of force magnitude in atoms (DOF only) per step")
		_ncols = 1
		XXplot = [Xstarter + i for i in list(iForceList.keys())]
		YYplot = [iForceList[i]["Max-ForceMagnitude"] for i in list(iForceList.keys())]

		ax.plot(XXplot, YYplot,
				marker='+', markeredgecolor='k', linewidth=.5)

		if ConvergenceList[j]:
			ax.plot(Xstarter-1+len(iForceList),
					iForceList[list(iForceList.keys())[-1]]["Max-ForceMagnitude"],
					marker='o',  markerfacecolor='none', markeredgecolor='g', markersize=8)


	#######################
	if PlotThese in ['8', '9']:
		if PlotThese == '8':
			print(f'Entered plot 8 for file {j}')
			print(f'WhichAtom: {WhichAtom}')
			# extract to create dictionary
			_PlotList = {_iAt: [] for _iAt in WhichAtom}
			print(f'Dictionary to plot : {_PlotList}')
			for _iDic in list(iForceList.keys()):
				for _jAtom in WhichAtom:
					print(f'  ->Entered _iDic {_iDic}, jatom {_jAtom}')
					_PlotList[_jAtom].append(iForceList[_iDic]["Magnitudes"][_jAtom - 1])
			print(f'Dictionary to plot : {_PlotList}')


		elif PlotThese == '9':
			# extract to create dictionary
			WhichAtomXYZ = [str(i) + j for i in WhichAtom for j in ['x', 'y', 'z']]
			_PlotList = {_iAt: [] for _iAt in WhichAtomXYZ}
			for _iDic in list(iForceList.keys()):
				for _jAtom in WhichAtom:
					for _kAxis, _kName in enumerate(['x', 'y', 'z']):
						_PlotList[str(_jAtom) + _kName].append(iForceList[_iDic]["Forces"][_jAtom - 1][_kAxis])

		# Add to plot
		for _kAtom in list(_PlotList.keys()):
			PlotCount += 1
			ax.plot([i + Xstarter for i in list(iForceList.keys())],
					_PlotList[_kAtom],
					marker='+', markeredgecolor='k', linewidth=1.1, label= '(' + str(j+1) + ')'+ str(_kAtom))




	#######################

	Xstarter += len(iForceList)

SHowLegend = input('  > Hide legend (*) ? ')
if not SHowLegend:
	_ncols = max(int((PlotCount) ** .5), 1)
	leg = plt.legend(ncols=_ncols)
	for line in leg.get_lines():
		line.set_linewidth(3)
	leg.set_draggable(True)

# Title
if ConvergenceList[-1]:
	ax.set_title('Relaxation\nconverged', x=.95, y=.95, ha='right', va='top')
else:
	ax.set_title('Relaxation\nnot converged', x=.95, y=.95, ha='right', va='top')

# nice
ax.grid(which='both', axis='y', linewidth=.5)

plt.xlabel('Iteration')

if input('  > Save fig? '):
	plt.savefig('./Forces_through_runs.png')


plt.show()




quit()


# Title
if ConvergenceList[-1]:
	ax.set_title('Relaxation\nconverged', x=.95, y=.95, ha='right', va='top')
else:
	ax.set_title('Relaxation\nnot converged', x=.95, y=.95, ha='right', va='top')

# nice
ax.grid(which='both', axis='y', linewidth=.5)

plt.xlabel('Iteration')

if input('  > Save fig? '):
	plt.savefig('./Forces_through_runs.png')



























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
ax.set_position([.15, .12, .8, .85])


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
