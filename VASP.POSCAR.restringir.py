#!/usr/bin/env python3


print('Modificar Selective dynamics de archivo en formato POSCAR/CONTCAR')

iFile = input('    Nombre de archivo : ') or "POSCAR"


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


# Get data
with open(iFile, 'r') as f:
	content = f.readlines()
	print('Abre archivo coordenadas')
	f.close()

# Top Box
iLine = 4
TopBox = content[0:iLine+1]
iLine+=1

# Nombres de atomos
if len(content[iLine].split()) == len(content[iLine+1].split()) and not content[iLine+1][0]=='S':
	print('    > Detecta nombres')
	NameList = content[iLine]
	groupList = content[iLine+1]
	nAtoms = int(SumLine(content[iLine+1]))

	iLine+=2
else:
	print('    > No detecta nombres')
	# get atoms names
	NameList = GetAtomNameList(content[iLine])
	groupList = content[iLine]
	nAtoms = int(SumLine(content[iLine]))
	iLine+=1

#Selective dynamics Line
if content[iLine][0]=='S':
	print('    > Detecta Selective dynamics previo')
	iLine+=1
else:
	print('    > Agrega Selective dynamics nuevo')

CoordSystem = content[iLine]
iLine+=1

Coords = content[iLine:iLine+nAtoms]
Footer = content[iLine+nAtoms:]
print('    >', nAtoms,' atomos')


################# Get frozen groups ####################
print('    Patron de congelado: #1 FTF #2 TTF #3 FTT ...')
FrozenPatern = input('                      >>')

PatternNumbers=[]; PatternCoords=[]
for i in range(int(len(FrozenPatern.split())/2)):
	PatternNumbers.append(int(FrozenPatern.split()[2*i]))
	PatternCoords.append(FrozenPatern.split()[2*i+1])

# Check cantidad
if not sum(PatternNumbers)== nAtoms:
	print('    ¡ Faltan o sobran atomos !   ')
	print('                    ... adios!'); quit()

FrozenVect = []
for i in range(len(PatternNumbers)):
	#prepara linea de coordenadas
	tmpStr=''
	for char in PatternCoords[i]:
		tmpStr+= char+' '
	
	#escribe linea de coordenadas
	for j in range(PatternNumbers[i]):
		FrozenVect.append(tmpStr)

################# Reescribe archivo ####################
print('Sobre escribiendo')
with open(iFile, 'w') as f:
	for i in TopBox:
		f.write(i)
	f.write(NameList)
	f.write(groupList)
	f.write('Selective dynamics\n')
	f.write(CoordSystem)

	for j in range(len(Coords)):
		tmpCoord = Coords[j].split()
		f.write(tmpCoord[0]+'  '+tmpCoord[1]+'  '+tmpCoord[2]+'  ')
		f.write(FrozenVect[j]+'\n')

	for k in Footer:
		f.write(k)
print('         fin!')


