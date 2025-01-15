#!/usr/bin/env python3


print('    Registra OUTCAR de corrida de frecuencia con ajuste dipolar calculando intensidades IR  ')


# -------------------------------------------------------------------------------------------------
# Tools
# -------------------------------------------------------------------------------------------------
def print2file(fileObj, string):
	print(string)
	fileObj.write(string)
	

# -------------------------------------------------------------------------------------------------
# Get data
# -------------------------------------------------------------------------------------------------
print('        > Abriendo OUTCAR ...', end=' ')
with open('OUTCAR', 'r') as f:
	content = f.readlines()
	f.close()
print('Ok')

# -------------------------------------------------------------------------------------------------
# File management - Inicia
# -------------------------------------------------------------------------------------------------
Log = open('IR.log', 'w')


# -------------------------------------------------------------------------------------------------
# Checks iniciales
# -------------------------------------------------------------------------------------------------
print("        > Checkeos iniciales :\n            ", end="")


iLineLog = 0
#Buscando NIONS
for iLine in range(len(content)):
	if "NIONS" in content[iLine]:
		NIONS=int(content[iLine].split()[11])
		print("NIONS = "+str(NIONS), end=" ; ")
		iLineLog=iLine
		break

# Buscando IBRION = 5
for iLine in range(iLineLog, len(content)):
	if len(content[iLine])<10: continue
	if content[iLine][:11] == "   IBRION =":
		if content[iLine].split()[2] == "5":
			print("IBRION = 5", end=" ; ")
			iLineLog = iLine
		else:
			print("Cálculo no de frecuencia. Bye!")
			quit()
		break

# Buscando NFREE
for iLine in range(iLineLog, len(content)):
	if not "NFREE" in content[iLine]: continue
	print("NFREE = "+content[iLine].split()[2], end=" ; ")
	iLineLog=iLine
	if not int(content[iLine].split()[2]) == 2:
		print("... aún no programado"); quit()
		
		

# Buscando POTIM
for iLine in range(iLineLog, len(content)):
	if len(content[iLine])<10: continue
	if content[iLine][:11] == "   POTIM  =":
		stepsize = float(content[iLine].split()[2])
		print("Stepsize ="+str(stepsize))
		break

# Buscando grados de libertad
print("            ", end="")
for iLine in range(iLineLog, len(content)):
	if "Degrees of freedom" in content[iLine]:
		DOF = int(content[iLine].split()[5])
		print("Grados de libertad="+str(DOF), end=" ; ")
		NSTEPS = 2*DOF+1
		print("Etapas="+str(NSTEPS))
		break

# Cantidad de momentos dipolares 
print("            ", end="")
NDipol = 0
for iLine in range(len(content)):
	if "dipolmoment" in content[iLine]: NDipol+=1
print("Dipolos reportados = "+str(NDipol), end=" -> ")

if NDipol == NSTEPS:
	print(" reporta en cada paso iónico")
else: 
	print("reporta en cada paso scf, NO PROGRAMADO AÚN")
	quit()

# -------------------------------------------------------------------------------------------------
# Obtener momentos dipolares y posiciones desplazadas
# -------------------------------------------------------------------------------------------------

# Ubica momentos dipolares
print("        > Recopilando coordenadas desplazadas y momentos dipolares", end=" ... ")
dipolmoments=[]; desplPos=[]; iStep=0; iLine=0
while iLine < len(content):
	if iStep == NSTEPS: break 
	if "dipolmoment" in content[iLine]:
		ThisLine=content[iLine].split()
		dipolmoments.append([float(ThisLine[1]),float(ThisLine[2]),float(ThisLine[3])])
		iStep+=1
		# Avanza hasta posiciones asociadas
		while not "POSITION" in content[iLine]:
			iLine+=1
		#Recoge posiciones
		iLine+=2; tmpdesplPos=[]
		for iAtom in range(NIONS):
			ThisLine=content[iLine].split()
			for iCoord in range(3):
				tmpdesplPos.append(float(ThisLine[iCoord]))
			iLine+=1
		desplPos.append(tmpdesplPos)
	else:
		iLine+=1

print(str(iStep)+" guardados")

# Debug
#print("dipolmoments")
#for i in dipolmoments:
#	print(i)
#print("...........................")
#print("desplPos")
#for i in desplPos:
#	print(i)
#print("...........................")



# -------------------------------------------------------------------------------------------------
# Genera derivadas - Asume NFREE=2
# -------------------------------------------------------------------------------------------------
print("        > Calculando derivadas centrales", end=" ... ")
dipolDer=[]
for iDOF in range(1,DOF+1):
	forwDipol=dipolmoments[2*iDOF-1]
	backDipol=dipolmoments[2*iDOF]
	tmpDer=[]
	for i in range(3):
		tmpDer.append((forwDipol[i]-backDipol[i])/(2*stepsize))
	dipolDer.append(tmpDer)
print(str(len(dipolDer))+" obtenidas")

# Debug
#print("dipolDer")
#for i in dipolDer:
#	print(i)
#print("---------------------------------------------------------")



# -------------------------------------------------------------------------------------------------
# Genera kernel de desplazamientos atómicos
# -------------------------------------------------------------------------------------------------

#Genera vectores de diferencia
print("        > Calculando vectores en kernel de desplazamientos", end=" ... ")
kernelDesp=[]
for iDOF in range(1,DOF+1):
	forwCoord=desplPos[2*iDOF-1]
	backCoord=desplPos[2*iDOF]
	tmpDespKernel=[]
	for iCoord in range(len(forwCoord)):
		tmpDespKernel.append(forwCoord[iCoord]-backCoord[iCoord])
	kernelDesp.append(tmpDespKernel)
print(str(len(kernelDesp))+" obtenidos")

# Debug
#print("kernelDesp")
#for i in kernelDesp:
#	print(i)
#print("-------------------------------------------------")



# -------------------------------------------------------------------------------------------------
# Componiendo Tensor = Gradiente del campo de momentos dipolares
# Estructura : DipolTensorBase[Desplazamiento][Coordenada base i de desplazamiento] 
#				= [vector derivada direccional de momento dipolar en coordenada base i]
# Estructura : DipolTensor[Desplazamiento][x,y ó z]
# -------------------------------------------------------------------------------------------------

#Recorre NIONS en tres coordenadas compilando bases
print("        > Generando base de Tensor gradiente del campo vectorial de momentos dipolares")
DipolTensorBases=[]
for iBase in range(len(kernelDesp)):
	tmpDipolBase=[]	
	for iDesp in kernelDesp[iBase]:
		if iDesp == 0.0: tmpDipolBase.append([0.,0.,0.])
		else: tmpDipolBase.append(dipolDer[iBase])
	DipolTensorBases.append(tmpDipolBase)
	

# Debug
#print(" Debug DipolTensorBase: por modo")
#debugdesp=1
#for i in DipolTensorBases:
#	print("Despl ="+str(debugdesp))
#	for j in i:
#		print(j)
#	debugdesp+=1
#	print("--  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  ")
#print(" Debug DipolTensorBase: compilado")
#for i in DipolTensorBases:
#	print(i)
#print("............................")


# Compila tensor
DipolTensor=[]
for iDespl in range(len(DipolTensorBases[0])):
	#print("DESPL="+str(iDespl)+".............")
	NewDipol=[0.,0.,0.]
	for iDespBase in range(DOF):
		#print("iDesplBase ="+str(iDespBase))
		#print(DipolTensorBases[iDespBase][iDespl])
		for iCoord in range(3):
			NewDipol[iCoord]+=DipolTensorBases[iDespBase][iDespl][iCoord]
	DipolTensor.append(NewDipol)
	

# Degub
#print(" Debug DipolTensor")
#for i in DipolTensor:
#	print(i)
#print("-.-.--.-.-.-.-.-.-.-.-..-.-.-.-.-.-.-.-.-.")


# -------------------------------------------------------------------------------------------------
# Obtiene modos y frecuencias
# -------------------------------------------------------------------------------------------------
print("        > Extrayendo frecuencias y modos de vibración")
freqR=[]; freqI=[]; ModePos=[]; ModeDespl=[]; MagImg=[]
for iLine in range(len(content)):
	# Find Freq
	if not "THz" in content[iLine]: continue
	ThisLine=content[iLine].split()
	if ThisLine[1] == "f":
		freqR.append(float(ThisLine[7]))
	else:
		freqI.append(float(ThisLine[6]))
		MagImg.append(float(ThisLine[8]))
	#Get Modes
	tmpModePos=[]; tmpModeDespl=[]
	for iAtom in range(NIONS):
		ThisLine=content[iLine+2+iAtom].split()
		for iCoord in range(3):
			tmpModePos.append(float(ThisLine[iCoord]))
			tmpModeDespl.append(float(ThisLine[iCoord+3]))
	ModePos.append(tmpModePos)
	ModeDespl.append(tmpModeDespl)

# Debug
#print("ModeDespl")
#for i in ModeDespl:
#	print(i)
#print("------------------------------------------------")
#print("ModePos")
#for i in ModePos:
#	print(i)

print("            Se identifican "+str(len(freqR))+" frecuencias reales y "+str(len(freqI))+" imaginarias")
if len(freqI) > 0:
	print("\n            !!!!!!!!!! Frecuencias imaginarias encontradas !!!!!!!!!!")
	for i in range(len(freqI)):
		tmpStrImg = "            !!    freq = "+str("{:.2f}".format(freqI[i]))
		while len(tmpStrImg)<32: tmpStrImg+=" "
		tmpStrImg+=" cm⁻1      mag = "+str("{:.4f}".format(MagImg[i]))
		while len(tmpStrImg)<67: tmpStrImg+=" "
		print(tmpStrImg+"!!")
	print("            !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
print("            Se obtienen "+str(len(ModePos))+" configuraciones y "+
	  str(len(ModeDespl))+" modos de vibración correspondientes")

if len(freqI) > 0:
	print("            De estos, sólo se calculará la intensidad de los "+str(len(freqR))+" modos reales\n")


# -------------------------------------------------------------------------------------------------
# Normalizando modos de vibración
# -------------------------------------------------------------------------------------------------
print("        > Re-normalizando modos de vibración por precaución")
ModeDesplNormal=[]
for iMode in ModeDespl:
	ModuloSum=0.
	for j in iMode:
		ModuloSum+=j**2
	Modulo=ModuloSum**(0.5)
	#print("Mode Modulo="+str(Modulo))

	tmpMode=[]
	for j in iMode:
		tmpMode.append(j/Modulo)
	ModeDesplNormal.append(tmpMode)


# Debug
#print("ModeDesplNormal")
#for i in ModeDesplNormal:
#	print(i)
#print(".....................................")
	

# -------------------------------------------------------------------------------------------------
# Proyectando tensor en modo de vibración
# Genera DirecDipolDeriv[Mode][x,y ó z]
# -------------------------------------------------------------------------------------------------
print("        > Proyecta tensor dipolar en Modos normales de vibración")
DirectDipolDeriv=[]
for iMode in ModeDesplNormal:
	tmpDirectDipolDeriv=[0.,0.,0.]
	for iCoord in range(3):
		for i in range(len(DipolTensor)):
			tmpDirectDipolDeriv[iCoord]+=iMode[i]*DipolTensor[i][iCoord]
	DirectDipolDeriv.append(tmpDirectDipolDeriv)
		
# Debug
# print("Debug DirectDipolDeriv")
# for i in DirectDipolDeriv:
# 	print(i)
# print("..............................................")
	
# -------------------------------------------------------------------------------------------------
# Estimando intensidades relativas - Agrupa x, y, z
# -------------------------------------------------------------------------------------------------
print("        > Estimando intensidades relativas ")
Intensities=[]
for iDirectDipolDeriv in DirectDipolDeriv:
	tmpIntensity=0
	for i in range(3):
		tmpIntensity+=iDirectDipolDeriv[i]**2
	Intensities.append(tmpIntensity)


# Debug
#print("Intensities")
#print(Intensities)


# -------------------------------------------------------------------------------------------------
# Lorentz Peaks
# -------------------------------------------------------------------------------------------------
print("        > Generando peaks de Lorentz")
width=80

# Distribución lawrentziana
def LawrProb(iFreq, iFreq0, iWidth, iFactor):
	tmpNum=iWidth/2.
	tmpDen=(iFreq-iFreq0)**2+(iWidth/2.)**2
	return iFactor*(tmpNum/tmpDen)

# Peaks
IntensitiesLawrentz=[]
for i in range(len(freqR)):
	IntensitiesLawrentz.append(LawrProb(freqR[i], freqR[i], width, Intensities[i]))


# -------------------------------------------------------------------------------------------------
# Reporte
# -------------------------------------------------------------------------------------------------
print("        > Reporte :\n            #    Frecuencia       Intensidad    Lorentz Peak")
Log.write(" Análisis de frecuencias IR\n    #    Frecuencia       Intensidad    Lorentz Peak\n")
for i in range(len(freqR)):
	tmpModeNumber=str(i+1)
	while len(tmpModeNumber)<5:
		tmpModeNumber+=" "

	tmpFreq=str("{:.2f}".format(freqR[i]))
	tmpFreqSpace=tmpFreq+"  "
	while len(tmpFreqSpace)<9:
		tmpFreqSpace+=" "
	tmpInt="{:.4E}".format(Intensities[i])
	tmpLorz="{:.10E}".format(IntensitiesLawrentz[i])

	print("            "+tmpModeNumber+tmpFreqSpace+"cm⁻1    "+tmpInt+"    "+tmpLorz)
	Log.write("    "+tmpModeNumber+tmpFreqSpace+"cm⁻1    "+tmpInt+"    "+tmpLorz+"\n")

print("        > Guardado en IR.log")

# -------------------------------------------------------------------------------------------------
# Serie Lorentz
# -------------------------------------------------------------------------------------------------
print("        > Generando serie Lorentz broadening", end=" ... ")
fMin=5; fMax=3900; step=1

# Generando serie de datos
IntensitySerial=[]; FreqSerial=[]
for i in range(fMax,fMin,-step):
	IntensitySerial.append(0.)
	FreqSerial.append(i)

for iMode in range(len(freqR)):
	for i in range(len(FreqSerial)):
		IntensitySerial[i]+=LawrProb(FreqSerial[i], freqR[iMode], width, Intensities[iMode])

#Traspasando a Log
Log.write("\n Serie de absorbancia\n")
for i in range(len(FreqSerial)):
	tmpFreq=str(FreqSerial[i])
	while len(tmpFreq)<8:
		tmpFreq+=" "

	tmpInt=str("{:.10E}".format(IntensitySerial[i]))

	Log.write("    "+tmpFreq+"  "+tmpInt+"\n")
print("guardado en IR.log")

# -------------------------------------------------------------------------------------------------
# Graficación
# -------------------------------------------------------------------------------------------------
qyPlot=input('        > Graficar? (y/n, def=s:save) : ')
if qyPlot == "n": 
	print("\n        Análisis terminado. Check IR.log")
	quit()

import matplotlib.pyplot as plt
#plt.plot(FreqSerial, IntensitySerial)
#plt.show()


# Basic Plot
fig = plt.figure()
plt.plot(FreqSerial, IntensitySerial)
plt.fill_between(FreqSerial, 0., IntensitySerial, alpha=0.2)

# Details
qyPlotFreq=input('        > Agregar freqs? (def=y/n)')
if not qyPlotFreq == 'n':
	# Hallar máximo
	tmpMaxBand=0.
	for i in range(len(freqR)):
		if IntensitiesLawrentz[i]> tmpMaxBand: tmpMaxBand=IntensitiesLawrentz[i]

	# Purgando menores
	FreqBandTol = 0.1 
	FreqBandList=[]
	for i in range(len(freqR)):
		if IntensitiesLawrentz[i]>tmpMaxBand*FreqBandTol/100:
			FreqBandList.append([freqR[i],IntensitiesLawrentz[i]])

	for i in range(len(FreqBandList)):
		plt.plot([FreqBandList[i][0], FreqBandList[i][0]], [0., FreqBandList[i][1]],'k', linewidth=0.5)


# Add-on s
plt.xlabel(r'cm-1')
plt.gca().invert_xaxis()
#plt.ylabel("Absorbancia")

# Guardar
if qyPlot != "y":
	print("        > Generando IR.plot")
	plt.savefig('IR.png', dpi=fig.dpi, bbox_inches='tight', pad_inches=0.5)

plt.show()

# -------------------------------------------------------------------------------------------------
# File management - Inicia
# -------------------------------------------------------------------------------------------------
Log.close()

