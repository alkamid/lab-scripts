import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler

modefile = np.loadtxt('modes.dat', skiprows=1)
freqfile = np.loadtxt('sweep.tm.dat', delimiter=',')

modes = [1,2,4,6]

mode_data = {}

NUM_COLORS = 4
cm = plt.get_cmap('Dark2')

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
ax.set_prop_cycle(cycler('color', [cm(1.*i/NUM_COLORS) for i in range(NUM_COLORS)]))

labels = ['monopole', 'dipole', 'quadrupole', 'hexapole']

for i, m in enumerate(mode_data):
    ax.plot(radius_data, mode_data[m], lw=2, label=labels[i])

#ax.axhline(0.307)
#ax.axhline(0.229)
ax.axhspan(0.307, 0.32, color='#377eb8', zorder=3)
ax.axhspan(0.22, 0.229, color='#377eb8')
ax.set_ylim(bottom=0.22)
plt.legend(loc=(0.05, 0.1))
plt.savefig('modes_vs_def_radius.pdf')
plt.show()
