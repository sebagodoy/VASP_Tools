#!/usr/bin/env python3

################################################################
################################ V.0

import os
import re

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


################################################################################################################################
################################################################################################################################

print(' '*4+'Checking the TOTEN energy progression through multiple runs\n')

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
			continue
	else:
		continue
FolderList = [x for _,x in sorted(_FolderList)]

#### ---- Ask if the folders are Ok, remove folders if requested
print(' Found folders: ', end='')
print(' , '.join(FolderList))
QRemove = input(' > Include these in that order (def=y) : ')
while QRemove:
	removeThis = input('  Remove which one? : ') or ''
	FolderList = [iFolder for iFolder in FolderList if not iFolder == removeThis]
	print(' Ok, new folder list is : ', end='')
	print(' , '.join(FolderList))
	QRemove = input(' > Include these in that order (def=y) :')

#### ---- Gather files to include
print('\n Will gather TOTEN energies from geometric steps in OUTCAR-type files')
FileList = []
for iDir in FolderList:
	_Filelist = []
	for kFile in os.listdir(iDir):
		if "OUTCAR_" in kFile and "run" in kFile and not ".gz" in kFile:
			_Filelist.append((int(kFile.split("run")[1]), kFile))
		elif kFile == "OUTCAR":
			_Filelist.append((999, kFile))
	_SortedFileList = [x for _, x in sorted(_Filelist)]
	for iFile in _SortedFileList:
		if input(' > Include file (*=no / def True) '+iDir+'/'+iFile+' : '):
			print('  ** File not included! continuing')
		else:
			FileList.append(iDir+'/'+iFile)

#### ---- Get TOTEN energies
EnergyList = []; ConvergenceList = []; EnergyCounter = 0; EDIFFGlist = []; EDIFFlist = []
print(' Searching files ... ', end='')
for iDirFile in FileList:
	_EnergyList = []; _Converged = False
	with open(iDirFile, "r") as iFile:
		for iLine in iFile:
			# Check convergence forces
			if re.search('stopping-criterion for IOM', iLine):
				_tmp = float(iLine.split()[2])
				if _tmp < 0:
					EDIFFGlist.append(-_tmp)
				else:
					EDIFFGlist.append(0.)
			# Check convergence energies
			if re.search('stopping-criterion for ELM', iLine):
				EDIFFlist.append(float(iLine.split()[2]))
			# is there energy here?
			if re.search("free  energy   TOTEN", iLine):
				_EnergyList.append(float(iLine.split()[4]))
				EnergyCounter += 1
			# Does this line shows convergence?
			if re.search('reached required accuracy - stopping structural energy minimisation', iLine):
				_Converged = True
	ConvergenceList.append(_Converged)


	EnergyList.append(_EnergyList)

print('got '+str(EnergyCounter)+' entries from '+str(len(EnergyList)) + ' files')

# Add convergence
if not input(' > Add convergence text? : '):
	AddConvText = True

#### ---- Plotting
# Create
fig, ax = plt.subplots(1,1, figsize=(6.5,4.), dpi=80)
ax.set_position([.15, .1, .8, .85])

# Relative scale?
RelativeScale = input(' > Relative scale (def=y/no) :')
if RelativeScale in ['n', 'no', 'NO', 'N']:
	RelativeScale=False
	Scale_base = 0.
	plt.ylabel('Energy [eV]')
	ax.ticklabel_format(useOffset=False, axis='y')
else:
	RelativeScale=True
	Scale_base = float(int(EnergyList[0][0]))
	plt.ylabel('Energy [eV, OFfset=' + str('{:.1f}'.format(Scale_base)) + ']')

movieFolder = input(" > Movie folder : ") or "E0movie"
if movieFolder not in os.listdir("."):
	os.mkdir("./"+movieFolder)

qYspan = input(" > Fix ploting y span (eV) ?    : ")
qXspan = input(" > Fix ploting X span (0:all) ? : ")

# Plotting
print(' Plotting!')
heighvary = .08; heigh = .65
picCounter = 0
E0LongList = []
for i in EnergyList:
	for j in i:
		E0LongList.append(j)

for u in range(2, len(E0LongList)):
	#for j, iEnergyList in enumerate(EnergyList):
	#plt.axvline(x=Xstarter-.5, alpha=.5, lw = .5)
	iEnergyList = E0LongList[:u]
	ax.plot([i for i in range(len(iEnergyList))],
			[k-Scale_base for k in iEnergyList],
			marker='.', markeredgecolor='k', linewidth=.5)



	ann = plt.annotate('Step :' + str(u).rjust(4),
				 xy=(.04, .05),
				 xycoords=('axes fraction', 'axes fraction'),
				 fontsize=16, ha='left')

	# Title
	if ConvergenceList[-1] and u == len(E0LongList)-1:
		ax.set_title('Relaxation\nconverged', x=.95, y=.95, ha='right', va='top', weight='bold', color='g')

		ax.plot(len(iEnergyList)-1, E0LongList[-1]-Scale_base,
				marker='o',  markerfacecolor='none', markeredgecolor='g', markersize=8)

	else:
		ax.set_title('Relaxation\nnot converged', x=.95, y=.95, ha='right', va='top')

	# nice
	ax.grid(which='both', axis='y', linewidth=.5)
	if qYspan:
		plt.ylim([iEnergyList[-1] - float(qYspan)*.25 - Scale_base, iEnergyList[-1] + float(qYspan)*.75-Scale_base])
	if qXspan == "0":
		plt.xlim([0, len(E0LongList)])
	elif qXspan:
		plt.xlim([max(0, len(iEnergyList)-int(qXspan)), len(iEnergyList) + 1])


	plt.xlabel('Iteration')
	plt.savefig("./"+movieFolder+"/mov"+"{:06d}".format(picCounter)+".jpeg")

	picCounter += 1
	ann.remove()

plt.show()

quit()


