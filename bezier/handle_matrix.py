import bpy
import functools as ft
from mathutils import Vector

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)


from bezier.tensor_matrix import interpolate_tensor_matrix
from bezier.tensor_matrix import tensor_matrix__from_active, tensor_matrix__interpolate_missing__rows, tensor_matrix__from_silhuette_data
from bezier.spline import align_handles__vector as align_vector_triple
from utils import overlapping_pairs



def PS__from_tensor_panel(tensor_panel):
    A, B = tensor_panel[0]
    C, D = tensor_panel[1]
    _, p1, h1 = A[1]
    h2, p2, _ = B[1]
    P1 = p1, h1, h2, p2

    _, p1, h1 = A[2]
    h2, p2, _ = B[2]
    H1 = p1, h1, h2, p2

    _, p1, h1 = C[0]
    h2, p2, _ = D[0]
    H2 = p1, h1, h2, p2

    _, p1, h1 = C[1]
    h2, p2, _ = D[1]
    P2 = p1, h1, h2, p2

    return P1, H1, H2, P2



def tensor_panel_strips(tensor_matrix, longitudinally_cyclic=False, transversally_cyclic=False):
    return list(map(lambda strip: list(zip(*strip)),
                    overlapping_pairs(
                        list(map(lambda row: overlapping_pairs(row, cyclic=longitudinally_cyclic),
                                 tensor_matrix)),
                        cyclic=transversally_cyclic)))


def handle_matrix__from_tensor_matrix(tensor_matrix,
                                      longitudinally_cyclic=False, transversally_cyclic=False):
    tensor_panelss = tensor_panel_strips(tensor_matrix,
                                         longitudinally_cyclic=longitudinally_cyclic,
                                         transversally_cyclic=transversally_cyclic)
    return list(
        map(lambda strip: list(map(lambda tensor_panel: PS__from_tensor_panel(tensor_panel), strip)),
            tensor_panelss))




tensor_matrix__interpolate_missing__longitudinally = tensor_matrix__interpolate_missing__rows

def interpolated_handle_matrix__from_tensor_matrix(tensor_matrix,
                                                   longitudinally_cyclic=False,
                                                   transversally_cyclic=False):
    tensor_matrix = interpolate_tensor_matrix(
        tensor_matrix,
        longitudinally_cyclic=longitudinally_cyclic,
        transversally_cyclic=transversally_cyclic)

    # tensor_matrix = tensor_matrix__align_tensors(tensor_matrix)

    return handle_matrix__from_tensor_matrix(tensor_matrix,
                                             longitudinally_cyclic=longitudinally_cyclic,
                                             transversally_cyclic=transversally_cyclic)



def handle_matrix__from_active(context, longitudinally_cyclic=False, transversally_cyclic=False):
    return interpolated_handle_matrix__from_tensor_matrix(
        tensor_matrix__from_active(context),
        longitudinally_cyclic=longitudinally_cyclic,
        transversally_cyclic=transversally_cyclic)



# def handle_matrix__from_active(context, longitudinally_cyclic=False, transversally_cyclic=False):
#     return handle_matrix__from_tensor_matrix(
#         tensor_matrix__interpolate_missing__longitudinally(tensor_matrix__from_active(context)),
#         longitudinally_cyclic=longitudinally_cyclic,
#         transversally_cyclic=transversally_cyclic)

##########################

def vectors__from_triple_pair(bezier_f, n, triple_pair):
    _, p0, h0 = triple_pair[0]
    h1, p1, _ = triple_pair[1]
    return bezier_f(n, p0, h0, h1, p1)


def n_handle_tensor__from_tensor_pair(bezier_f, n, tensor_pair):
    return list(map(lambda triple_pair: vectors__from_triple_pair(bezier_f, n, triple_pair),
                    zip(*tensor_pair)))


def n_handle_row__from_tensor_row(bezier_f, n, tensor_row, cyclic=False):
    return list(map(lambda tensor_pair: n_handle_tensor__from_tensor_pair(bezier_f, n, tensor_pair),
                    overlapping_pairs(tensor_row, cyclic=cyclic)))


def n_handle_matrix__from_tensor_matrix(bezier_f, n, tensor_matrix, cyclic=False):
    return list(map(lambda row: n_handle_row__from_tensor_row(bezier_f, n, row, cyclic=cyclic),
                    tensor_matrix))

##########################

def align__n_handle_tensor(n_handle_tensor):
    return list(map(list,
                    zip(*map(lambda triple: align_vector_triple(*triple),
                             zip(*n_handle_tensor)))))


def align__n_handle_row(n_handle_row):
    return list(map(align__n_handle_tensor,
                    n_handle_row))


def align__n_handle_matrix(n_handle_matrix):
    return list(map(align__n_handle_row,
                    n_handle_matrix))
                    
##########################

def m_handle_tensor__from_n_handle_tensor_pair(bezier_f, m, n_handle_pair):
    return list(map(lambda triple_pair: vectors__from_triple_pair(bezier_f, m, triple_pair),
                    zip(*map(lambda tensor: list(zip(*tensor)),
                             n_handle_pair))))
    


def m_handle_column__from_n_handle_column(bezier_f, m, n_handle_column, cyclic=False):
    return list(map(lambda pair: m_handle_tensor__from_n_handle_tensor_pair(bezier_f, m, pair),
                    overlapping_pairs(n_handle_column,
                                      cyclic=cyclic)))


def m_handle_matrix__from_n_handle_matrix(bezier_f, m, n_handle_matrix, cyclic=False):
    return list(
        map(list,
            zip(*map(lambda col: m_handle_column__from_n_handle_column(bezier_f, m, col, cyclic=cyclic),
                     zip(*n_handle_matrix)))))

##########################

def concat(*xss, cyclic=False):
    ys = []
    if cyclic:
        ys.extend(xss[0][1:])
    else:
        ys.extend(xss[0])
    for xs in xss[1:]:
        ys.extend(xs[1:])
    return ys
    

def vertex_positions__from_m_handle_matrix(m_handle_matrix, l_cyclic=False, t_cyclic=False):
    return concat(*list(map(lambda col: list(map(lambda vss: concat(*vss, cyclic=t_cyclic), zip(*col))),
                            zip(*m_handle_matrix))),
                  cyclic=l_cyclic)

##########################

def vertex_positions__from_tensor_matrix(bezier_func, n, m, tensor_matrix, l_cyclic, t_cyclic):
    n_handle_matrix = n_handle_matrix__from_tensor_matrix(
        bezier_func, n, tensor_matrix, cyclic=l_cyclic)

    n_handle_matrix = align__n_handle_matrix(n_handle_matrix)

    m_handle_matrix = m_handle_matrix__from_n_handle_matrix(
        bezier_func, m, n_handle_matrix, cyclic=t_cyclic)

    vertex_positions = vertex_positions__from_m_handle_matrix(
        m_handle_matrix, l_cyclic=l_cyclic, t_cyclic=t_cyclic)

    return vertex_positions


def vertex_positionss__from_silhuette_data(bezier_func, n, m, silhuette_data):
    tensor_matrix = interpolate_tensor_matrix(
        tensor_matrix__from_silhuette_data(silhuette_data))

    l_cyclic = silhuette_data['longitudinal']['cyclic']
    t_cyclic = silhuette_data['transversal']['cyclic']
    
    vertex_positions = vertex_positions__from_tensor_matrix(
        bezier_func, n, m, tensor_matrix, l_cyclic=l_cyclic, t_cyclic=t_cyclic)

    return vertex_positions




if __name__ == '__main__':
    print('\nhandle_matrix.py\n')

    from mesh_basic import toroidal_connect
    from bezier.silhuette import get_silhuette_data__from_active
    from bezier.vectors import bezier_cooss__uniform__num

    from bezier.discrete import bezier_discrete_uniform__num
    from mesh_basic import plot_vectors

    def bezier_f(n, p0, h0, h1, p1):
        coos, diffs, diff2s = bezier_discrete_uniform__num(n, p0, h0, h1, p1)
        return list(map(lambda coo: Vector(coo),
                        coos))

    context = bpy.context
    
    silhuette_data = get_silhuette_data__from_active(context)

    vertex_positionss = vertex_positionss__from_silhuette_data(
        bezier_f, 8, 8, silhuette_data)


    vectors = []
    for vertex_positions in vertex_positionss:
        for pos in vertex_positions:
            vectors.append(pos)
    plot_vectors(context, vectors)
