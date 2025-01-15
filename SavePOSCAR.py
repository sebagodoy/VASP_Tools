#!/usr/bin/env python3

# packages
import numpy as np
import tkinter as tk
import os
# Data
def OpenParsePOSCAR(_iFile):
    with open(_iFile, 'r') as f:
        cont = f.readlines()
    Factor = float(cont[1])
    Cell = np.array([[float(j)*Factor for j in i.split()] for i in cont[2:5]])
    NAtoms = sum([int(i) for i in cont[6].split()])

    AtNamesNums = cont[5:9]
    AtomNameList = []
    for i,j in enumerate(AtNamesNums[1].split()):
        [AtomNameList.append(AtNamesNums[0].split()[i]) for k in range(int(j))]
    CoordSystem = cont[8]

    AtCoordDir = np.array([[float(j) for j in i.split()[:3]] for i in cont[9:9+NAtoms]])
    AtSelDyn = np.array([[j for j in i.split()[3:]] for i in cont[9:9+NAtoms]])
    AtCoordCart = np.array([np.dot(Cell.T, i) for i in AtCoordDir])
    Tail = cont[9+NAtoms+1:]

    return Cell, AtomNameList, NAtoms, CoordSystem, AtCoordDir, AtSelDyn, AtCoordCart, Tail

LargeLog = input(" Master file to drop new data : ") or "/media/seba/TOSHIBA EXT/PSMN_bkp/PSMN_runs/Articles/Article_DFT_PMe3_Ads/Geoms/MasterCoordinates.tex"
GeomFile = input(" Geometry to add              : ") or "./CONTCAR"
print("-"*60)
boolDir = True if input(" * Add folder (def True, * False)     : ") else False
boolCell = False if input(" * Add Cell (def False, * True)       : ") else True
boolCart = False if input(" * Use Cartesian (def False, * True) : ") else True
boolComment = False if input(" * Use Cartesian (def True, * False) : ") else True
print("-"*60)
SectionTitle = input(" >> Add section    : ") or False
SubSectionTitle = input(" >> Add subsection : ") or False

Cell, AtomNameList, NAtoms, _, _, _, AtCoordCart, _ = OpenParsePOSCAR(GeomFile)

def RemoveLastLine(iFile):
    with open(iFile, "r+", encoding = "utf-8") as file:
        file.seek(0, os.SEEK_END)
        pos = file.tell() - 1
        while pos > 0 and file.read(1) != "\n":
            pos -= 1
            file.seek(pos, os.SEEK_SET)
        if pos > 0:
            file.seek(pos, os.SEEK_SET)
            file.truncate()

def WriteToFile():
    inputValue=CommmentBox.get("1.0","end-1c")
    print(inputValue)
    # Remove last line from file
    RemoveLastLine(LargeLog)
    # Write Coordinates
    with open(LargeLog,'a', encoding='utf-8') as f:
        if SectionTitle:
            f.write("%" * 80 + "\n")
            f.write("%" * 80 + "\n\n")
            f.write("\\section{"+SectionTitle+"}\n\n")
        if SubSectionTitle:
            f.write("%" * 80 + "\n")
            f.write("%" * 80 + "\n\n")
            f.write("\\subsection{"+SubSectionTitle+"}\n\n")
        f.write("%" * 80 + "\n")
        f.write("%" * 80 + "\n\n")
        f.write("\\rule{\columnwidth}{.5pt} \\newline\n")
        f.write("\\colorbox{backcolour}{System :}\n")
        for j in inputValue.split('\n'):
            f.write(j+'\\newline\n ')
        # Writte cell
        if boolCell:
            f.write('%%%% Periodic cell\n ')
            f.write("\\normalsize\n")
            f.write('\\newline\\texttt{Periodic Cell :} \\par\n ')
            f.write('\\begin{lstlisting}\n')
            [f.write("  " + " ".join(["{:.16f}".format(iCo).rjust(21) for iCo in iCell]) + "\n") for iCell in Cell]
            f.write('\\end{lstlisting}\n')
            f.write("\n")
        # Coordinates
        f.write('%%%% Coordinates\n ')
        f.write('\\texttt{Cartesian coordinates ('+str(NAtoms)+' atoms):}\\par\n ')
        f.write('\\begin{lstlisting}\n')
        for iAtName, iAtCoor in zip(AtomNameList, AtCoordCart):
            f.write(iAtName.rjust(2))
            f.write(" ".join(["{:.16f}".format(iCo).rjust(20) for iCo in iAtCoor]) + "\n")
        f.write('\\end{lstlisting}')
        f.write("\n"*3)
        f.write("\\end{multicols*}\\end{document}")
    frame.quit()

frame = tk.Tk()
frame.title("Adding geometry to master file")
frame.geometry('800x200')




CommmentBox = tk.Text(frame, height = 5, width = 100)

CommmentBox.pack(padx=10, pady=10)


buttonCommit=tk.Button(frame, height=1, width=30, text="Add to master file & Close", command=lambda: WriteToFile())
buttonCommit.pack()

tk.mainloop()

print("-" * 40 + " Done!")
