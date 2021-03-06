import bpy
import functools as ft

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)

from utils import overlapping_pairs, one_true, rotate_list, are_all_true
from bezier.spline import align_handles__vector
from bezier.silhuette import get_silhuette_data__from_active





def align_handles__angle_adjust(h1, p1, h2):
    r1, r2 = (h1 - p1), (h2 - p1)

    downstream_direction = r2 - r1
    upstream_direction = -downstream_direction

    downstream_unit = downstream_direction / downstream_direction.magnitude
    upstream_unit = upstream_direction / upstream_direction.magnitude

    h1_ = p1 + (upstream_unit * r1.magnitude)
    h2_ = p1 + (downstream_unit * r2.magnitude)
    
    return h1_, p1, h2_






def vector_triple__from_node_data(node_data):
    h1 = node_data['up_handle']
    p1 = node_data['core']
    h2 = node_data['down_handle']
    return h1, p1, h2



def maybe_vector_triples__from_spline_data(spline_data, n):
    if spline_data == None:
        return list(map(lambda _: (None, None, None),
                        range(n)))
    else:
        return list(map(vector_triple__from_node_data,
                        spline_data['nodes']))

def tensor_matrix_row__from_longitudinal_column(column):
    n = len(column['core']['nodes'])
    tripless = list(map(lambda key: maybe_vector_triples__from_spline_data(column[key], n),
                        ['up_handle', 'core', 'down_handle']))
    return list(map(list,
                    zip(*tripless)))

def tensor_matrix__from_longitudinal_columns(columns):
    return list(map(tensor_matrix_row__from_longitudinal_column,
                    columns))


def tensor_matrix_column__from_transverse_column(column):
    n = len(column['core']['nodes'])
    tripless = list(map(lambda key: maybe_vector_triples__from_spline_data(column[key], n),
                        ['up_handle', 'core', 'down_handle']))
    return list(map(lambda triples: list(zip(*triples)),
                    zip(*tripless)))

def tensor_matrix__from_transversal_columns(columns):
    return list(map(list,
                    zip(*map(tensor_matrix_column__from_transverse_column,
                             columns))))

# PROBABLY NOT CURRENTLY IN USE
def tensor_matrix__from_axis(columns, axis):
    if axis == 'longitudinal':
        return tensor_matrix__from_longitudinal_columns(columns)
    else:
        return tensor_matrix__from_transversal_columns(columns)


def maybe_align_handles(h1, p1, h2):
    if are_all_true(map(lambda x: x != None, [h1, p1, h2])):
        return align_handles__angle_adjust(h1, p1, h2)
    else:
        return h1, p1, h2


def maybe_vector_mean(v1, v2):
    if v1 == None and v2 == None:
        return None
    elif v1 == None:
        return v2
    elif v2 == None:
        return v1
    else:
        return (v1 + v2) / 2


def tensor_matrix__tensor_row_mean(longitudinal_tensor_row, transversal_tensor_row):

    return list(map(lambda params: maybe_vector_mean(*params),
                    zip(longitudinal_tensor_row,
                        transversal_tensor_row)))

def tensor_matrix__tensor_mean(longitudinal_tensor, transversal_tensor):
    return list(map(lambda tensor_row_pair: tensor_matrix__tensor_row_mean(*tensor_row_pair),
                    zip(longitudinal_tensor,
                        transversal_tensor)))

def tensor_matrix__inform_tensors(longitudinal_tensor, transversal_tensor):
    tensor = tensor_matrix__tensor_mean(longitudinal_tensor, transversal_tensor)

    abc, def_, ghi = tensor

    a, b, c = abc
    d, e, f = def_
    g, h, i = ghi

    d1, e1, f1 = maybe_align_handles(d, e, f)

    a1, b1, c1 = maybe_align_handles(a, b, c)
    g1, h1, i1 = maybe_align_handles(g, h, i)

    a1, d1, g1 = maybe_align_handles(a1, d1, g1)
    c1, f1, i1 = maybe_align_handles(c1, f1, i1)

    return [
        [a1, b1, c1],
        [d1, e1, f1],
        [g1, h1, i1]
    ]



def tensor_matrix__inform_longitudinal_row(longitudinal__tensor_matrix, transversal__tensor_matrix):
    return list(map(lambda tensors: tensor_matrix__inform_tensors(*tensors),
                    zip(longitudinal__tensor_matrix,
                        transversal__tensor_matrix)))



def tensor_matrix__from_silhuette_data(silhuette_data):
    longitudinal__tensor_matrix = tensor_matrix__from_longitudinal_columns(
        silhuette_data['longitudinal']['columns'])
    transversal__tensor_matrix = tensor_matrix__from_transversal_columns(
        silhuette_data['transversal']['columns'])
    return list(map(lambda params: tensor_matrix__inform_longitudinal_row(*params),
                    zip(longitudinal__tensor_matrix,
                        transversal__tensor_matrix)))


def interpolated_tensor_matrix__from_silhuette_data(silhuette_data):
    tensor_matrix = tensor_matrix__from_silhuette_data(silhuette_data)
    
    tensor_matrix = interpolate_tensor_matrix(
        tensor_matrix,
        longitudinally_cyclic=silhuette_data['longitudinal']['cyclic'],
        transversally_cyclic=silhuette_data['transversal']['cyclic'])

    return tensor_matrix

    


def tensor_matrix__from_active(context):
    return tensor_matrix__from_silhuette_data(
        get_silhuette_data__from_active(context)
    )


def interpolated_tensor_matrix__from_active(context,
                                            longitudinally_cyclic=False, transversally_cyclic=False):
    return interpolate_tensor_matrix(
        tensor_matrix__from_active(context),
        longitudinally_cyclic=longitudinally_cyclic,
        transversally_cyclic=transversally_cyclic
    )



# def transpose_tensor(tensor):
#     return list(zip(*tensor))

# def align_longitudinal_tensor_cores(tensor):
#     return [
#         tensor[0],
#         align_handles__vector(*tensor[1]),
#         tensor[2]
#     ]

# def align_transversal_tensor_cores(tensor):
#     return transpose_tensor(
#         align_longitudinal_tensor_cores(
#             transpose_tensor(tensor)))

# def align_tensor_cores(tensor):
#     return align_transversal_tensor_cores(
#         align_longitudinal_tensor_cores(tensor))

# def align_longitudinal_tensor_handles(tensor):
#     return [
#         align_handles__vector(*tensor[0]),
#         tensor[1],
#         align_handles__vector(*tensor[2])
#     ]

# def align_transversal_tensor_handles(tensor):
#     return transpose_tensor(
#         align_longitudinal_tensor_handles(
#             transpose_tensor(tensor)))

# def align_tensor_handles(tensor):
#     return align_transversal_tensor_handles(
#         align_longitudinal_tensor_handles(tensor))

# def align_tensor(tensor):
#     return align_tensor_handles(
#         align_tensor_cores(tensor))

# def tensor_matrix_row__align_tensors(tensor_matrix_row):
#     return list(map(align_tensor,
#                     tensor_matrix_row))

# def tensor_matrix__align_tensors(tensor_matrix):
#     return list(map(tensor_matrix_row__align_tensors,
#                     tensor_matrix))






def transpose_tensor_matrix(tensor_matrix):
    return list(map(lambda row: list(map(lambda tensor: list(zip(*tensor)), row)),
                    zip(*tensor_matrix)))




def handle_curve_points__from__core_curve_points(l0, l1, p0, h0, h1, p1):
    a0, a1 = h0 - p0, h1 - p1
    s0, s1 = l0 - p0, l1 - p1
    d, d_ = p1 - p0, l1 - l0
    q = d_.magnitude / d.magnitude
    b0, b1 = q * a0, q * a1
    h0_, h1_ = l0 + b0, l1 + b1
    return l0, h0_, h1_, l1



def tensor__interpolate_longitudinal_upstream_handle_vectors(tensor0, tensor1):
    abc0, def0, _ = tensor0
    abc1, def1, _ = tensor1
    
    a0, b0, c0 = abc0
    a1, b1, c1 = abc1
    
    _, l0, _ = abc0
    _, l1, _ = abc1
    _, p0, r0 = def0
    r1, p1, _ = def1
    b0_, c0_, a1_, b1_ = handle_curve_points__from__core_curve_points(l0, l1, p0, r0, r1, p1)
    
    tensor0[0] = [a0, b0_, c0_]
    tensor1[0] = [a1_, b1_, c1]

    return tensor0, tensor1



def tensor__interpolate_longitudinal_downstream_handle_vectors(tensor0, tensor1):
    _, def0, ghi0 = tensor0
    _, def1, ghi1 = tensor1
    
    g0, h0, i0 = ghi0
    g1, h1, i1 = ghi1
    
    _, l0, _ = ghi0
    _, l1, _ = ghi1
    _, p0, r0 = def0
    r1, p1, _ = def1
    h0_, i0_, g1_, h1_ = handle_curve_points__from__core_curve_points(l0, l1, p0, r0, r1, p1)
    
    tensor0[2] = [g0, h0_, i0_]
    tensor1[2] = [g1_, h1_, i1]

    return tensor0, tensor1



def tensor__interpolate_transversal_upstream_handle_vectors(tensor0, tensor1):
    t0 = list(zip(*tensor0))
    t1 = list(zip(*tensor1))
    return tensor__interpolate_longitudinal_upstream_handle_vectors(t0, t1)



def tensor__interpolate_transversal_downstream_handle_vectors(tensor0, tensor1):
    t0 = list(zip(*tensor0))
    t1 = list(zip(*tensor1))
    return tensor__interpolate_longitudinal_downstream_handle_vectors(t0, t1)



def missing_spline_upstream_interpolation__tensor_merge(A0, B0, B1, C1):
    abc, _, _ = B0
    a, b, c = abc
    B1[0][0] = a
    return B1



def missing_spline_downstream_interpolation__tensor_merge(A0, B0, B1, C1):
    _, _, ghi = B0
    g, h, i = ghi
    B1[2][0] = g
    return B1        



def tensor_matrix_row__interpolate_missing__general(interpolation_f, tensor_merge_f,
                                                    tensor_matrix_row, cyclic=False):
    tensor_pairs = overlapping_pairs(tensor_matrix_row,
                                     cyclic=cyclic)
    processed_pairs = list(map(lambda pair: interpolation_f(*pair),
                               tensor_pairs))
    middle_interpolated_tensors = []
    for i in range(len(processed_pairs) - 1):
        A0, B0 = processed_pairs[i]
        B1, C1 = processed_pairs[i+1]
        B2 = tensor_merge_f(A0, B0, B1, C1)
        middle_interpolated_tensors.append(B2)

    interpolated_tensors = []

    if cyclic:
        A0, B0 = processed_pairs[-1]
        B1, C1 = processed_pairs[0]
        B2 = tensor_merge_f(A0, B0, B1, C1)
        interpolated_tensors.append(B2)
        interpolated_tensors.extend(middle_interpolated_tensors)

    else:    
        A, B = processed_pairs[0]
        interpolated_tensors.append(A)
        interpolated_tensors.extend(middle_interpolated_tensors)
        A, B = processed_pairs[-1]
        interpolated_tensors.append(B)

    return interpolated_tensors

    

def tensor_matrix_row__interpolate_missing__upstream(tensor_matrix_row, cyclic=False):
    return tensor_matrix_row__interpolate_missing__general(
        tensor__interpolate_longitudinal_upstream_handle_vectors,
        missing_spline_upstream_interpolation__tensor_merge,
        tensor_matrix_row, cyclic=cyclic)



def tensor_matrix_row__interpolate_missing__downstream(tensor_matrix_row, cyclic=False):
    return tensor_matrix_row__interpolate_missing__general(
        tensor__interpolate_longitudinal_downstream_handle_vectors,
        missing_spline_downstream_interpolation__tensor_merge,
        tensor_matrix_row, cyclic=cyclic)



def tensor_matrix__interpolate_missing_longitudinal_data(tensor_matrix, cyclic=False):
    missing_spline_indices = identify_missing_longitudinal_splines__from_tensor_matrix(tensor_matrix)
    for missing__data in missing_spline_indices:
        if missing__data['spline'] == 0:
            tensor_matrix[missing__data['row']] = tensor_matrix_row__interpolate_missing__upstream(
                tensor_matrix[missing__data['row']], cyclic=cyclic)
        else:
            tensor_matrix[missing__data['row']] = tensor_matrix_row__interpolate_missing__downstream(
                tensor_matrix[missing__data['row']], cyclic=cyclic)
    return tensor_matrix



def tensor__profile_missing_vectors(triples):
    data = {}
    for key, triple in zip(['upstream_handle', 'core', 'downstream_handle'], triples):
        data[key] = one_true(map(lambda vector: vector == None,
                                 triple))
        
    return data



tensor__interpolate_downstream_handles = tensor__interpolate_longitudinal_downstream_handle_vectors
tensor__interpolate_upstream_handles = tensor__interpolate_longitudinal_upstream_handle_vectors

def tensor_matrix__interpolate__segment(tensor1, tensor2):
    tensor1_missing_data = tensor__profile_missing_vectors(tensor1)
    tensor2_missing_data = tensor__profile_missing_vectors(tensor2)

    if tensor1_missing_data['upstream_handle'] or tensor2_missing_data['upstream_handle']:
        tensor1, tensor2 = tensor__interpolate_upstream_handles(tensor1, tensor2)

    if tensor1_missing_data['downstream_handle'] or tensor2_missing_data['downstream_handle']:
        tensor1, tensor2 = tensor__interpolate_downstream_handles(tensor1, tensor2)

    return tensor1, tensor2



def tensor__merge(tensor_pair_1, tensor_pair_2):
    _, T0 = tensor_pair_1
    T1, _ = tensor_pair_2

    abc0, _, ghi0 = T0

    a0, _, _ = abc0

    g0, _, _ = ghi0

    T2 = list(map(list,
                  T1))
    
    T2[0][0] = a0
    T2[2][0] = g0

    return T2
    

def tensor__symmetrize_vertical(triples, axis):
    abc, def_, ghi = triples
    a, b, c = abc
    d, e, f = def_
    g, h, i = ghi

    if axis == 'upstream':
        c_ = 2*b - a
        f_ = 2*e - d
        i_ = 2*h - g
        tensor = [
            [a, b, c_],
            [d, e, f_],
            [g, h, i_]
        ]

    if axis == 'downstream':
        a_ = 2*b - c
        d_ = 2*e - f
        g_ = 2*h - i
        tensor = [
            [a_, b, c],
            [d_, e, f],
            [g_, h, i]
        ]
    
    return tensor
    

def tensor_matrix__interpolate_missing__row__non_cyclic(row):
    tensor_pairs = overlapping_pairs(row)
    processed_segments = list(map(lambda tensor_pair: tensor_matrix__interpolate__segment(*tensor_pair),
                                  tensor_pairs))
    segment_pairs = overlapping_pairs(processed_segments)

    final_tensors = [
        tensor__symmetrize_vertical(processed_segments[0][0], axis='downstream')
    ]
    final_tensors.extend(list(map(lambda tensor_pair__pair: tensor__merge(*tensor_pair__pair),
                                  segment_pairs)))
    final_tensors.append(
        tensor__symmetrize_vertical(processed_segments[-1][-1], axis='upstream'))
    
    return final_tensors


def tensor_matrix__interpolate_missing__row__cyclic(row):
    tensor_pairs = overlapping_pairs(row, cyclic=True)
    processed_segments = list(map(lambda tensor_pair: tensor_matrix__interpolate__segment(*tensor_pair),
                                  tensor_pairs))
    segment_pairs = overlapping_pairs(processed_segments, cyclic=True)
    final_tensors = list(map(lambda tensor_pair__pair: tensor__merge(*tensor_pair__pair),
                             segment_pairs))
    return rotate_list(-1,
                       final_tensors)


def tensor_matrix__interpolate_missing__row(row, cyclic=False):
    if cyclic:
        return tensor_matrix__interpolate_missing__row__cyclic(row)
    else:
        return tensor_matrix__interpolate_missing__row__non_cyclic(row)



def tensor_matrix__interpolate_missing__rows(tensor_matrix, cyclic=False):
    return list(map(lambda row: tensor_matrix__interpolate_missing__row(row, cyclic=cyclic),
                    tensor_matrix))



def tensor_matrix__interpolate_missing__cols(tensor_matrix, cyclic=False):
    return transpose_tensor_matrix(
        tensor_matrix__interpolate_missing__rows(transpose_tensor_matrix(tensor_matrix),
                                                 cyclic=cyclic))



def tensor_matrix__interpolate_holes(tensor_matrix, longitudinal_cyclic=False, transversal_cyclic=False):
    return tensor_matrix__interpolate_missing__cols(
        tensor_matrix__interpolate_missing__rows(tensor_matrix,
                                                 cyclic=longitudinal_cyclic),
        cyclic=transversal_cyclic)




tensor_matrix__interpolate_missing__longitudinally = tensor_matrix__interpolate_missing__rows

def interpolate_tensor_matrix(tensor_matrix,
                              longitudinally_cyclic=False,
                              transversally_cyclic=False):
    
    tensor_matrix = tensor_matrix__interpolate_missing__longitudinally(
        tensor_matrix, cyclic=longitudinally_cyclic)

    # tensor_matrix = tensor_matrix__align_tensors(tensor_matrix)

    return tensor_matrix



def node__from_triple(triple):
    h1, p1, h2 = triple
    data = {}
    data['up_handle'] = h1
    data['core'] = p1
    data['down_handle'] = h2
    return data


def nodes__from_triples(triples):
    return list(map(node__from_triple,
                    triples))


def silhuette_column_data__from_tensor_matrix_row(row):
    nodess = list(map(nodes__from_triples,
                     zip(*row)))

    data = {}
    for i, key in zip(range(3), ['up', 'core', 'down']):
        data[key] = nodess[i]
        
    return data


def silhuette_longitudinal_column_data__from_tensor_matrix(tensor_matrix):
    return list(map(silhuette_column_data__from_tensor_matrix_row,
                    tensor_matrix))


def silhuette_transversal_column_data__from_tensor_matrix(tensor_matrix):
    tensor_matrix = transpose_tensor_matrix(tensor_matrix)

    return list(map(silhuette_column_data__from_tensor_matrix_row,
                    tensor_matrix))


def silhuette_column_data__from_tensor_matrix(tensor_matrix):
    data = {}
    data['longitudinal'] = silhuette_longitudinal_column_data__from_tensor_matrix(tensor_matrix)
    data['transversal'] = silhuette_transversal_column_data__from_tensor_matrix(tensor_matrix)
    return data
