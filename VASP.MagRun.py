#!/usr/bin/env python3

# V.2.7 - 27/jul/2022 - SAGG
print(' '*4+'Checking progress of relaxation/n')
print(' > Looking for OSZICAR files')

import matplotlib.pyplot as plt

try:
	with open('OSZICAR') as f:
		cont = f.readlines()

	ContMag = []
	for iLine in cont:
		if 'mag=' in iLine:
			ContMag.append(float(iLine.split()[9]))
	if ContMag==[]:
		print('  > Did not found any complete step reporting total magnetization')
		print('    Check OSZICAR, see how OUTCAR ended and that it is doing a ')
		print('    spin-polarized calcualtion (ISPIN=2), also verify your INCAR. Bye!')
		quit()
except:
	print(' >> Could not found or parse OSZICAR files, check the folder to see what\'s going on. Bye!')
	quit()

print(f' Got {len(ContMag)} total magnetization reported')

#### Plotting
# Create
fig, ax = plt.subplots(1,1, figsize=(6.5,4.), dpi=80)
ax.set_position([.15, .12, .8, .85])


RelativeScale = input(' '*4+'>> Relative scale (def=n/yes)            :')
if RelativeScale in ['y', 'yes', 'YES', 'Y']:
	RelativeScale=True
else:
	RelativeScale=False
# Relative Scale
if RelativeScale:
	Scale_base = float(int(ContMag[0]))
	plt.ylabel(r'Magnetization, [$\mu$B, OFfset=' + str(Scale_base) + '.0]')
else:
	Scale_base = 0.
	plt.ylabel(r'Magnetization, $\mu$B')
	ax.ticklabel_format(useOffset=False, axis='y')

# Add geom points
ax.plot([i+1 for i in range(len(ContMag))], 
	[i-Scale_base for i in ContMag], marker='+', markeredgecolor='k', linewidth=.5)


# Title
ax.set_title('Total magnetization\n whole cell', x=.95, y=.95, ha='right', va='top')
ax.ticklabel_format(useOffset=False)
# nice
ax.grid(which='both', linewidth=.5)

plt.xlabel('Iteration')



plt.show()
