import meep as mp
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from solvers import triangular_with_defect, gaas


ms = triangular_with_defect()
ms.num_bands = 31
ms.k_points = [mp.Vector3(0., 0.5), ]


radii = np.linspace(0.25, 0.7, 60)
defect_freqs = np.zeros((6, radii.size))

for e, r in enumerate(radii):
    j = 0
    defect = mp.Cylinder(r, material=gaas)
    ms.geometry.append(defect)
    ms.run_tm()

    for i, freq in enumerate(ms.get_freqs()):
        if 0.229 < freq < 0.307:
            defect_freqs[j, e] = freq
            j += 1

new_freqs = defect_freqs.copy()
new_freqs[new_freqs == 0] = np.nan
fig, ax = plt.subplots()
labels = ['dipole', 'quadrupole', 'monopoole', 'hexapole']
for j, freq in enumerate([f for i, f in enumerate(new_freqs) if i not in (1,3)]):
    ax.plot(radii, freq, label=labels[j])
ax.set_ylim(bottom=0.2)
ax.set_xlim([radii[0], radii[-1]])
ax.fill_between(radii, 0.307, 0.35, facecolor='blue', alpha=0.5)
ax.fill_between(radii, 0.2, 0.229, facecolor='blue', alpha=0.5)
ax.set_xlabel('Defect radius')
ax.set_ylabel(r'frequency / $\omega\alpha/2\pi c$')
ax.legend(loc=(0.05, 0.27))

matplotlib.rcParams['axes.labelsize'] = 18
matplotlib.rcParams['xtick.labelsize'] = 14
matplotlib.rcParams['ytick.labelsize'] = 14
matplotlib.rcParams['legend.fontsize'] = 14

new_freqs = defect_freqs.copy()
new_freqs[new_freqs == 0] = np.nan
fig, ax = plt.subplots(constrained_layout=True)
labels = ['dipole', 'quadrupole', 'monopole', 'hexapole']
for j, freq in enumerate([f for i, f in enumerate(new_freqs) if i not in (1,3)]):
    ax.plot(radii, freq, label=labels[j])
bottom_limit = 0.225
top_limit = 0.31
ax.set_ylim(bottom=bottom_limit, top=top_limit)
ax.set_xlim([radii[0], radii[-1]])
axy = ax.twinx()
axy.set_ylim(bottom=bottom_limit*3e8/4.4e-5*1e-12, top=top_limit*3e8/4.4e-5*1e-12)
axy.set_ylabel('frequency / THz')
ax.fill_between(radii, 0.307, 0.35, facecolor='blue', alpha=0.5)
ax.fill_between(radii, 0.2, 0.229, facecolor='blue', alpha=0.5)
ax.set_xlabel(r'defect radius / $R/a$')
ax.set_ylabel(r'frequency / $\omega a/2\pi c$')
ax.legend(loc=(0.01, 0.05))
fig.savefig('modes_vs_def_radius.pdf')
