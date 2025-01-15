#!/usr/bin/env python3

#Reconoce variables
print('---------------------------------------------')
print(' Crea interpolación parabólica con imágenes')
print(' aproximadamente equidistantes')

#Get Coordenadas
print('---------------------------------------------')
fileIni = input('    Geometría inicial  : ')
while fileIni == '':
	fileIni = input('    Hey!, Geometría inicial  : ')

fileFin = input('    Geometría final    : ')
while fileFin == '':
	fileFin = input('    Hey!, Geometría final    : ')

fileTS = input('    TS aproximado      : ')
while fileTS == '':
	fileTS = input('    Hey!, TS aproximado      : ')

nImages = int(input('    Total de imágenes  : '))+2
if nImages == '' or nImages <=2:
	nImages = 6
	print("Se asume un mínimo de "+str(nImages)+" imágenes")



def ReadPOSCAR(filename):
	#Open file
	with open(filename,'r') as thisFile:
		content = thisFile.readlines()
	thisFile.close()
	
	#N atomos
	nAtoms = 0
	for iAtoms in content[6].split():
		nAtoms += int(iAtoms)
	
	#Separa cabecera
	header = content[0:9]
	
	#Crea coordenadas / letas
	coordenadas=[]; fixing = []
	for i in range(nAtoms):
		tmpLine = content[9+i].split()
		coordenadas.append([float(tmpLine[0]), float(tmpLine[1]), float(tmpLine[2])])
		fixing.append([tmpLine[3], tmpLine[4], tmpLine[5]])

	#Separa velocidades
	velBlock = content[9+nAtoms+1:]

	return header, nAtoms, coordenadas, fixing, velBlock


def ParabInter(x1, x2, x3, ntot, this):
	#Obtiene parámetros de parabola
	aa = 2.*x3+2.*x1-4.*x2
	bb = 4.*x2-x3-3.*x1
	cc = x1
	offset = (this-1.)/(ntot-1)#pasa # imagen a rango [0,1]
	
	xOUT = aa*(offset**2)+bb*offset+cc
	return xOUT

def Distance(v1, v2):
	d2=0.
	for xyz in range(3):
		d2+=(v2[xyz]-v1[xyz])**2
	return d2**0.5

print('---------------------------------------------')
print('    Preparando para crear imágenes I->TS->Fin')
print('    Leyendo imagenes')
Head1, nAt1, Coord1, Fix1, Vel1 = ReadPOSCAR(fileIni)
Head2, nAt2, Coord2, Fix2, Vel2 = ReadPOSCAR(fileFin)
HeadTS, nAtTS, CoordTS, FixTS, VelTS = ReadPOSCAR(fileTS)

#Detecta error 
if nAt1 != nAt2 or nAt2 != nAtTS:
	print('¡ ¡ ¡ Distintos poscar ! ! !'); quit()


#Creando archivos + agrega cabecera de inicial
print('---------------------------------------------')
print('    Creando archivos')
for iImg in range(nImages):
	ThisFileName = 'Img_'+str(iImg)
	with open(ThisFileName,'w') as file:
		file.writelines(HeadTS)

#Agrega interpolación de coordenadas por linea
import numpy as np

print('    Interpolando linea a linea')
print('                    ... demora')
for iLine in range(nAt1): #Avanza por linea

	#Crea vector puntos normalizados de interpolacion
	tVect = []
	for iImg in range(nImages): #Para cada imagen
		tVect.append(iImg+1)

	####
	#### Bloque de optimización de distancia de imagenes
	####


	#Tolerancia de desviacion
	Tol=0.0001; MaxStep=0.0005; CriterioOld=100
	#LoopCounter
	LoopCounter=0; MaxLoop=500000

	while LoopCounter < MaxLoop:
		#Crea matriz posiciones
		PosImgs=[]
		for iImg in range(nImages):
			newPos=[]
			for xyz in range(3): #Coordenada x, y, z
				xyzIni = Coord1[iLine][xyz]; xyzFin = Coord2[iLine][xyz]; xyzTS = CoordTS[iLine][xyz];
				newPos.append(ParabInter(xyzIni, xyzTS, xyzFin, nImages, tVect[iImg]))
			PosImgs.append(newPos)

		#vector de distancias
		dist=[]; distdesv=[]
		for i in range(1,nImages):
			dist.append(Distance(PosImgs[i],PosImgs[i-1]))
		#desviacion de distancias
		for i in range(1,nImages):
			distdesv.append(dist[i-1]-np.mean(dist))
		#Criterio maximo
		criterio=max(max(distdesv),abs(min(distdesv)))

		if criterio < Tol:
			break

		#Ajusta vector t
		for i in range(1,nImages-1):
			tVect[i]-=(distdesv[i-1]/criterio)*MaxStep

		LoopCounter+=1

	####
	#### Bloque de optimización de distancia de imagenes
	####

	if LoopCounter == MaxLoop:
		print('Equidistancia no lograda para at='+str(iLine+1)+'; crit='+str(criterio))


	#Escribe a archivo
	for iImg in range(nImages):
		ThisFileName = 'Img_'+str(iImg)
		with open(ThisFileName,'a') as file:
			for iCoord in PosImgs[iImg]:
				file.writelines(str('{:.16f}'.format(iCoord))+' ')		

	#Saca movilidad desde archivo TS
	for iImg in range(nImages):
		ThisFileName = 'Img_'+str(iImg)
		with open(ThisFileName, 'a') as file:
			for iFix in FixTS[iLine]:
				file.write(' '+iFix)
			file.write('\n')

#Agrega footer de inicial
print('    Obtiene congelamiento desde TS')
print('    Cerrando bloque de velocidades')
for iImg in range(nImages):
	ThisFileName = 'Img_'+str(iImg)
	with open(ThisFileName,'a') as file:
		file.write('\n')
		file.writelines(VelTS)

		
#Reorganiza
print('---------------------------------------------')
import os; import shutil
print('    Reordenando')
for iImg in range(nImages):
	if iImg<10:
		folderName = '0'+str(iImg)
	else:
		folderName = str(iImg)
	#Crea carpetas
	os.mkdir(folderName)
	#Mueve archivos
	ActualDir = './Img_'+str(iImg)
	NuevaDir = './'+folderName+'/POSCAR'
	shutil.move(ActualDir, NuevaDir)

print('    Finalizado, yay! ')
print('')

	




























