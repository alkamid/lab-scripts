import matplotlib.pyplot as plt
import numpy as np

modefile = np.loadtxt('modes.dat', skiprows=1)
freqfile = np.loadtxt('sweep.tm.dat', delimiter=',')

modes = [1,2,4,6]

mode_data = {}

for m in modes:
    mode_data[m] = [None]*len(freqfile)

for i, row in enumerate(modefile):
    for j, col in enumerate(row[1:]):
        c = int(col)
        if c in modes:
            mode_data[c][i] = freqfile[i][j+5]

radius_data = modefile[:,0]

fig = plt.figure()
ax = fig.add_subplot(111)

for m in mode_data:
    print(mode_data[m])

    ax.plot(radius_data, mode_data[m])

plt.show()
