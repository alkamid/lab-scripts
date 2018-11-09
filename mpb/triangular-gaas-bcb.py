import meep as mp
from meep import mpb
import math

num_bands = 8

k_points = [mp.Vector3(),
            mp.Vector3(0., 0.5),
            mp.Vector3(-1/3, 1/3),
            mp.Vector3()]

k_points = mp.interpolate(10, k_points)

geometry = [mp.Cylinder(0.25, material=mp.Medium(epsilon=12.96))]

geometry_lattice = mp.Lattice(size=mp.Vector3(1, 1),
                              basis1=mp.Vector3(math.sqrt(3)/2, 0.5),
                              basis2=mp.Vector3(math.sqrt(3)/2, -0.5))

default_material = mp.Medium(epsilon=2.4)

resolution = 32

ms = mpb.ModeSolver(num_bands=num_bands,
                    k_points=k_points,
                    geometry=geometry,
                    geometry_lattice=geometry_lattice,
                    resolution=resolution,
                    default_material=default_material)

ms.run_tm()