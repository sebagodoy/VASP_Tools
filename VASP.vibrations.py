#!/usr/bin/env python3

# Version 0.1
import numpy as np

print('  Recalculation  of vibrational frequencies from Hessian matrix')

def CodeStatus(inStr, **kwargs):
	print(' '*kwargs.get('l',4) + '> '+ inStr,  end=kwargs.get('end','\n'))

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

############ Check Information in  POSCAR
try:
	# Open, read and extract information nedded
	with open('POSCAR','r') as f:
		POSCAR = f.readlines()
		AtomType_POSCAR = POSCAR[5].split()
		AtomQuant_POSCAR = [int(iT) for iT in POSCAR[6].split()]
	# Report
	strPOSCAR = ''
	for i,j in zip(AtomQuant_POSCAR, AtomType_POSCAR): strPOSCAR +=str(i)+' '+j+', '
	CodeStatus('POSCAR file found and properly read: '+strPOSCAR[:-2])

	############################################################################################
	#### Created: 	AtomType_POSCAR = ['Atom name 1', 'Atom name 2']
	####			AtomQuant_POSCAR = ['Amomunt of Atom 1', 'Amount of Atom 2', ...]
	############################################################################################

except:
	quit(' '*8+'>>>> Is there something wrong with the POSCAR file? Is it there? are atomic types in the 6th line?')


############ Check Information in  POTCAR
try:
	# Open POTCAR, get Atomic names and POMASS mases
	with open('POTCAR','r') as f:
		AtomType_POTCAR = []
		AtomMass_POTCAR = []
		for iLine in f.readlines():
			if 'VRHFIN' in iLine: AtomType_POTCAR.append(iLine.split('=')[1].split(':')[0].strip())
			elif 'POMASS' in iLine: AtomMass_POTCAR.append(float(iLine.split('=')[1].split(';')[0]))

	# Check POTCAR mass information is complete (each   ato m type has a mass)
	if not len(AtomType_POTCAR) == len(AtomMass_POTCAR): quit(' ' * 8 + '>>>> Mass information is missing. Something is wrong with the POTCAR file.')

	# Report
	CodeStatus('POTCAR has been found and properly read')

except:
	quit(' '*8+'>>>> There is something wrong with the POTCAR file. Is it there?')

############ Check POTCAR and POSCAR coincide
if not AtomType_POTCAR == AtomType_POSCAR: quit(' '*8+'>>>> POTCAR and POTCAR species does not coincide. POSCAR='+str(AtomType_POSCAR)+' / POTCAR='+str(AtomType_POTCAR))


	############################################################################################
	#### Created: 	AtomType_POTCAR = ['Atom name 1', 'Atom name 2']
	####			AtomMass_POSCAR = ['Mass of Atom 1', 'Mass of Atom 2', ...]
	############################################################################################


################################################################################################################################
################################################################################################################################
print(' '*6+'-'*60)
################################################################################################################################
################################################################################################################################

#### Consolidate parametric information

#### Construct dictionary Atom mases
AtomMass = {}
for i,j in zip(AtomType_POTCAR, AtomMass_POTCAR): AtomMass[i] = j
# CodeStatus('Atom masses dictionary created in the form \'Atom name\':\'Atom mass\'')
CodeStatus('Atom masses dictionary : ' + str(AtomMass)) # Debug

#### Create Atom List dictionary: Atom_index['Atom number'] = 'Atom name'
Atom_index = {}
AtomCounter = 0
for i, j in zip(AtomQuant_POSCAR, AtomType_POSCAR):
	for k in range(int(i)):
		AtomCounter += 1
		Atom_index[str(AtomCounter)] = [j,AtomMass[j]]
CodeStatus('Atom index created = {\'Atom index number : [\'Atom name\', Atom mass]}')
CodeStatus('Atom index created = {' + list(Atom_index.keys())[0]+':'+str(list(Atom_index.values())[0])+' ... '+ list(Atom_index.keys())[-1]+':'+str(list(Atom_index.values())[-1])+'}')  # Debug


################################################################################################################################
################################################################################################################################
print(' '*6+'-'*60)
################################################################################################################################
################################################################################################################################


#### Wish to  modify?
Modifiying = True
while Modifiying:
	if  input(' '*4+'> Wish to modify some mases ? (y/def=n) : ') == 'y':
		#####
		print(' '*8+'.'*40)
		#####

		# Ask for Modification type
		ModificationType = str(input(' '*8+'> Modify by atom type (def=t) or by atom index (i) ?  : '))
		if ModificationType == '': ModificationType = 't'

		if not ModificationType in ['t','i']:
			CodeStatus('Option has to be \'t\' (for atom type, default option) or \'i\' (for atom index), try again.')
			continue

		# Modify by atom type
		if ModificationType == 't':
			# Ask for atom name
			try:
				ModyAtomName = input(' '*12+'> Modify mass  of atom (name) : ')
				AtomMass[ModyAtomName]
			except:
				CodeStatus('Atom type not recognized, Come again ?',  l=8)
				continue
			# Ask for new mass
			try:
				ModifyAtomMass = float(input(' '*12+'> New mass (g/mol) of atom    : '))
			except:
				CodeStatus('Mass  not recognized. Sure it was a number?', l=8)
				continue
			# Modify registry
			AtomMass.pop(ModyAtomName)
			AtomMass[ModyAtomName+'-Istp.'] = ModifyAtomMass
			for k in Atom_index:
				if Atom_index[k][0] == ModyAtomName: Atom_index[k] = [ModyAtomName+'-Istp',  ModifyAtomMass]
			CodeStatus('New dict. of masses : ' + str(AtomMass), l=12)

		# Modify by atom index
		elif ModificationType == 'i':
			# Ask for atom index
			try:
				ModyAtomIndex = input(' '*12+'> Modify mass  of atom (index, 1 to '+str(AtomCounter)+')   : ')
				Atom_index[ModyAtomIndex]
			except:
				CodeStatus('Atom index not recognized. Atoms in POSCAR are numbered from ',  l=8)
				continue
			# Ask for new mass
			try:
				ModifyAtomMass = float(input(' '*12+'> New mass (g/mol) of atom #'+ModyAtomIndex+' ('+Atom_index[ModyAtomIndex][0]+', '+str(Atom_index[ModyAtomIndex][1])+')'+'    : '))
			except:
				CodeStatus('Mass  not recognized. Sure it was a number?', l=8)
				continue
			# Modify registry
			AtomMass[Atom_index[ModyAtomIndex][0]+'-Istp'] = ModifyAtomMass
			Atom_index[ModyAtomIndex] = [Atom_index[ModyAtomIndex][0]+'-Istp', ModifyAtomMass]
			CodeStatus('Added exception : Atom=' + str(Atom_index[ModyAtomIndex]), l=12)

		# Ask for review
		if input(' '*4+'> Review registry? (y/def=n) : ') == 'y':
			print(' '*12+'Atom types and mases : '+str(AtomMass))
			print(' '*12+'Atom index list : ')
			for k in Atom_index:
				print(' '*16+'Atom N='+str(k)+' , type '+Atom_index[k][0]+' , mass (g/mol) = '+str(Atom_index[k][1]))

	else:
		CodeStatus('Atom types and mases are set. Continuing ... ')
		Modifiying = False




############################################################################################
#### Created: 	AtomMass = {'Atom name' : Atom mass}
####			Atom_index = {'Atom index number' : ( 'Atom name', Atom mass)}
############################################################################################






################################################################################################################################
################################################################################################################################
print(' '*6+'-'*60)
################################################################################################################################
################################################################################################################################

############ Check Information in  OUTCAR

try:
	# Getting OUTCAR
	with open('OUTCAR', 'r') as f:
		OutFile = f.readlines()
	CodeStatus('OUTCAR file found and read')
	# with open('POTCAR', 'r')

except: quit('OUTCAR file not found')



LineIter = iter(OutFile)
# IBRION type
while True:
	try:
		iLine = next(LineIter)
		if 'IBRION' in iLine.split():
			if int(iLine.split()[2]) in [5,6,7]: CodeStatus('Calculation is of frequency type (IBRION='+iLine.split()[2]+')')
			break

	except:
		quit(' '*8+'>>>> IBRION tag not found or incomplete, something is really wrong here')


# DOF
while True:
	try:
		iLine = next(LineIter)
		if 'Degrees' in iLine.split():
			DOF = int(iLine.split()[5])
			CodeStatus('A total of '+str(DOF)+' degrees of freedom are considerated')
			break
	except:
		quit(' ' * 8 + '>>>> Degrees of freedom not found')






# Second derivative matrix
while True:
	try:
		iLine=next(LineIter)
		if ' SECOND DERIVATIVES (NOT SYMMETRIZED)\n' == iLine:
			# DOF list
			next(LineIter)
			DOF_list = next(LineIter).split()
			CodeStatus('Degrees of freedom list retrieved : '+str(DOF_list)) # Debug
			# Hessian
			Hess = []
			for iRow in range(DOF):
				Hess.append([-float(ele) for ele in next(LineIter).split()[1:]])

			# End recollection
			break

	except:
		quit(' ' * 8 + '>>>> Something is wrong with your second derivatives matrix. It may be missing or incomplete, check it out.')

# Report Hessian
CodeStatus('Hessian matrix properly retrieved')

def ReportHessian():
	print(' (decimals chopepd only for visualization): \n')											# Debug
	print(' ' * 18, end='')																			# Debug
	for iDOF in DOF_list: print(FixBlanck(Atom_index[iDOF[:-1]][0] + ':' + iDOF), end=' ')			# Debug
	print('')																						# Debug
	for iRow, iDOF in zip(Hess, DOF_list):															# Debug
		print(' ' * 10, end=FixBlanck(Atom_index[iDOF[:-1]][0] + ':' + iDOF))						# Debug
		for iCol in iRow:																			# Debug
			print(FixNumBlanck(iCol), end=' ')														# Debug
		print('')																					# Debug
	print('')

# ReportHessian()	# Debug

# Force symmetrization
if not input(' '*4+'> Force symmetrization of Hessian by averaging (VASP default) ? (def=y/n) : ') == 'n':
	# top triangle
	for i in range(len(DOF_list)-1):
		for j in range(1+i,len(DOF_list)):
			# print('Index:('+str(i)+','+str(j)+')'+str(Hess[i][j]))
			Hess[i][j] = (Hess[i][j] + Hess[j][i]) / 2.
			Hess[j][i] = Hess[i][j]

else:
	CodeStatus('Keeping original non-symmetrized Hessian matrix from VASP OUTPUT: ')
	ReportHessian()


####################################################################
#### Created: 	Hess = Hessian matrix of second derivatives
####################################################################




################################################################################################################################
################################################################################################################################
print(' '*6+'-'*60)
################################################################################################################################
################################################################################################################################


############ Recalculation of frequencies

eV2J = 1.602176634e-19	# J/eV
Nav = 6.02214076e23		# Part/mol
cc = 299792458 			# m/s


MassHess = []
for iRow, iDOF in zip(Hess, DOF_list):
	MassHess_row = []
	# print(str(iDOF)+' = '+str(Atom_index[iDOF[:-1]])+' -> '+str(iRow)) # debug
	RowMass = Atom_index[iDOF[:-1]][1]
	for iHess in iRow:
		MassHess_row.append(iHess/RowMass)
	# print('-'*20+'> ' + str(MassHess_row))  # debug
	MassHess.append(MassHess_row)




#  Report
CodeStatus('Positive mass weighted hessian matrix constructed ')
# print('(decimals chopepd only for visualization): \n'+' ' * 12) 									# Debug
# for iDOF in DOF_list: print(FixBlanck(Atom_index[iDOF[:-1]][0] + ':' + iDOF, l=16), end=' ')  	# Debug
# print('') 																						# Debug
# for iRow, iDOF in zip(MassHess, DOF_list):  														# Debug
# 	print(' ' * 4, end=FixBlanck(Atom_index[iDOF[:-1]][0] + ':' + iDOF))							# Debug
# 	for iCol in iRow:																				# Debug
# 		print(FixNumBlanck(iCol, l=16), end=' ')													# Debug
# 	print('')																						# Debug


# Eigenvalues and Eigenvectors
HessArray = np.array(MassHess)
eVal, eVect = np.linalg.eig(HessArray)
CodeStatus('Eigenvalues and eigenvectors were calculated : \n')

# for iF in eVal: print(str(FixNumBlanck(iF, l=8, d=2)), end=' / ') # Debug
# print() # Debug


# Aplying factors
eVal = [k * eV2J * Nav * 1e3 * 1e20 for k in eVal]	# [1/s^2],

# Linear frequencies [1/s = Hz]
FqReal = []; FqImg=[]
for iVal in eVal:
	if iVal <0: FqImg.append(	((-iVal)**.5)	/(2*np.pi))
	else: 		FqReal.append(	((iVal)**.5)	/(2*np.pi))

# Order frequencies
FqReal.sort(reverse=True)
FqImg.sort(reverse=True)

# Spectral frequencies [cm-1]
FqRealcm = []; FqImgcm=[]
for iFq in FqReal: FqRealcm.append(	iFq/(100*cc))
for iFq in FqImg: FqImgcm.append(	iFq/(100*cc))

# Report
def ReportFreqList(iFreqList, **kwargs):
	for iFq in iFreqList: print(FixNumBlanck(iFq, l=kwargs.get('l',9), d=kwargs.get('g',2)), end='')


print(' '*8, end='Real freqs      (THz) : ')
ReportFreqList([k*1e-12 for k in FqReal]) # THz
print('\n'+' '*8, end='               (cm-1) : ')
ReportFreqList(FqRealcm) # cm-1

print('\n\n'+' '*8, end='Imaginary freqs (THz) : ')
if len(FqImg) == 0: print('None found')
else:
	ReportFreqList([k*1e-12 for k in FqImg]) # THz
	print('\n' + ' ' * 8, end='               (cm-1) : ')
	ReportFreqList(FqImgcm) #  cm-1
print('\n')

CodeStatus("List of frequencies (cm-1)\n")
print(" "*8 + "Real : "+str( [float("{:.6f}".format(i)) for i in FqRealcm] ) )
print(" "*8 + "Img  : "+str( [float("{:.6f}".format(i)) for i in FqImgcm] ) )
print("")


################################################################################################################################
################################################################################################################################
print(' '*6+'-'*60)
################################################################################################################################
################################################################################################################################



############################### ZPVE calculation
hh			= 6.62606957E-34
cc			= 299792458
eV2J		= 1.602176634E-19
def fZPVEi(iFreq):
	return (iFreq * hh * cc * 100) / (2 * eV2J)			# /(eV)

# Contribuciones reales individuales
FqRealeV = []
for iFq in FqRealcm: FqRealeV.append(fZPVEi(iFq))

# Cut Off
try:
	CutOff = float(input('  '*2+'> CutOff for ZPVE (def=100cm-1) = '))
except:
	CodeStatus('What\'s that? Using default value = 100 cm-1')
	CutOff = 100

# Replace lower tha cutoff
ReplaceOrNot = input('  '*2+'> Replace lower freqs with the CutOff for ZPVE? (def=yes/*=No) = ')

# Replace Imaginary freqs
ReplaceImg = input('  '*2+'> Replace imaginary frequencies by adding to real freqs = ')
if ReplaceImg:
	_asd = [float(i) for i in ReplaceImg.split(';')]
	for i in _asd: FqRealcm.append(i)

# ZPVE summ
ZPVE = 0
for iFq in FqRealcm:
	if iFq > CutOff: 
		print(iFq, end=' ; ')
		ZPVE+=fZPVEi(iFq)
	elif not ReplaceOrNot:
		print(CutOff, end=' ; ') 
		ZPVE+=fZPVEi(CutOff)

# Report
print()
Separe = True
CodeStatus('ZPVE contributions (eV) : ', end='')
for  iF in FqRealcm:
	if Separe and iF < CutOff:
		print(' \n'+' '*9+'real but not in ZPVE : ', end='')
		Separe = False
	print(FixNumBlanck(fZPVEi(iF), l=4, d=4), end=' ' * 3) # eV
print('')

CodeStatus('Accumulated ZPVE   (eV) : '+str(FixNumBlanck(ZPVE, d=10, l=0))+' eV\n')

