import mathutils

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)

from geometry import vector_angle
from get_bones import get_fiber_vector_data



###################################################
# bendy bone function research

# factor_points = []
# factor_points.append((1, 0.6475))
# factor_points.append((0.75, 0.44125))
# factor_points.append((0.5, 0.3875))
# factor_points.append((0.25, 0.3569))

# factor = (lambda x: x**3.5 / 3.4 + 0.355)(angle_factor)
###################################################


def geodesic_basis_step(ijk0, j1):

    i0, j0, k0 = ijk0

    i1 = j1.cross(k0)
    i1 /= i1.magnitude

    k1 = i1.cross(j1)
    k1 /= k1.magnitude

    return i1, j1, k1


def adjust_flatness(ijk, factor):
    i, j, k = ijk
    i *= factor
    k /= factor
    return i, j, k


def geodesic_bases_interpolation__from_axial_vectors(ijk0, axial_vectors):
    i0, j0, k0 = ijk0
    interpolated_bases = []
    for j1 in axial_vectors:
        ijk0 = geodesic_basis_step(ijk0, j1)
        interpolated_bases.append(ijk0)
    return interpolated_bases


def generate_fiber_bezier_curve(p0, p1, h0_orientation, h1_orientation, spline_n):
    
    length = (p1 - p0).magnitude

    angle_factor = (lambda v1, v2: v1.dot(v2) / (v1.magnitude * v2.magnitude))(h0_orientation, h1_orientation) # between -1 and 1, -1 means straight, 1 means maximally bent
    angle_factor = angle_factor / 2 + 0.5 # normalized to [0, 1]

    if angle_factor < 0:
        angle_factor = 0
    elif angle_factor > 1:
        angle_factor = 1

    factor = (lambda x: x**3.5 / 3.4 + 0.355)(angle_factor)

    h0 = p0 + (h0_orientation * length * factor)
    h1 = p1 + (h1_orientation * length * factor)

    vertex_position_vectors = mathutils.geometry.interpolate_bezier(
        p0, h0, h1, p1, spline_n
    )

    return vertex_position_vectors



def approximate_fiber_curve(vector_data):

    vdat = vector_data

    r0 = vdat['origin']
    r1 = vdat['insertion']

    segments = vdat['n_segments']
    spline_n = segments + 1

    length = vdat['reach']

    h0_orientation = vdat['origin_orientation']
    h1_orientation = vdat['insertion_orientation'] * -1

    vertex_position_vectors = generate_fiber_bezier_curve(
        r0, r1,
        h0_orientation, h1_orientation,
        spline_n)

    return vertex_position_vectors


def approximate_fiber_curve__double(vector_data):

    vdat = vector_data

    r0 = vdat['origin']
    r1 = vdat['midpoint']
    r2 = vdat['insertion']

    segments = vdat['n_segments']
    spline_n = segments + 1

    h0_orientation = vdat['origin_orientation']
    h1_orientation = vdat['midpoint_orientation'] * -1
    h2_orientation = vdat['midpoint_orientation']
    h3_orientation = vdat['insertion_orientation'] * -1

    proximal_vertex_position_vectors = generate_fiber_bezier_curve(
        r0, r1,
        h0_orientation, h1_orientation,
        spline_n)

    distal_vertex_position_vectors = generate_fiber_bezier_curve(
        r1, r2,
        h2_orientation, h3_orientation,
        spline_n)

    return proximal_vertex_position_vectors, distal_vertex_position_vectors



def approximate_intermediate_axial_vector(v0, v1, v2):
    a0 = v1 - v0
    a1 = v2 - v1
    return (a0 + a1) / 2

def approximate_intermediate_axial_vectors(spline_position_vectors):
    rs = spline_position_vectors
    return list(map(
        lambda i: approximate_intermediate_axial_vector(rs[i], rs[i+1], rs[i+2]),
        range(len(rs) - 2)))



if __name__ == '__main__':
    print("boom")
