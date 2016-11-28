import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from cycler import cycler

SUFFIXES = {1: 'st', 2: 'nd', 3: 'rd'}
def ordinal(num):
    suffix = SUFFIXES.get(num % 10, 'th')
    return str(num) + suffix

plt.rcParams['axes.labelsize'] = 'x-large'
plt.rcParams['xtick.labelsize'] = 'x-large'
plt.rcParams['ytick.labelsize'] = 'x-large'

fig = plt.figure()
ax = fig.add_subplot(111)
ax2 = ax.twinx()

NUM_COLORS = 7
cm = plt.get_cmap('Dark2')
ax2.set_prop_cycle(cycler('color', [cm(1.*i/NUM_COLORS) for i in range(NUM_COLORS)]))

data_r = []

with open('bandgap.out', 'r') as f:
    linecount = 0
    lines = f.readlines()
    i = 0
    while i < len(lines):
        if linecount == 0:
            bandslist = []
            lsp = lines[i].split(':')
            if lsp[0] == 'Geometric objects':
                i+=2
                linecount += 1
                r = float(lines[i].split()[1][:-1])
        elif linecount == 1:
            lsp = lines[i].split()
            if lsp[0] == 'Band' and lsp[1].isdigit():
                bandslist.append((int(lsp[1]), float(lsp[3]), float(lsp[9])))
            if lsp[0] == 'total':
                data_r.append((r, bandslist))
                linecount = 0
        i+=1

maxband = 0
for band in data_r[0][1]:
    if band[0] > maxband:
        maxband = band[0]

polypoints = [None]*maxband
diffs = [None]*maxband

minimum_gap_tol = 0.01

for band in range(maxband-1):
    for ratio in data_r:
        lowerMax = ratio[1][band][2]
        upperMin = ratio[1][band+1][1]

        if (upperMin > lowerMax + minimum_gap_tol):
            if not polypoints[band]:
                polypoints[band] = [[], []]
                diffs[band] = []
            if polypoints[band]:
                polypoints[band][0].append([ratio[0], lowerMax])
                polypoints[band][1].append([ratio[0], upperMin])
                diffs[band].append([ratio[0], (upperMin-lowerMax)/(0.5*(upperMin+lowerMax))])
ax.set_xlabel("r/a")
ax.set_ylabel("frequency / $\omega a/ 2 \pi c$")
ax.set_xlim(right=0.5)

#set good-looking limits of both y axes
patches_min = 0
for patch in polypoints:
    if patch:
        freqs = [p[1] for p in patch[0]]
        patches_min = min(freqs)
        break

patches_max = 0
for patch in polypoints[::-1]:
    if patch:
        freqs = [p[1] for p in patch[1]]
        patches_max = max(freqs)
        break

diffs_max = 0
for diff in diffs:
    if diff:
        m = max([d[1] for d in diff])
        if m > diffs_max:
            diffs_max = m

ax.set_ylim(top=1.1*patches_max)
ax2.set_ylim(top=diffs_max*1.1*patches_max/patches_min)


#counter to display ordinals properly (1st/2nd band etc.)
i = 1
for band in range(maxband):
    if polypoints[band]:
        polypoints[band][1] = polypoints[band][1][::-1]
        diffs[band]= np.array(diffs[band])

        poly = Polygon(np.vstack([np.array(polypoints[band][0]), np.array(polypoints[band][1])]), color='#377eb8')
        ax.add_patch(poly)
        ax2.plot(diffs[band][:,0], diffs[band][:,1], label="{0} bandgap size".format(ordinal(i)))
        ax.axvline(x=diffs[band][np.argmax(diffs[band][:,1])][0], linestyle='--', color='black')
        i += 1

ax2.legend(loc='upper left')
plt.suptitle("Bandgap size as a function of pillar-lattice constant ratio")
plt.savefig("bandgap-size.pdf")
plt.show()
