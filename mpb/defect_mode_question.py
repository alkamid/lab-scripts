import meep as mp
from meep import mpb
import math
import numpy as np
import matplotlib.pyplot as plt

num_bands = 31
gaas = mp.Medium(epsilon=12.96)
k_points = [mp.Vector3(0., 0.5),]

geometry_lattice = mp.Lattice(size=mp.Vector3(5, 5),
                              basis1=mp.Vector3(math.sqrt(3)/2, 0.5),
                              basis2=mp.Vector3(math.sqrt(3)/2, -0.5))

geometry = [mp.Cylinder(0.25, material=gaas)]
geometry = mp.geometric_objects_lattice_duplicates(geometry_lattice, geometry)
defect = mp.Cylinder(0.6, material=gaas)
geometry.append(defect)

default_material = mp.Medium(epsilon=2.4)

resolution = 32
target_freq = (0.229 + 0.307) / 2

ms = mpb.ModeSolver(num_bands=num_bands,
                    k_points=k_points,
                    geometry=geometry,
                    geometry_lattice=geometry_lattice,
                    resolution=resolution,
                    default_material=default_material,
                    )

efields = []
def get_efields(ms, band):
    efields.append(ms.get_efield(band, bloch_phase=False))

ms.run_tm(mpb.output_at_kpoint(k_points[0]), mpb.fix_efield_phase,
          get_efields)

defect_modes_idx = []
for i, freq in enumerate(ms.get_freqs()):
    if 0.229 < freq < 0.307:
        defect_modes_idx.append(i)
        ms.get_dfield(i+1, bloch_phase=False)
        ms.compute_field_energy()
        energy = ms.compute_energy_in_objects([defect])
        energy2 = ms.compute_energy_in_dielectric(11, 13)
        print(i, freq, energy, energy2)

"""
D-energy-components:, 1, 25, 0, 0, 1
25 0.23522156656345886 0.028740036937926903
D-energy-components:, 1, 26, 0, 0, 1
26 0.2354496032832558 0.3681463616261254
"""

md = mpb.MPBData(rectify=True, resolution=32, periods=1)

converted = []
for i in defect_modes_idx:
    f = efields[i]
    f = f[..., 0, 2]
    converted.append(md.convert(f))

eps = ms.get_epsilon()
converted_eps = md.convert(eps)

fig, ax = plt.subplots(1, 2, squeeze=False)
for i, f in enumerate(converted):
    ax[i//2, i%2].contour(converted_eps.T, levels=[0,1,2,3], cmap='binary_r')
    ax[i//2, i%2].imshow(np.real(f).T, interpolation='spline36', cmap='RdBu', alpha=0.9)
    ax[i//2, i%2].axis('off')

plt.show()
