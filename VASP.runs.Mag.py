#!/usr/bin/env python3

################################################################
################################ V.0

import os
import re

import matplotlib.pyplot as plt


################################################################################################################################
################################################################################################################################

print(' '*4+'Checking the magneization progression through multiple runs\n')

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

SerialPattern = input(' > Serial pattern (def=run) : ') or 'run'
MatchPattern = input(' > Required match (def None)') or False
for iFolder in [iFolder for iFolder in os.listdir('.') if os.path.isdir(iFolder)]:
	# Check previous run folders
	if SerialPattern in iFolder:
		# Check match
		if MatchPattern and not MatchPattern in iFolder:
			continue
		
	else:
		continue
	

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
print('\n Will gather magnetization from OSZICAR-type files')
FileList = []
for iDir in FolderList:
	_Filelist = []
	for kFile in os.listdir(iDir):
		if "OSZICAR_" in kFile and "run" in kFile:
			_Filelist.append((int(kFile.split("run")[1]), kFile))
		elif kFile == "OSZICAR":
			_Filelist.append((999, kFile))
	_SortedFileList = [x for _, x in sorted(_Filelist)]
	for iFile in _SortedFileList:
		if input(' > Include file (*=no / def True) '+iDir+'/'+iFile+' : '):
			print('  ** File not included! continuing')
		else:
			FileList.append(iDir+'/'+iFile)

#### ---- Get TOTEN energies
EnergyList = []; EnergyCounter = 0
print(' Searching files ... ', end='')
for iDirFile in FileList:
	_EnergyList = []; _Converged = False
	with open(iDirFile, "r") as iFile:
		for iLine in iFile:
			# is there energy here?
			if re.search("mag=  ", iLine):
				_EnergyList.append(float(iLine.split("mag=")[1]))
				EnergyCounter += 1


	EnergyList.append(_EnergyList)

print('got '+str(EnergyCounter)+' entries from '+str(len(EnergyList)) + ' files')


#### ---- Plotting
# Create
fig, ax = plt.subplots(1,1, figsize=(6.5,4.), dpi=80)
ax.set_position([.15, .1, .8, .85])

# Relative scale?
RelativeScale = input(' > Relative scale (def=y/no) :')
if RelativeScale in ['n', 'no', 'NO', 'N']:
	RelativeScale=False
	Scale_base = 0.
	plt.ylabel('mag [uB]')
	ax.ticklabel_format(useOffset=False, axis='y')
else:
	RelativeScale=True
	Scale_base = float(int(EnergyList[0][0]))
	plt.ylabel('mag [uB, OFfset=' + str('{:.1f}'.format(Scale_base)) + ']')

# Add convergence
if not input(' > Add convergence text? : '):
	AddConvText = True

# Plotting
print(' Plotting!')
Xstarter = 0; heighvary = .08; heigh = .65

for j, iEnergyList in enumerate(EnergyList):
	plt.axvline(x=Xstarter-.5, alpha=.5, lw = .5)
	ax.plot([Xstarter + i for i in range(len(iEnergyList))],
			[k-Scale_base for k in iEnergyList],
			marker='+', markeredgecolor='k', linewidth=.5)

	# Add convergence text
	if AddConvText:
		plt.annotate('#:'+str(j+1),
					 xy=(Xstarter+len(iEnergyList)-.75,heigh+heighvary),
					 xycoords=('data', 'axes fraction'),
					 fontsize='small', ha='right', bbox=dict(boxstyle="round", alpha=0.1))
		heighvary *= -1

	Xstarter += len(iEnergyList)




# nice
ax.grid(which='both', axis='y', linewidth=.5)

plt.xlabel('Iteration')

plt.show()

quit()


