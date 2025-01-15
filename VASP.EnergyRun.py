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

################################################################################################################################
################################################################################################################################

print(' '*4+'Checking progress of relaxation')

FileName = input(' '*4+'>> Filename of images (def=OUTCAR)      : ')
if FileName=='': FileName='OUTCAR'

# Collectors
scf_dict = {0:[]}
dipolCorr_dict={}
RelaxEList = []
RelaxConverg = False

# Opening file
with open(FileName, 'r') as f:
		OUTCAR = f.readlines()

# Getting data points
for iLine in OUTCAR:
	# If there is scf Geometry
	if 'energy without entropy =' in iLine:
		# check slot exist
		if not len(RelaxEList) in scf_dict: scf_dict[len(RelaxEList)]=[]
		# Add scf point
		try:
			scf_dict[len(RelaxEList)].append(float(iLine.split()[-1]))
		except:
			print(" "*4+">> Something went wrong while reading line")
			print(" "*8 + iLine)
			scf_dict[len(RelaxEList)].append(0.)
	elif 'dipol+quadrupol energy correction' in iLine:
		#  Save dipolar correction
		dipolCorr_dict[len(RelaxEList)]=float(iLine.split()[3])
	elif 'energy  without entropy='in iLine:
		# Add relaxation point
		RelaxEList.append(float(iLine.split()[-1]))
	elif ' reached required accuracy - stopping structural energy minimisation' in iLine:
		RelaxConverg = True

#### Plottting
RelativeScale = input(' '*4+'>> Relative scale (def=y/no)            :')
if RelativeScale in ['n', 'no', 'NO', 'N']:
	RelativeScale=False
else:
	RelativeScale=True

Incl_scf = input(' '*4+'>> Include all scf points? (yes/def=no) : ')
if Incl_scf in ['yes', 'YES', 'y']:
	Incl_scf = True
else:
	Incl_scf=False



# Create
fig, ax = plt.subplots(1,1, figsize=(6.5,4.), dpi=80)
ax.set_position([.15, .12, .8, .85])

# Relative Scale
if RelativeScale:
	Scale_base = float(int(RelaxEList[0]))
	plt.ylabel('Energy [eV, OFfset=' + str(Scale_base) + '.0]')
else:
	Scale_base = 0.
	plt.ylabel('Energy [eV]')
	ax.ticklabel_format(useOffset=False, axis='y')

# Add geom points
ax.plot([i+1 for i in range(len(RelaxEList))], [k-Scale_base for k in RelaxEList], marker='+', markeredgecolor='k', linewidth=.5)
if RelaxConverg:
	ax.plot(len(RelaxEList), RelaxEList[-1]-Scale_base, marker='o',  markerfacecolor='none', markeredgecolor='g', markersize=8)

# Add scf points
if Incl_scf:
	Limits = ax.get_ylim()
	for Slot in scf_dict:
		# Check corrections
		if Slot in dipolCorr_dict: DipolCorr = dipolCorr_dict[Slot]
		else: DipolCorr = 0.
		# Compute step
		scf_step = 1./(len(scf_dict[Slot])+1)
		# Add points
		ax.plot([1+Slot+scf_step*(k+1)-1 for k in range(len(scf_dict[Slot]))],
				[j-Scale_base+DipolCorr for j in scf_dict[Slot]],
				marker='x', markeredgecolor='m', linewidth=.4, color='m', markersize=4)
	ax.set_ylim(Limits)

	# Report dipole
	if dipolCorr_dict == {}: print(' ' * 4 + 'Dipole corrections found, added to scf when possible.')
	# Overlay geom steps
	ax.plot([i+1 for i in range(len(RelaxEList)-1)], [k - Scale_base for k in RelaxEList][:-1], marker='o', markeredgecolor='k', markerfacecolor='none', linestyle='none', markersize=10)

# Title
if RelaxConverg:
	ax.set_title('Relaxation\nconverged', x=.95, y=.95, ha='right', va='top')
else:
	ax.set_title('Relaxation\nnot converged', x=.95, y=.95, ha='right', va='top')

# nice
ax.grid(which='both', linewidth=.5)

plt.xlabel('Iteration')



plt.show()
