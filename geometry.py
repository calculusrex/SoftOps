import numpy as np
from numpy import cos, pi, sin, arccos
import mathutils
from mathutils import Vector
from math import ceil

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)

from utils import invert_domain, map_output, map_domain




def vector_angle(v1, v2):

    stage1 = v1.dot(v2) / (v1.magnitude * v2.magnitude)

    if stage1 > 1:
        stage1 = 1
    elif stage1 < -1:
        stage1 = -1

    stage2 = arccos(stage1)

    return stage2


def projection_magnitude(v0, v1):
    return v0.dot(v1/v1.magnitude)


# cosinus curve the ascending portion normalized
curve_ascending = lambda x: (-cos(pi * x) + 1) / 2
curve_concave = lambda x: sin((pi/2) * x)

dx = 0.00000001

curve_slope = lambda f, x: (f(x + dx) - f(x)) / dx


def positions_from_ring_n(n):
    return map(lambda x: x / (n - 1),
               range(n))


def vector_from_xy(xy):
    x, y = xy
    return Vector(
        (x, y, 0)
    )


def convert_coordinates__cartesian(vector_in_old_basis,
                                   old_basis_in_new_coordinates):
    
    p = vector_in_old_basis
    i, j, k = old_basis_in_new_coordinates

    return p.x * i + p.y * j + p.z * k


def circle_points__polar_coordinates(r, n):
    rs = map(lambda x: r, range(n))
    thetas = np.arange(0, 2*np.pi, np.pi/(n/2)) + (np.pi/4) # + np.pi/4 because i want them rotated by 45 degrees
    return list(zip(rs, thetas))

def semicircle_points__polar_coordinates(r, n, zenith_angle):
    rs = map(lambda x: r, range(n))
    thetas = np.arange(0, np.pi, np.pi/n) - np.pi/2 + zenith_angle
    return list(zip(rs, thetas))



x_from_polar = lambda r, t: r * np.cos(t)
y_from_polar = lambda r, t: r * np.sin(t)

def cartesian_from_polar__point(polar_tuple):
    r, t = polar_tuple
    x = x_from_polar(r, t)
    y = y_from_polar(r, t)
    return x, y


def circle_points__local_cartesian_coordinates(r, n):
    polar_points_xy = circle_points__polar_coordinates(r, n)
    cartesian_points_xy = list(
        map(cartesian_from_polar__point,
            polar_points_xy)
    )
    vctrs = list(map(
        lambda xy: Vector((xy[0], 0, xy[1])),
        cartesian_points_xy))
    return vctrs



def semicircle_points__local_cartesian_coordinates(r, n, zenith_axis):
    axes_x_angles = {
        'x': 0, 'z': np.pi/2, '-x': np.pi, '-z': 3*np.pi/2
    }
    polar_points_xy = semicircle_points__polar_coordinates(r, n,
                                                           axes_x_angles[zenith_axis])
    cartesian_points_xy = list(
        map(cartesian_from_polar__point,
            polar_points_xy)
    )
    vctrs = list(map(
        lambda xy: Vector((xy[0], 0, xy[1])),
        cartesian_points_xy))
    return vctrs


def circle_points(r, n, ijk, offset_vector):

    n = 2 * ceil(n/2) # i want it to be impossible to output circles with odd number points

    points = circle_points__local_cartesian_coordinates(r, n)

    points = list(map(
        lambda vctr: convert_coordinates__cartesian(vctr, ijk) + offset_vector,
        points))

    return points


def semicircle_points(r, n, ijk, offset_vector, zenith_axis):

    n = 2 * ceil(n/2) # i want it to be impossible to output circles with odd number points

    points = semicircle_points__local_cartesian_coordinates(r, n, zenith_axis)

    points = list(map(
        lambda vctr: convert_coordinates__cartesian(vctr, ijk) + offset_vector,
        points))

    return points


def zenith_point(altitude, ijk, offset_vector):
    point = Vector((0, 0, altitude))
    point = convert_coordinates__cartesian(point, ijk) + offset_vector
    return point

def nadir_point(altitude, ijk, offset_vector):
    point = Vector((0, 0, -altitude))
    point = convert_coordinates__cartesian(point, ijk) + offset_vector
    return point
    


def generate_fusiform_profile_curve_function(origin_tendon_length=0,
                                             origin_tendon_radius=0.01,
                                             insertion_tendon_length=0,
                                             insertion_tendon_radius=0.01,
                                             body_radius=0.02):



    def in_curve(x):                              # In radius
        return map_output(
            curve_concave,
            origin_tendon_radius,
            body_radius
        )(x)


    def out_curve(x):                             # Out radius
        return map_output(
            invert_domain(curve_concave),
            insertion_tendon_radius,
            body_radius,
        )(x)


    def curve_0(x):                                 # The body of the muscle
        if x < 0.5:
            return in_curve(2 * x)
        else:
            return out_curve(1 - (2 * x))


    def curve_1(x):
        return map_domain(
            curve_0,
            origin_tendon_length,
            1 - insertion_tendon_length
        )(x)
        

    def curve_2(x):                                 # The tendons
        if x < origin_tendon_length:
            return curve_0(0)
        elif x < (1 - insertion_tendon_length):
            return curve_1(x)
        else:
            return curve_0(1)

    return curve_2


def compute_twist_angle(ijk0, ijk1):
    i0, j0, k0 = ijk0
    i1, j1, k1 = ijk1

    sine = projection_magnitude(i1, k0)

    fi = vector_angle(k0, k1)

    if sine < 0:
        return -fi
    else:
        return fi

def arange_angles(fi, n):

    factors = np.append(
        np.arange(0, 1, 1/(n-1)),
        1)

    angles = list(map(
        lambda factor: fi * factor,
        factors))

    return angles

def rotate_ijk_around_y_axis(ijk, fi):
    i0, j0, k0 = ijk

    k1 = Vector(cos(fi) * k0 + sin(fi) * i0)
    i1 = Vector(cos(fi) * i0 - sin(fi) * k0)

    return i1, j0, k1


def linear_falloff(n):
    factors = np.arange(0, 1+(1/n), 1/n)
    factors = list(map(float, factors))[1:]
    factors.reverse()
    return factors


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    print(linear_falloff(10))
    

    # curve_f = generate_muscle_curve(
    #     origin_tendon_length=0.1,
    #     origin_tendon_radius=0.01,
    #     insertion_tendon_length=0.4,
    #     insertion_tendon_radius=0.0025,
    #     flatness=1,
    #     body_radius=0.05)

    # xs = list(map(lambda x: x / 100,
    #               range(100)))

    # def gen_ys():
    #     return list(map(curve_f, xs))

    # def plot():
    #     ys = gen_ys()
    #     plt.plot(xs, ys)
    #     plt.show()

    # plot()
    
