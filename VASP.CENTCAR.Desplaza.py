#!/usr/bin/env python3

################################################################
################################ V.0


print(' Genera coordenadas desplazadas desde CENTAR según un MODECAR\n')


######################### Tools:ini #########################
def SumLine(strline):
	nSum = 0.
	for iElement in strline.split():
		nSum+=float(iElement)
	return nSum

def GetAtomNameList(conjuntos):
	strline = input('    Lista de nombres atomicos: ')
	if not len(strline.split())==len(conjuntos.split()):
		print('        Nombres y # grupos de atomos no coinciden')		
		print('        . . . adios!')
		quit()
	NameList = ''
	for iName in strline.split():
		NameList+=iName+' '
	NameList+='\n'
	return NameList

######################### Tools:fin #########################
fileSystem = input('    > Use CENTCAR/MODECAR(1) or POSCAR(def=2) :') or '2'

if fileSystem == '1':
	iFile1 = input('    Archivo de geometría central (def=CENTCAR) : ') or 'CENTCAR'
	iFile2 = input('    Archivo de direcciones    (def=NEWMODECAR) : ') or 'MODECAR'
elif fileSystem == '2':
	iFile1 = input('    Archivo de geometría/dir.    (def=CONTCAR) : ') or 'CONTCAR'
	iFile2 = iFile1



######################################## Coordenadas centrales

# Get data
print("\n    > Abriendo "+iFile1, end=" ... ")
with open(iFile1, 'r') as f:
	content = f.readlines()
	f.close()
print('Ok')

# Top Box
TopBox = content[0:5]
print('    > Almacena Top Box')

iLine = 5
# Cantidad de átomos
if len(content[iLine].split()) == len(content[iLine+1].split()) and not content[iLine+1][0]=='S':
	print('    > Detecta formato con nombres')
	nAtoms = int(SumLine(content[iLine+1]))
	iLine+=2
else:
	print('    > Detecta formato sin nombres')
	nAtoms = int(SumLine(content[iLine]))
	iLine+=1
print('    > Detecta '+str(nAtoms)+' átomos en el sistema')


#Selective dynamics Line
if 'S' in content[iLine]:
	print('    > Detecta Selective dynamics previo')
	iLine+=2
else:
	print('    > No detecta Selective dynamics nuevo')
	iLine+=1

#Check tipo de coordenadas
if not 'D' in content[iLine-1]:
	print('    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
	print('    !! No detecta sistema de coordenadas directo  !!')
	print('    !! necesito eso para vivir, adios mundo cruel !!')
	print('    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
	quit()

# Mid Box
MidBox = content[5:iLine]
print('    > Almacena Mid Box')
#print(MidBox)
#print('------>'+str(iLine))

# Añade coordenadas
print('    > Obteniendo coordenadas relativas', end=' ... ')
CoordsCentral=[]; DynamicsCentral=[]
for i in range(nAtoms):
	ThisLine=content[iLine+i].split()
	CoordsCentral.append([float(ThisLine[0]), float(ThisLine[1]), float(ThisLine[2])])
	DynamicsCentral.append([ThisLine[3], ThisLine[4], ThisLine[5]])
print('Ok')
	
# Desecha Tail si existe




######################################## Dirección de desplazamiento

# Get data
if fileSystem == '1':
	print("\n    > Abriendo "+iFile2, end=" ... ")
	with open(iFile2, 'r') as f:
		content = f.readlines()
		f.close()
	print('Ok')

# Get desplazamientos
print('    > Obteniendo desplazamientos', end=' ... ')
Desplz=[]
if fileSystem == '1':
	for iLine in content:
		ThisLine = iLine.split()
		Desplz.append([float(ThisLine[0]), float(ThisLine[1]), float(ThisLine[2])])
elif fileSystem == '2':
	for iLine in content[iLine + nAtoms + 1 :]:
		_iLine = [float(i) for i in iLine.split()]
		if _iLine == []:
			break
		Desplz.append(_iLine)
print('Ok')

# Cantidades coinciden
if len(CoordsCentral) == len(Desplz): print('    > Cantidad de coordenadas coinciden')
else:
	print('    > Cantidad de coordenadas no coincide, '+str(len(CoordsCentral))+' en'+iFile1+'(coords.) y '+str(len(Desplz))+' en '+iFile2 +' (displ.)')
	print('    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
	print('    !! Qué? Así no se puede trabajar. !!')
	print('    !! Adios!                         !!')
	print('    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
	quit()

######################################## Archivos a generar

# Direcciones de imágenes
direct = input('\n    Dirección de desplazamiento (f/b/def=both) : ')
print(direct)
#if not direct=='f' or not direct=='b': direct='both'
if not direct: direct ='both'
print(direct)

# Cantidad de imágenes
nImages = input('    Cantidad de imágenes desplazadas (def=5)   : ')
if nImages == '': nImages = 5
else: nImages = int(nImages)

# Scale factor
ScaleFactor = input('    Scale of displacements (def=1.0)           : ') or 1.
ScaleFactor = float(ScaleFactor)

#### Deleting images at the end
if input('    Borrar imágenes individuales (def=y/n)') ==  'n': DelImg = False
else: DelImg = True

# Vector iterativo de desplazamientos
ImagenDesplaza = [0]
if direct == 'f' or direct == 'both':
	for i in range(nImages): ImagenDesplaza.append(i+1)
if direct == 'b' or direct == 'both':
	for i in range(nImages): ImagenDesplaza.append(-i-1)
MinDespl = min(ImagenDesplaza)


print('\n    > Generando desplazamientos : ')
FileMovList = []
for iDespl in ImagenDesplaza:
	print('      Imagen '+str('{:+2d}'.format(iDespl))+' en archivo : ', end='')
	ThisTitle='CONTCAR_'+iFile1+'_mv_'
	if iDespl == 0:ThisTitle+='central'
	elif iDespl > 0: ThisTitle+='forw_'+str(iDespl)
	else: ThisTitle+='back_'+str(iDespl-(MinDespl-1))

	FileMovList.append(ThisTitle)
	print(ThisTitle, end=' ... ')

	with open(ThisTitle, 'w') as f:
		for i in TopBox:
			f.write(i)
		for j in MidBox:
			f.write(j)

		for iAt in range(nAtoms):
			for jCoor in range(3):
				ThisCoord = CoordsCentral[iAt][jCoor]+iDespl*Desplz[iAt][jCoor]*ScaleFactor/100
				f.write('  '+str('{:.16f}'.format(ThisCoord)))
			for jDyn in range(3):
				f.write('   '+DynamicsCentral[iAt][jDyn])
			f.write('\n')
	print('Ok')

if not DelImg:
	print('\n'+' '*4+'> Revisar archivos con : VESTA '+'CONTCAR_'+iFile1+'_mv_*\n')




#### Generando XDATCAR5 vmd movie
def CodeStatus(istr): print(' '*4+'> '+istr)
def CodeError(istr): print(' '*4+'Error: '+istr)
def FixBlanck(iStr, **kwargs):
	length = kwargs.get('l', 10)
	strout = iStr
	if len(strout)<length: strout = ' '*(length-len(strout))+strout
	return strout

# Ordenando lista
# FileMovList.append()

ImagesCounter = 1
Head = None
Natoms = 0
OutFile = 'dimMovie_XDATCAR5'
FileMovList.sort()

try:
	for iImage in FileMovList:
		# print(iImage)
		with open('./' +iImage, 'r') as f:
			iGeom = f.readlines()

		#### First image: Get head ? -> Create OutFile
		if Head == None:
			#### Get head
			Head = iGeom[0:7]
			#### Get number of atoms
			try:
				for iAt in iGeom[6].split(): Natoms += int(iAt)
			except:
				CodeError('Atom type quantities not in 5th line. That POSCAR-type format is required. Bye!')
				break
			CodeStatus('Header properly retrieved, ' + str(Natoms) + ' atoms detected')
			#### Creating Output
			with open(OutFile, 'w') as f:
				for iLine in Head:
					f.write(iLine)
			CodeStatus('Created file ' + OutFile + ' to write movie un XDATCAR-vmd format')

		#### Check geometry format
		if not iGeom[8].split()[0][0] == 'D':
			CodeError('All images need to define a \'Direct\' geometry on the 9th line. Bye!')
			break

		#### Collect geometry
		with open(OutFile, 'a') as f:
			f.write('Direct configuration=' + FixBlanck(str(ImagesCounter), l=6) + '\n')
			for iAt in iGeom[9:9 + Natoms]:
				f.write(' ')
				for i in range(3): f.write('  ' + iAt.split()[i])
				f.write('\n')
		ImagesCounter+=1

	#### Line for final image
	with open(OutFile, 'a') as f: f.write('Direct configuration=' + FixBlanck(str(ImagesCounter), l=6) + '\n')

except:
	CodeError('Somethig were terribly wrong when creating the vmd XDATCAR5 movie, but everything else was ok. bye!')


if DelImg:
	import os
	for iImage in FileMovList:
		try:
			os.remove('./'+iImage)
		except:
			CodeError('Error trying to remove '+iImage)




	


