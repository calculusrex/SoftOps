import bpy
from math import ceil


import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)


from geometry import positions_from_ring_n, circle_points, compute_twist_angle, arange_angles, rotate_ijk_around_y_axis, generate_fusiform_profile_curve_function, nadir_point, zenith_point, semicircle_points
from spline import adjust_flatness, geodesic_bases_interpolation__from_axial_vectors, approximate_intermediate_axial_vectors, approximate_fiber_curve, approximate_fiber_curve__double
from get_bones import fiber_rig_type, get_fiber_vector_data
from mesh_basic import cyllindrical_mesh
from utils import flaten__triple, flatten_lists


def twisted_curve_points_n_bases(vector_data):

        curve_points = approximate_fiber_curve(vector_data)
    
        axial_vectors = []
        axial_vectors.append(vector_data['origin_axes']['y'])
        axial_vectors.extend(
            approximate_intermediate_axial_vectors(
                curve_points)
        )
        axial_vectors.append(vector_data['insertion_axes']['y'])

        ijk0 = (
            vector_data['origin_axes']['x'],
            vector_data['origin_axes']['y'],
            vector_data['origin_axes']['z'],
        )

        ijk1 = (
            vector_data['insertion_axes']['x'],
            vector_data['insertion_axes']['y'],
            vector_data['insertion_axes']['z'],
        )

        curve_bases = [ijk0]
        curve_bases.extend(geodesic_bases_interpolation__from_axial_vectors(
            ijk0, axial_vectors[1:]))


        # twist
        twist_angle = compute_twist_angle(ijk1, curve_bases[-1])
        twists = arange_angles(twist_angle, len(curve_points))
        curve_bases = map(lambda args: rotate_ijk_around_y_axis(*args),
                          zip(curve_bases, twists))

        return curve_points, curve_bases


def twisted_curve_points_n_bases__double_fiber(vector_data):

    proximal_curve_points, distal_curve_points = approximate_fiber_curve__double(vector_data)

    proximal_axial_vectors = []
    proximal_axial_vectors.append(vector_data['origin_axes']['y'])
    proximal_axial_vectors.extend(
        approximate_intermediate_axial_vectors(
            proximal_curve_points)
    )
    proximal_axial_vectors.append(vector_data['midpoint_axes']['y'])

    distal_axial_vectors = []
    distal_axial_vectors.append(vector_data['midpoint_axes']['y'])
    distal_axial_vectors.extend(
        approximate_intermediate_axial_vectors(
            distal_curve_points)
    )
    distal_axial_vectors.append(vector_data['insertion_axes']['y'])

    ijk0 = (
        vector_data['origin_axes']['x'],
        vector_data['origin_axes']['y'],
        vector_data['origin_axes']['z'],
    )

    ijk1 = (
        vector_data['midpoint_axes']['x'],
        vector_data['midpoint_axes']['y'],
        vector_data['midpoint_axes']['z'],
    )

    ijk2 = (
        vector_data['insertion_axes']['x'],
        vector_data['insertion_axes']['y'],
        vector_data['insertion_axes']['z'],
    )

    proximal_curve_bases = [ijk0]
    proximal_curve_bases.extend(geodesic_bases_interpolation__from_axial_vectors(
        ijk0, proximal_axial_vectors[1:]))

    distal_curve_bases = [ijk1]
    distal_curve_bases.extend(geodesic_bases_interpolation__from_axial_vectors(
        ijk1, distal_axial_vectors[1:]))

    # proximal muscle twist
    proximal_twist_angle = compute_twist_angle(ijk1, proximal_curve_bases[-1])
    proximal_twists = arange_angles(proximal_twist_angle, len(proximal_curve_points))
    proximal_curve_bases = list(map(lambda args: rotate_ijk_around_y_axis(*args),
                                    zip(proximal_curve_bases, proximal_twists)))

    # distal muscle twist
    distal_twist_angle = compute_twist_angle(ijk2, distal_curve_bases[-1])
    distal_twists = arange_angles(distal_twist_angle, len(distal_curve_points))
    distal_curve_bases = list(map(lambda args: rotate_ijk_around_y_axis(*args),
                                  zip(distal_curve_bases, distal_twists)))

    curve_bases = []
    curve_bases.extend(proximal_curve_bases)
    curve_bases.extend(distal_curve_bases[1:])

    curve_points = []
    curve_points.extend(proximal_curve_points)
    curve_points.extend(distal_curve_points[1:])

    return curve_points, curve_bases


def curve_points_n_bases(fiber_data, flatness):
    vector_data = get_fiber_vector_data(fiber_data)
    if fiber_data['type'] == 'DOUBLE':        
        curve_points, curve_bases = twisted_curve_points_n_bases__double_fiber(vector_data)        
    else:
        curve_points, curve_bases = twisted_curve_points_n_bases(vector_data)
    # flatness
    curve_bases = list(map(
        lambda ijk: adjust_flatness(ijk, flatness),
        curve_bases
    ))
    return curve_points, curve_bases


def generate_radii(n,
                   origin_tendon_length,
                   origin_tendon_radius,
                   insertion_tendon_length,
                   insertion_tendon_radius,
                   body_radius):

    profile_f = generate_fusiform_profile_curve_function(origin_tendon_length=origin_tendon_length,
                                                         origin_tendon_radius=origin_tendon_radius,
                                                         insertion_tendon_length=insertion_tendon_length,
                                                         insertion_tendon_radius=insertion_tendon_radius,
                                                         body_radius=body_radius)
    radii = list(map(
        profile_f,
        positions_from_ring_n(n)
    ))
    
    return radii

def radiii_from_curves(curves,
                       origin_tendon_length,
                       origin_tendon_radius,
                       insertion_tendon_length,
                       insertion_tendon_radius,
                       body_radius):

    def mapped_func(curve):
        return generate_radii(len(curve[1]),
                              origin_tendon_length,
                              origin_tendon_radius,
                              insertion_tendon_length,
                              insertion_tendon_radius,
                              body_radius)    

    radiii = list(map(mapped_func, curves))
    return radiii


def fusiform_pointss(bases_n_offsets, radii, section_vert_count):

    def prepare_args(radius, base_n_offset):
        base, offset = base_n_offset
        return radius, section_vert_count, base, offset

    argss = map(
        lambda args: prepare_args(*args),
        zip(radii, bases_n_offsets)
    )

    pss = list(map(
        lambda args: circle_points(*args),
        argss
    ))

    return pss


def generate_fusiform_pointss(curve_points, curve_bases,
                              section_vert_count,
                              origin_tendon_length,
                              origin_tendon_radius,
                              insertion_tendon_length,
                              insertion_tendon_radius,
                              body_radius):

    radii = generate_radii(len(curve_bases),
                           origin_tendon_length,
                           origin_tendon_radius,
                           insertion_tendon_length,
                           insertion_tendon_radius,
                           body_radius)    

    bases_n_offsets = zip(curve_bases,
                          curve_points)

    pss = fusiform_pointss(bases_n_offsets,
                           radii,
                           section_vert_count)

    return pss


def compile_widemuscle_data(curves, radiii):
        
    fibers = list(map(flaten__triple,
                      zip(curves, radiii)))
    
    pbrss = []
    for points, bases, radii in fibers:
        pbrs = list(map(flaten__triple,
                        zip(zip(points, bases),
                            radii)))
        pbrss.append(pbrs)

    return pbrss


def generate_edge_pointss(curve_data, side, vert_count):
    if side == 'SUP':
        zenith_axis = '-x'
    else:
        zenith_axis = 'x'
    pss = []
    def mapped_f(point, base, radius):
        return semicircle_points(radius, vert_count, base, point, zenith_axis)
    return list(map(lambda args: mapped_f(*args), curve_data))

def generate_middle_pointss(curve_data):
    data = {}
    def dorsal_f(point, base, radius):
        return zenith_point(radius, base, point)
    def ventral_f(point, base, radius):
        return nadir_point(radius, base, point)
    data['dorsal'] = list(map(lambda args: dorsal_f(*args), curve_data))
    data['ventral'] = list(map(lambda args: ventral_f(*args), curve_data))
    return data


def widemuscle_pointss(muscle_data, widemuscle_data, section_vert_count):

    # print()
    # print('widemuscle_pointss')
    # for i in range(len(widemuscle_data)):
    #     ds = widemuscle_data[i]
    #     print()
    #     print(f'fiber {i}: ')
    #     print('number of points: ', len(ds))
    #     print()
    #     for xs in ds:
    #         print('number of points: ', len(xs))
    #         print()
    #         for ys in xs:
    #             print(ys)
    #         print()
    #     print()
    # print()
    
    superior_edge_data = widemuscle_data[0]
    inferior_edge_data = widemuscle_data[-1]

    superior_pss = generate_edge_pointss(superior_edge_data, 'SUP', 2 * ceil(section_vert_count/4))
    inferior_pss = generate_edge_pointss(inferior_edge_data, 'INF', 2 * ceil(section_vert_count/4))


    has_middle_portion = len(widemuscle_data) >= 3
    if has_middle_portion:
        middle_data = widemuscle_data[1:-1]
        middle_psss = []
        for fiber in middle_data:
            middle_pss = generate_middle_pointss(fiber)
            middle_psss.append(middle_pss)

    ##############################################################################
    # VERTEX DATA

    fiber_type = muscle_data[0]['type']
    half_n = len(widemuscle_data[0]) // 2

    vertex_data = []

    fiber_data = {}
    fiber_data['origin'] = superior_pss[0]
    if fiber_type == 'DOUBLE':
        fiber_data['proximal_body'] = superior_pss[1:half_n]
        fiber_data['distal_body'] = superior_pss[half_n:-1]
    else:
        fiber_data['body'] = superior_pss[1:-1]
    fiber_data['insertion'] = superior_pss[-1]
    vertex_data.append(fiber_data)

    if has_middle_portion:
        for fiber in middle_psss:
            fiber_data = {}
            fiber_data['origin'] = [fiber['dorsal'][0],
                                    fiber['ventral'][0]]

            if fiber_type == 'DOUBLE':
                fiber_data['proximal_body'] = list(map(list,
                                                       zip(fiber['dorsal'][1:half_n],
                                                           fiber['ventral'][1:half_n])))
                fiber_data['distal_body'] = list(map(list,
                                                     zip(fiber['dorsal'][half_n:-1],
                                                         fiber['ventral'][half_n:-1])))
            else:
                fiber_data['body'] = list(map(list,
                                              zip(fiber['dorsal'][1:-1],
                                                  fiber['ventral'][1:-1])))

            fiber_data['insertion'] = [fiber['dorsal'][-1],
                                       fiber['ventral'][-1]]
            vertex_data.append(fiber_data)

    fiber_data = {}
    fiber_data['origin'] = inferior_pss[0]
    if fiber_type == 'DOUBLE':
        fiber_data['proximal_body'] = inferior_pss[1:half_n]
        fiber_data['distal_body'] = inferior_pss[half_n:-1]
    else:
        fiber_data['body'] = inferior_pss[1:-1]
    fiber_data['insertion'] = inferior_pss[-1]
    vertex_data.append(fiber_data)

    # VERTEX DATA
    ##############################################################################

    pss = []
    for i in range(len(widemuscle_data[0])):
        loop = []
        loop.extend(superior_pss[i])
        if has_middle_portion:
            for fiber in middle_psss:
                loop.append(
                    fiber['ventral'][i])
        loop.extend(inferior_pss[i])
        if has_middle_portion:
            dorsal = []
            for fiber in middle_psss:
                dorsal.append(
                    fiber['dorsal'][i])
            dorsal.reverse()
            loop.extend(dorsal)
        pss.append(loop)
    return vertex_data, pss

        


def generate_widemuscle_pointss(muscle_data,
                                curves,
                                section_vert_count,
                                origin_tendon_length,
                                origin_tendon_radius,
                                insertion_tendon_length,
                                insertion_tendon_radius,
                                body_radius):

    radiii = radiii_from_curves(curves,
                                origin_tendon_length,
                                origin_tendon_radius,
                                insertion_tendon_length,
                                insertion_tendon_radius,
                                body_radius)

    widemuscle_data = compile_widemuscle_data(curves, radiii) # !!!

    vertex_data, pss = widemuscle_pointss(muscle_data, widemuscle_data, section_vert_count) # !!!

    return vertex_data, pss



def compile_fusiform_vertex_data(pss):    
    vertex_data = {}
    vertex_data['origin'] = pss[0]
    vertex_data['body'] = pss[1:-1]
    vertex_data['insertion'] = pss[-1]
    return vertex_data


def compile_fusiform_vertex_data__double_fiber(pss):    
    vertex_data = {}
    vertex_data['origin'] = pss[0]
    half_n = len(pss) // 2
    vertex_data['proximal_body'] = pss[1:half_n]
    vertex_data['distal_body'] = pss[half_n:-1]
    vertex_data['insertion'] = pss[-1]
    return vertex_data


def generate_fusiform_muscle_mesh(fiber_data,
                                  section_vert_count=8,
                                  origin_tendon_length=0.0,
                                  origin_tendon_radius=0.003,
                                  insertion_tendon_length=0.1,
                                  insertion_tendon_radius=0.001,
                                  flatness=1,
                                  body_radius=0.005):

    curve_points, curve_bases = curve_points_n_bases(fiber_data, flatness)

    pss = generate_fusiform_pointss(curve_points, curve_bases,
                                    section_vert_count=section_vert_count,
                                    origin_tendon_length=origin_tendon_length,
                                    origin_tendon_radius=origin_tendon_radius,
                                    insertion_tendon_length=insertion_tendon_length,
                                    insertion_tendon_radius=insertion_tendon_radius,
                                    body_radius=body_radius)

    if fiber_data['type'] == 'DOUBLE':
        vertex_data = compile_fusiform_vertex_data__double_fiber(pss)
    else:
        vertex_data = compile_fusiform_vertex_data(pss)
        
    vert_loops, face_loops, mesh = cyllindrical_mesh(pss, 'FUSIFORM', fiber_data)

    return vertex_data, mesh





def generate_wide_muscle_mesh(muscle_data,
                              section_vert_count=8,
                              origin_tendon_length=0.0,
                              origin_tendon_radius=0.003,
                              insertion_tendon_length=0.1,
                              insertion_tendon_radius=0.001,
                              flatness=1,
                              body_radius=0.005):

    fiber_keys = list(range(len(muscle_data)))
    curves = list(map(lambda fiber_data: curve_points_n_bases(fiber_data, flatness),
                      map(lambda k: muscle_data[k],
                          fiber_keys)))

    vertex_data, pss = generate_widemuscle_pointss(muscle_data,
                                                   curves,
                                                   section_vert_count=section_vert_count,
                                                   origin_tendon_length=origin_tendon_length,
                                                   origin_tendon_radius=origin_tendon_radius,
                                                   insertion_tendon_length=insertion_tendon_length,
                                                   insertion_tendon_radius=insertion_tendon_radius,
                                                   body_radius=body_radius)

    
    vert_loops, face_loops, mesh = cyllindrical_mesh(pss, 'WIDE', muscle_data)

    return vertex_data, mesh




if __name__ == '__main__':
    print("boom")

