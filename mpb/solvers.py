import meep as mp
from meep import mpb
import math

bcb = mp.Medium(epsilon=2.4)
gaas = mp.Medium(epsilon=12.96)


def triangular():
    k_points = [mp.Vector3(),
                mp.Vector3(0., 0.5),
                mp.Vector3(-1 / 3, 1 / 3),
                mp.Vector3()]

    k_points = mp.interpolate(10, k_points)

    geometry = [mp.Cylinder(0.25, material=gaas)]

    geometry_lattice = mp.Lattice(size=mp.Vector3(1, 1),
                                  basis1=mp.Vector3(math.sqrt(3) / 2, 0.5),
                                  basis2=mp.Vector3(math.sqrt(3) / 2, -0.5))

    default_material = bcb

    resolution = 32
    mesh_size = 7
    num_bands = 5

    ms = mpb.ModeSolver(num_bands=num_bands,
                        k_points=k_points,
                        geometry=geometry,
                        geometry_lattice=geometry_lattice,
                        resolution=resolution,
                        default_material=default_material,
                        mesh_size=mesh_size)

    return ms


def triangular_with_defect():
    k_points = [mp.Vector3(),
                mp.Vector3(0., 0.5),
                mp.Vector3(-1 / 3, 1 / 3),
                mp.Vector3()]

    k_points = mp.interpolate(10, k_points)

    geometry_lattice = mp.Lattice(size=mp.Vector3(5, 5),
                                  basis1=mp.Vector3(math.sqrt(3) / 2, 0.5),
                                  basis2=mp.Vector3(math.sqrt(3) / 2, -0.5))

    geometry = [mp.Cylinder(0.25, material=gaas)]
    geometry = mp.geometric_objects_lattice_duplicates(geometry_lattice, geometry)
    defect = mp.Cylinder(0.2, material=gaas)
    geometry.append(defect)

    default_material = bcb

    resolution = 32
    mesh_size = 7
    num_bands = 5

    ms = mpb.ModeSolver(num_bands=num_bands,
                        k_points=k_points,
                        geometry=geometry,
                        geometry_lattice=geometry_lattice,
                        resolution=resolution,
                        default_material=default_material,
                        mesh_size=mesh_size)

    return ms