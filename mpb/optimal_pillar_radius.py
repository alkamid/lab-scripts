import meep as mp
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar

import solvers
from solvers import gaas

ms = solvers.triangular()
ms.num_bands = 2
ms.mesh_size = 8
ms.resolution = 64


def first_tm_gap(r):
    ms.geometry = [mp.Cylinder(r, material=gaas)]
    ms.run_tm()
    return -1 * ms.retrieve_gap(1) # return the gap from TM band 1 to TM band 2


n_ratio = np.linspace(1.4, 3.6, num=20)
opt_radius = np.zeros_like(n_ratio)
opt_gap = np.zeros_like(n_ratio)

for i, ratio in enumerate(n_ratio):
    eps = (3.6/ratio)**2
    ms.default_material = mp.Medium(epsilon=eps)
    result = minimize_scalar(first_tm_gap, method='bounded', bounds=[0.1, 0.5], tol=0.001)
    opt_radius[i] = result.x
    opt_gap[i] = result.fun * -1

fig, ax_r = plt.subplots(1, 1)
ax_g = ax_r.twinx()
ax_r.plot(n_ratio, opt_radius, color='C1', label='optimal radius')
ax_g.plot(n_ratio, opt_gap, color='C2', label='maximum TM gap')

ax_r.set_xlabel(r'$\mathrm{n_{pillar} / n_{medium}}$')
ax_g.set_ylabel('relative photonic gap width / %')
ax_r.set_ylabel('radius as a fraction of lattice constant')

plt.legend(loc='top right')
plt.show()