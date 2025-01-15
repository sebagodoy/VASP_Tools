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
				print(" !> Could not include " + iFolder + " because of its name format, must start as runX")
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
print(' Gathering geometries from XDATCAR files')
FileList = []
for iDir in FolderList:
	_Filelist = []
	for kFile in os.listdir(iDir):
		if "XDATCAR_" in kFile and "run" in kFile:
			_Filelist.append((int(kFile.split("run")[1]), kFile))
		elif kFile == "XDATCAR":
			_Filelist.append((999, kFile))
	_SortedFileList = [x for _, x in sorted(_Filelist)]
	for iFile in _SortedFileList:
		if input(' > Include file (*=no / def True) '+iDir+'/'+iFile+' : '):
			print('  ** File not included! continuing')
		else:
			FileList.append(iDir+'/'+iFile)

#### ---- Get geometries energies
Header = False
with open(FileList[0]) as f:
	Header = f.readlines()[:7]
NAtoms = sum([int(i) for i in Header[-1].split()])


GeomList = []
GeomCounter = 0
print(' Searching files ... ')
for iDirFile in FileList:
	with open(iDirFile, "r") as iFile:
		_cont = iFile.readlines()
	_GeomCounterIter = 0
	# Check match with Header
	if not Header == _cont[:7]:
		print("\n !> File Header from "+FileList[0]+" (initial)")
		[print("    > "+i, end="") for i in Header]
		print(" !> File Header from "+iDirFile)
		[print("    > "+i, end="") for i in _cont[:7]]
		raise TypeError("\n\n  !> File headers does not coincide, better consider combining by sections\n\n")
	# Consume coordinates
	iLine = 7
	while iLine < len(_cont):
		if "Direct configuration=" in _cont[iLine]:
			try:
				#print("Getting :" + _cont[iLine])
				iLine +=1; _coords = []
				for iAt in range(NAtoms):
					_coords.append([float(k) for k in _cont[iLine].split()])
					iLine +=1
				GeomList.append(_coords)
				GeomCounter += 1
				_GeomCounterIter += 1
				#print("Gotten")
			except:
				pass
				#print("Error here")
	print(" * Got "+str(_GeomCounterIter) + " configurations from "+iDirFile)
print(" Got "+str(len(GeomList)) + " configurations in total")

#### ---- Writting file
FileOut = input(" > Writte sequence to file (def=XDATCAR_all_runs) : ") or "XDATCAR_all_runs"

with open(FileOut, "w") as f:
	[f.write(i) for i in Header]
	GeomCounterOut = 1
	for iConf in GeomList:
		f.write("Direct configuration=" + str(GeomCounterOut).rjust(6)+"\n")
		for iAt in iConf:
			[f.write("  {:.8f}".format(i)) for i in iAt]
			f.write("\n")
		GeomCounterOut +=1
	f.write("Direct configuration=" + str(GeomCounterOut).rjust(6) + "\n")

print(" Done, check the "+FileOut + " file, e.g. with vmd as VASP_XDATCAR5 format")

