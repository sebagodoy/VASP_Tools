#!/usr/bin/env python3

# V.2.7 - 27/jul/2022 - SAGG

import os, subprocess
from datetime import datetime, timedelta
CWD = os.getcwd()
FileList = os.listdir(os.getcwd())

#### ---------------------------------------------------------------- Tools

def StartSection(NSEct,iStr):
	print(' '*4+'['+str(NSEct)+'] '+iStr)

def RaiseWarming(iStr):
	print('')
	print(' '*4+'*'*80)
	print(' '*4+' WARNING: '+iStr)
	print(' ' * 4 + '*' * 80+'\n')

def StrFix(iStr,le):
	if len(iStr)<le:
		return ' '*(le-len(iStr))+iStr
	else:	return iStr

def StrFixDot(iStr,le):
	if len(iStr)<le:
		return iStr+'.'*(le-len(iStr))
	else:	return iStr

def Status(iStr, **kwargs):
	print(' ' * 8 + '> '+iStr, end=kwargs.get('end', '\n'))

def Report(iStr, *args,  **kwargs):
	if not kwargs.get('NewLine'):
		print(' ' * 8 + StrFixDot('> '+iStr+' ', DotL) + ' : ', end='')
	else:
		print(' ' * (11+DotL)+iStr, end='')
	for i in args: print(i, end=' ')
	print('', end=kwargs.get('end','\n'))


print('\n'+' '*4+'General check at the end of a VASP run\n')

#### ---------------------------------------------------------------- Parameters

DotL = 35
SectNumber = iter(range(20))
neb = False


#### ---------------------------------------------------------------- Submit and Job INFO
StartSection(next(SectNumber), 'Submit job info')

#### Jobinfo
if 'JobInfo' in FileList:
	with open('JobInfo','r') as f:
		Jobinfo = f.readlines()

	# Búsqueda en todas las líneas
	Report('Jobinfo file found', end='')
	for iLine in Jobinfo:
		if "JobID=" in iLine: print(iLine.split()[0], end='')
		if "INICIA" in iLine: INI_line = iLine.split()
		if "TERMINA" in iLine: END_line = iLine.split()

	try:
		# INI_line[5][1:] timezone
		month2number={"ene":1, "feb":2, "mar":3, "abr":4, "may":5, "jun":6,
					  "jul":7, "ago":8, "sep":9, "oct":10, "nov":11, "dec":12,
					  "jan":1, "apr":4, "aug":8,
					  "jan.":1, "fev.":2, "mar.":3, "avr.":4, "mai":5, "nov.":11, "dec.":12, "May": 5, "Jun":6}
		# numbering format: INICIA mié feb 24 12:08:27 -03 2021
		INI_time = INI_line[4].split(':')
		END_time = END_line[4].split(':')
		INI_datetime = datetime(int(INI_line[6]), month2number[INI_line[2].lower()], int(INI_line[3]),
								int(INI_time[0]), int(INI_time[1]), int(INI_time[2]))
		END_datetime = datetime(int(END_line[6]), month2number[END_line[2].lower()], int(END_line[3]),
								int(END_time[0]), int(END_time[1]), int(END_time[2]))
		#print(INI_datetime)
		#print(END_datetime)
		Elapsed_time = END_datetime - INI_datetime
		print(', elapsed time:' + str(END_datetime - INI_datetime))
	except:
		try:
			# Other numbering format: INICIA: jeu. 02 nov. 2023 16:39:25 CET
			INI_time = INI_line[5].split(':')
			END_time = END_line[5].split(':')
			INI_datetime = datetime(int(INI_line[4]), month2number[INI_line[3].lower()], int(INI_line[2]),
									int(INI_time[0]), int(INI_time[1]), int(INI_time[2]))
			END_datetime = datetime(int(END_line[4]), month2number[INI_line[3].lower()], int(END_line[2]),
									int(END_time[0]), int(END_time[1]), int(END_time[2]))
			Elapsed_time = END_datetime - INI_datetime
			print(', elapsed time:' + str(END_datetime - INI_datetime))
		except:
			print()
			RaiseWarming('Timming information incomplete or format not recognized, better check that out.')


else:
	print(' '*8+'> Jobfile not found')


#### submit
FoundSubmit = False
for iFile in FileList:
	if 'submit' in iFile:
		FoundSubmit = True
		print(' ' * 8 + StrFixDot('> Submit file found ', DotL) + ' : ' + iFile, end=' , ')

		with open(iFile, 'r') as f:
			SubmitLines = f.readlines()
			f.close()

		for iLine in SubmitLines:
			if '#SBATCH -J' in iLine: iRunName = iLine.split()[2]
			if '#SBATCH -p' in iLine: print('partition:' + str(iLine.split()[2]), end=' , ')
			if '#SBATCH -n' in iLine:
				cpus = int(iLine.split()[2])
				print('cpu:' + str(cpus), end=' ')
			if '#SBATCH --mem-per-cpu' in iLine: print('mem/cpu:' + str(iLine.split('=')[1].split()[0]), end=' ')
			if '#SBATCH --ntasks-per-node' in iLine:
				taskpernode = int(iLine.split('=')[1].split()[0])
				print('task/node:' + str(taskpernode), end=' ')
			
			if '#MSUB -r' in iLine: iRunName = iLine.split()[2]
			if '#MSUB -q' in iLine: print('partition:' + str(iLine.split()[2]), end=' , ')
			if '#MSUB -n' in iLine:
				cpus = int(iLine.split()[2])
				print('cpu:' + str(cpus), end=' ')
			if '#SBATCH -t' in iLine:
				reqTime_str = iLine.split()[2]
				timenum = reqTime_str
				if "-" in timenum:
					reqTime_d = int(timenum.split("-")[0])
					timenum = timenum.split("-")[1]
				else:
					reqTime_d = 0
				if ":" in timenum:
					reqTime_h = int(timenum.split(":")[0])
					reqTime_m = int(timenum.split(":")[1])
					if len(timenum.split(":")) == 3:
						reqTime_s = int(timenum.split(":")[2])
					else:
						reqTime_h = 0
						reqTime_m = 0
						reqTime_s = 0
				else:
					reqTime_s = int(timenum)
				reqTime = timedelta(days = reqTime_d, hours = reqTime_h, minutes = reqTime_m, seconds = reqTime_s)
				
				try:
					Elapsed_time
				except:
					RaiseWarming('Requested time available, will use req. time assuming time limit end.')
					Elapsed_time = reqTime


		print()
		Report('name:'+'.'.join(k for k in iRunName.split('.')[:-1]), NewLine=True)

if not FoundSubmit:
	print(' ' * 8 + '> Submit file not found, look like a local run')




#### ---------------------------------------------------------------- INCAR check
StartSection(next(SectNumber), 'Looking for INCAR file')
if 'INCAR' in FileList:
	# try:
	# Open
	with open('INCAR') as f:
		INCARfile = f.readlines()
	INCAR = {iLine.split('=')[0].strip():iLine.split('=')[1] for iLine in INCARfile if '=' in iLine}
	# clean dictionary
	INCAR_cleaning_list = []
	# Identify what to delete
	for dkey in INCAR:
		if bool([b for b in dkey if b in ["!", "#"]]):
			INCAR_cleaning_list.append(dkey)
	#delete it
	for dkey in INCAR_cleaning_list:
		INCAR.pop(dkey)

	# Check runtype
	if 'IBRION' in INCAR:
		IBRION = int(INCAR['IBRION'])
		Report('INCAR file found', end='')

	# Check optimizers
	Henk, POTIM = (False, False)
	if 'POTIM' in INCAR: POTIM = float(INCAR['POTIM'])
	if POTIM == 0. and 'IOPT' in INCAR and int(INCAR['IBRION']) == 3:
		Henk = True
		IOPT = int(INCAR['IOPT'])

	# Check neb/home/seba/Thesis/Tools_Develop/FinalCheck/VASP.FinalCheck.py
	neb, nebclimb = (False, False)
	if IBRION in [1,2,3]:
		if 'IMAGES' in INCAR:
			neb = True
			IMAGES = int(INCAR['IMAGES'])
			if 'LCLIMB' in INCAR and INCAR['LCLIMB']:
				nebclimb = True

	# Report runtype
	if IBRION in [5,6,7,8]:
		print('IBRION='+str(IBRION)+', frequency calculation')
	elif IBRION == -1:
		print('Static run, IBRION='+str(IBRION))
	elif neb:
		print('neb path: IMAGES=' + str(IMAGES)+', climbing='+str(nebclimb), end='')
		if Henk:
			print(', Henkelman optimizer='+str(IOPT), end='')
		else:
			print(', optimizer='+str(IBRION), end='')
		print()

	elif IBRION in [1,2]:
			print('IBRION='+str(IBRION)+', geometry relaxation')
	elif Henk and IBRION == 3:
		print('Henkelman optimizer IOPT='+str(IOPT))

	else:
		# IBRION = 3 not henkelman
		print('IBRION=' + str(IBRION) + ', molecular dynamics evolution')



	# Parallelization
	Report('Parallelization', end='')
	NPAR, KPAR, NCORE = (False, False, False)
	if 'NPAR' in INCAR:
		NPAR= int(INCAR['NPAR'])
		print('NPAR=' + str(NPAR), end=' ')
	if 'KPAR' in INCAR:
		KPAR= int(INCAR['KPAR'])
		print('KPAR=' + str(KPAR), end=' ')
	if 'NCORE' in INCAR:
		NCORE = int(INCAR['NCORE'])
		print('NCORE=' + str(KPAR), end=' ')

	if not (KPAR or NPAR or NCORE):
		print('Not found, probably a serial run', end='')
	print()




	# except:
	# 	RaiseWarming('Something went wrong when looking for info in the INCAR file')


else:
	print("INCAR file not found. That is weird, better take a closer look!")






#### ---------------------------------------------------------------- log info
def CountSteps(iFile):
	scpCounter=0
	geomCounter=0
	with open(iFile) as f:
		loglines=f.readlines()
	for line in [iLine for iLine in loglines if len(iLine.split())>1]:
		if line.split()[0] in ['DAV:','RMM:']: scpCounter+=1
		if 'E0=' in line.split(): geomCounter+=1
	return scpCounter, geomCounter




StartSection(next(SectNumber), 'Looking for log/stdout/OSZICAR files')
if neb:
	ListCounter = []

	nebFolders = ["{:02d}".format(i)+'/' for i in range(1,IMAGES+1)]
	for iFolder in nebFolders:
		iscp, igeom = CountSteps(iFolder+'/OSZICAR')
		# print(iFolder+':'+str(iscp)+', '+str(igeom))
		ListCounter.append((igeom, iscp))

	# print(ListCounter)

	totalscp = sum([i[1] for i in ListCounter])

	Report('neb OSZCAR files', 'total scp='+str(totalscp)+', geom steps='+str(ListCounter[0][0]))

	Report('Detailed per (image)geo/scp',end='')
	for i in range(len(nebFolders)):
		print('('+nebFolders[i][:-1]+')'+str(ListCounter[i][0])+'/'+str(ListCounter[i][1]), end=' ')
	print()

else:
	for iFile in FileList:
		if 'logfile' in iFile or 'Logfile' in iFile or 'log' in iFile:
			LogFile = iFile
			print(' '*8+StrFixDot('> Logfile found ',DotL)+' : '+LogFile, end =' , ')

			scpCounter, geomCounter = CountSteps(LogFile)

			print('scp count : '+str(scpCounter), end=' , ')
			print('geom count : ' + str(geomCounter))
			Eff_str = ""
			try:
				Eff_str += 't/scp       : ' + "{:.2f}".format(Elapsed_time.total_seconds()/scpCounter).rjust(10) + " s     = " + \
							"{:.2f}".format(Elapsed_time.total_seconds()/(scpCounter*60)) + " min"
				print(' ' * (11+DotL) + Eff_str)
			except:
				pass
			Eff_str = ""
			try:
				Eff_str += '(t*cpu)/scp : ' + "{:.2f}".format(cpus * Elapsed_time.total_seconds()/scpCounter).rjust(10) + " cpu-s = " + \
							"{:.2f}".format(cpus * Elapsed_time.total_seconds()/(scpCounter*60)) + " cpu-min"			
				print(' ' * (11+DotL) + Eff_str)
			except:
				pass
				print(' ' * (11+DotL) + Eff_str)




	# else: print(' '*4+'>>>> Did not found a logfile of the run')





#### ---------------------------------------------------------------- OUTCAR info
if not neb:
	StartSection(next(SectNumber),'Looking for OUTCAR/OSZICAR files')

	print(' '*8+StrFixDot('> Opening OUTCAR ',DotL), end=' : ')
	with open('OUTCAR', 'r') as f:
		OUTCARlines = f.readlines()
		f.close()
	print('Ok', end=', ')

	if 'Voluntary context switches:' in OUTCARlines[-1]:
		print('properly finished run')
	else:
		print()
		RaiseWarming('Interrupted run')



	# Check IBRION
	for nLine, iLine in enumerate(OUTCARlines):
		if len(iLine.split()) > 3:
			if 'IBRION' in iLine.split():
				IBRION=int(iLine.split()[2])
				print(' '*8+StrFixDot('> Recognize run type ',DotL)+' : '+str(IBRION),end=', ')
				if IBRION in [1,2]:
					print('geometry relaxation')
				elif IBRION == -1:
					print('static')
				elif IBRION in [5,6,7,8]:
					print('frequency ', end="")
					for k in range(50):
						if "NFREE" in OUTCARlines[nLine+k]:
							print(", "+OUTCARlines[nLine+k].split()[2], end=" x ")
						if "POTIM" in OUTCARlines[nLine+k]:
							print("step="+OUTCARlines[nLine+k].split()[2], end="")
					print()
				elif Henk:
					print(' geometry relaxation, Henkelman optimizer=' + str(IOPT))
				else: print('')

	# Check convergece parameters
	GotEDIFFG = False
	GotEDIFF = False
	for iLine in OUTCARlines:
		if "EDIFFG" in iLine:
			OUTCAR_EDIFFG = float(iLine.split()[2])
			GotEDIFFG = True
		if "EDIFF" in iLine and not "EDIFFG" in iLine:
			OUTCAR_EDIFF = float(iLine.split()[2])
			GotEDIFF = True
		if (GotEDIFFG and GotEDIFF):
			break
	Report("Convergence: Electr = "+str(OUTCAR_EDIFF), end = '', NewLine=True)
	if IBRION in [1,2,3]:
		print(" , Geom = "+str(OUTCAR_EDIFFG))
	else:
		print("")


	# Dispersion correction
	if IBRION in [-1,1,2,3]:
		GotD3 = False
		print(' '*8+StrFixDot('> Dispersion correction ',DotL),end=' : ')
		for iLine in range(len(OUTCARlines)):
			ThisLine = OUTCARlines[len(OUTCARlines) - iLine - 1]

			if GotD3 == False:
				if 'IVDW' in ThisLine:
					GotD3 = True
					# Dispersion type
					print('found IVDW='+ThisLine.split()[2],end=', ')
					for i in OUTCARlines[len(OUTCARlines) - iLine - 2].split(): print(i, end=' ')
					print()
					# Dispersion energy
					while ' Edisp' not in OUTCARlines[len(OUTCARlines) - iLine - 2]: iLine+=1
					print(' ' * (11+DotL) + 'correction @ last geometry      = ' +
						   OUTCARlines[len(OUTCARlines) - iLine - 2].split()[2] + ' eV')
					break
		if GotD3 == False: print('Not found')


	# Recorre hacia arriba
	if IBRION in [-1, 1,2,3]:
		print(' '*8+StrFixDot('> Checking final energies/mag ',DotL), end=' : ')
		GotDipol = False; GotLastE = False
		for iLine in range(len(OUTCARlines)):
			ThisLine = OUTCARlines[len(OUTCARlines) - iLine - 1]

			if GotDipol == False:
				if "dipol+quadrupol energy correction" in ThisLine:
					GotDipol = True
					LastDipol = float(ThisLine.split()[3])
					print('found last dipole correction    = '+"{:.8f}".format(LastDipol)+' eV')

			if "  energy without entropy =" in ThisLine:
				try:
					LastE = float(ThisLine.split()[7])
					LastTOTEN = float(OUTCARlines[len(OUTCARlines) - iLine - 3].split()[4])
				except:
					LastE = 0.
					LastTOTEN = 0.
					print("\n"+" "*18+">> !! Something wrong in file line " + str(len(OUTCARlines) - iLine - 1 +1))
					print(" "*18 + ThisLine)
				GotLastE = True

			if GotLastE==True:
				if not GotDipol:
					print("Dipol energy not found")
				Report('Last Energy (raw DFT, TOTEN)     = '+str(LastTOTEN)+' eV', NewLine=True)
				Report('Last Energy (raw DFT, sigma->0)  = '+str(LastE)+' eV', NewLine=True)
				break
		if not GotLastE:
			print('Couldn\'t find any energy')
		# Last TOTEN
		try:
			EnergiesExtracted = subprocess.check_output("grep 'free  energy   TOTEN' OUTCAR",
														shell=True, text=True).rstrip().lstrip().split('\n')
			Report(f'Last TOTEN (completed geom step) = {EnergiesExtracted[-1].split()[4]} eV', NewLine=True)
		except:
			pass
		# Last mag
		try:
			MagExtracted = subprocess.check_output("grep 'mag' OSZICAR",
												   shell=True, text=True).rstrip().lstrip().split('\n')
			Report(f'Last magnetization (OSZICAR)     = {MagExtracted[-1].split("mag=")[1].rstrip().lstrip()} muB',
				   NewLine=True)
		except:
			pass







	# Recorre hacia arriba
	if IBRION in [1,2,3]:
		print(' '*8+StrFixDot('> Checking convergence ',DotL), end=' : ')
		Convergido = False; GotE = False
		for iLine in range(len(OUTCARlines)):
			ThisLine = OUTCARlines[len(OUTCARlines) - iLine - 1]

			if Convergido == False:
				if ThisLine == " reached required accuracy - stopping structural energy minimisation\n":
					Convergido = True
					print('reached geometric convergence, yay !!!!')
				continue
			else:
				if len(ThisLine.split())>4:
					if ThisLine.split()[4] == "energy(sigma->0)" :
						ConvergedEnery = float(ThisLine.split()[6])
						LastTOTENEnery = float(OUTCARlines[len(OUTCARlines) - iLine - 3].split()[4])
						if GotDipol and GotLastE:
							Report('Recomputed dipol corr (sigma->0) = '+"{:.8f}".format(ConvergedEnery-LastE)
								   + " eV", NewLine=True)
							Report('Recomputed dipol corr (TOTEN)    = '+"{:.8f}".format(LastTOTENEnery-LastTOTEN)
								   + " eV", NewLine=True)
						Report('Energy (sigma->0)     = '+ThisLine.split()[6]+' eV', NewLine=True)
						Report('TOTEN Energy (+dipol) = '+OUTCARlines[len(OUTCARlines) - iLine - 3].split()[4]+' eV', NewLine=True)
						GotE = True
					else:
						continue
				else:
					continue
			if GotE==True:
				print(' '*4+'Done!')
				quit()
		if not GotE:
			print('Couldn\'t find geometric convergence')
			print(' ' * 4 + 'Done!')

	elif IBRION in [-1]:
		print(' '*8+StrFixDot('> Checking Single Point ',DotL), end=' : ')

		SinglePointConvergido = False;
		for iLine in range(len(OUTCARlines)):
			ThisLine = OUTCARlines[len(OUTCARlines) - iLine - 1]

			if "  energy  without entropy=" in ThisLine:
				SinglePointConvergido = True
				ConvergedEnergy = float(ThisLine.split()[6])
				if GotDipol and GotLastE:
					print('Recomputed dipol corr = ' + "{:.8f}".format(ConvergedEnergy - LastE))
				Report('Energy (sigma->0) = ' + ThisLine.split()[6] + ' eV', NewLine=True)

			if SinglePointConvergido==True:
				print(' '*4+'Done!')
				quit()


		if not SinglePointConvergido:
			print(' '*7+'> Couldn\'t find last converged scf energy')
			print(' ' * 4 + 'Done!')







	elif IBRION in [5,6,7,8]:
		print(' '*8+StrFixDot('> Frequencies found ',DotL), end=' : ')
		#TODO: Add list
		tmpFreqListR = []
		tmpFreqListI = []
		Separe	= True
		for iLine in OUTCARlines:
			if 'THz' in iLine.split():
				# Real freqs
				if iLine.split()[1] == 'f':
					tmpFreqListR.append(float(iLine.split()[7]))
					print(StrFix(iLine.split()[0],2),end=' ')
					print('f   = ', end='')
					print(StrFix(iLine.split()[7],12),end=' ')
					print(StrFix(iLine.split()[8], 4),end=' ')
					print(StrFix(iLine.split()[9],12), end=' ')
					print(StrFix(iLine.split()[10],4))
				elif iLine.split()[1] == 'f/i=':
					if Separe == True:
						print('-'*45+'\n'+' '*(11+DotL), end='')
						Separe = False

					tmpFreqListI.append(float(iLine.split()[6]))
					print(StrFix(iLine.split()[0],2),end=' ')
					print('f/i = ', end='')
					print(StrFix(iLine.split()[6],12),end=' ')
					print(StrFix(iLine.split()[7], 4),end=' ')
					print(StrFix(iLine.split()[8],12), end=' ')
					print(StrFix(iLine.split()[9],4))
				print(' '*(11+DotL),end='')
		# List
		print('\n'+' '*10+'Real Freqs (cm-1): '+str(tmpFreqListR))
		print(' ' * 10 + 'Img  Freqs       : ' + str(tmpFreqListI))



		print('\n'+' ' * 4 + 'Done!')




	else: print(' ' * 4 + 'Done!')

