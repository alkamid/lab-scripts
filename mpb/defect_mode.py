import meep as mp
from meep import mpb
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter


num_bands = 31
gaas = mp.Medium(epsilon=12.96)
k_points = [mp.Vector3(0., 0.5), ]

a = 44
pillar_size = (a/4-0.0)/a
defect_size = (57/2-0.0)/a

geometry_lattice = mp.Lattice(size=mp.Vector3(5, 5),
                              basis1=mp.Vector3(math.sqrt(3)/2, 0.5),
                              basis2=mp.Vector3(math.sqrt(3)/2, -0.5))

geometry = [mp.Cylinder(pillar_size, material=gaas)]
geometry = mp.geometric_objects_lattice_duplicates(geometry_lattice, geometry)
defect = mp.Cylinder(defect_size, material=gaas)
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

defect1 = mp.Cylinder(defect_size, material=gaas)
defect_modes_idx = []
for i, freq in enumerate(ms.get_freqs()):
    if 0.229 < freq < 0.307:
        defect_modes_idx.append(i)
        ms.get_dfield(i+1, bloch_phase=False)
        df = ms.compute_field_energy()
        print(df)
        energy_defect = ms.compute_energy_in_objects([defect1])
        energy_ar = ms.compute_energy_in_dielectric(12, 13)
        print(i, freq, energy_defect, energy_ar)

# Create an MPBData instance to transform the efields
md = mpb.MPBData(rectify=True, resolution=32, periods=1)

converted = []
for i in defect_modes_idx:
    f = efields[i]
    # Get just the z component of the efields
    f = f[..., 0, 2]
    converted.append(md.convert(f))

# smooth_eps = gaussian_filter(converted_eps.T, sigma=1)
eps = ms.get_epsilon()
converted_eps = md.convert(eps)
smooth_eps = gaussian_filter(converted_eps.T, sigma=1)

fig, ax = plt.subplots(3, 2, squeeze=False)
for i, f in enumerate(converted):
    ax[i//2, i%2].contour(smooth_eps, levels=[0,1,2,3], cmap='binary_r')
    ax[i//2, i%2].imshow(np.real(f).T, interpolation='spline36', cmap='RdBu', alpha=0.9)
    ax[i//2, i%2].axis('off')

plt.show()


# result = ms.run_tm(mpb.output_at_kpoint(k_points[0], mpb.fix_efield_phase,
#          mpb.output_efield_z))
