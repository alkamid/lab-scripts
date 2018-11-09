import meep as mp
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Patch
from matplotlib.ticker import FormatStrFormatter
from solvers import triangular

num_bands = 2
resolution = 32

ms = triangular()
ms.num_bands = num_bands
ms.resolution = resolution

num_x = 30
results = []
radii = np.linspace(0, 0.5, num=num_x)
for r in radii:
    geometry = [mp.Cylinder(r, material=mp.Medium(epsilon=12.96))]
    ms.geometry = geometry
    ms.run_tm()
    if len(ms.gap_list) > 0:
        results.append(ms.gap_list[0])
    else:
        results.append((0, 0, 0))

polypoints = [(r, b[2]) for r, b in zip(radii, results) if b != (0, 0, 0)]
polypoints.extend([(r, b[1]) for r, b in zip(radii, results) if b != (0, 0, 0)][::-1])

max_idx = np.argmax([b[0] for b in results])
max_gap_centre = np.mean(results[max_idx][1:])
max_gap_half = results[max_idx][2] - max_gap_centre

matplotlib.rcParams['axes.labelsize'] = 18
matplotlib.rcParams['xtick.labelsize'] = 14
matplotlib.rcParams['ytick.labelsize'] = 14
matplotlib.rcParams['legend.fontsize'] = 14

fig, ax = plt.subplots(constrained_layout=True)
poly = Polygon(polypoints)
ax.errorbar(radii[max_idx], max_gap_centre, yerr=max_gap_half, color='black')
ax.plot([radii[max_idx], 0.5], [results[max_idx][2]]*2, color='black', ls=':', alpha=0.5)
ax.plot([radii[max_idx], 0.5], [results[max_idx][1]]*2, color='black', ls=':', alpha=0.5)
ax.axvline(radii[max_idx], ls='--', color='black', alpha=0.5, zorder=3)
ax.add_patch(poly)
ax.legend(handles=[Patch(facecolor='C0', label='first photonic band gap')], loc='upper right')
ax.set_xlim([0, 0.5])
ax.set_ylim([0.15, 0.4])
axy = ax.twinx()
axy.set_xlim([0, 0.5])
axy.set_ylim([0.15, 0.4])
axy.set_yticks([results[max_idx][2], results[max_idx][1]])
axy.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
ax.set_xlabel(r'pillar radius / $r/a$')
ax.set_ylabel(r'frequency / $\omega a/2\pi c$')
fig.savefig('bandgap_vs_ratio.pdf')

plt.show()