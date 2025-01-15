#!/usr/bin/env python3

################################################################
################################ V.0

import os
import re

import matplotlib.pyplot as plt


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
EnergyList = []; ConvergenceList = []; EnergyCounter = 0; EDIFFGlist = []; EDIFFlist = []; Modelist=[]
print(' Searching files ... ', end='')
for iDirFile in FileList:
	_EnergyList = []; _Converged = False; _gettingIBRION = False
	with open(iDirFile, "r") as iFile:
		for iLine in iFile:
			# get IBRION
			if re.search('Dimension of arrays',iLine):
				_gettingIBRION = True			
			if re.search('   IBRION =    ', iLine):
				if _gettingIBRION:
					try:
						Modelist.append(iLine.split()[2])
					except:
						Modelist.append('?')
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
	if not _gettingIBRION:
		Modelist.append('?')
	ConvergenceList.append(_Converged)


	EnergyList.append(_EnergyList)

print('got '+str(EnergyCounter)+' entries from '+str(len(EnergyList)) + ' files')

# Add convergence
if not input(' > Add convergence text? : '):
	AddConvText = True
else:
	AddConvText = False

try:
	AddRefLine = float(input(' > Add reference line at energy? : '))
except:
	AddRefLine = False

#SaveThePlot = False
#if input(" > Save the plot after ? : "):
#	SaveThePlot = True

# Plot title
PlotTitle = input(' > Add plot title : ')


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
		plt.annotate('#:'+str(j+1)+'\nIB:' + Modelist[j] + '\nel:' + str(EDIFFlist[j])+'\ng:'+str(EDIFFGlist[j]),
					 xy=(Xstarter+len(iEnergyList)-.75,heigh+heighvary),
					 xycoords=('data', 'axes fraction'),
					 fontsize='small', ha='right', bbox=dict(boxstyle="round", alpha=0.1))
		heighvary *= -1

	Xstarter += len(iEnergyList)

	if ConvergenceList[j]:
		ax.plot(Xstarter-1, iEnergyList[-1]-Scale_base,
				marker='o',  markerfacecolor='none', markeredgecolor='g', markersize=8)

# Add reference line
if AddRefLine:
	plt.axhline(y=AddRefLine - Scale_base, color = 'b', linestyle = '--')

# Add plot title
if PlotTitle:
	FixX = float(input(' > fix title x position : ') or 0.4)
	plt.annotate(PlotTitle, xy=(FixX, 0.9), xycoords='axes fraction', fontsize=14, ha='center')


# Report convergence
if ConvergenceList[-1]:
	ax.set_title('Relaxation\nconverged', x=.95, y=.95, ha='right', va='top')
else:
	ax.set_title('Relaxation\nnot converged', x=.95, y=.95, ha='right', va='top')

# nice
ax.grid(which='both', axis='y', linewidth=.5)

plt.xlabel('Iteration')

if input('  > Save fig? '):
	plt.savefig('./Energy_through_runs.png')

plt.show()
#if SaveThePlot:
#	plt.savefig('Relaxation.jpeg')


quit()


