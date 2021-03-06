import bpy
import bmesh
from mathutils import Vector

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)

from bezier.json_subprocess_interface import call_bezier
from mesh_basic import toroidal_connect
from utils import flatten_lists

from bezier.vectors import bezier_cooss__uniform__num, bezier_cooss__adaptive__num, bezier_cooss__uniform__sym, bezier_cooss__adaptive__sym #, bezier_cooss__uniform__num__auto_aligned, bezier_cooss__adaptive__num__auto_aligned, bezier_cooss__uniform__sym__auto_aligned, bezier_cooss__adaptive__sym__auto_aligned

from bezier.handle_matrix import handle_matrix__from_active
from bezier.handle_matrix import vertex_positionss__from_silhuette_data

from bezier.discrete import bezier_discrete_adaptive__num, bezier_discrete_uniform__num



just_coos = lambda xs: xs[0]


bezier_cooss_lambs = {
    'uniform_sym': bezier_cooss__uniform__sym,
    'adaptive_sym': bezier_cooss__adaptive__sym,
    'uniform_num': bezier_cooss__uniform__num,
    'adaptive_num': bezier_cooss__adaptive__num,
    # 'uniform_sym__auto_aligned': bezier_cooss__uniform__sym__auto_aligned,
    # 'adaptive_sym__auto_aligned': bezier_cooss__adaptive__sym__auto_aligned,
    # 'uniform_num__auto_aligned': bezier_cooss__uniform__num__auto_aligned,
    # 'adaptive_num__auto_aligned': bezier_cooss__adaptive__num__auto_aligned

}



def bezier_panel(bm, vertex_distribution, n, m, P0, H0, H1, P1,
                 longitudinal_intermediate=False, transversal_intermediate=False):

    cooss = bezier_cooss_lambs[
        vertex_distribution](
            n, m, P0, H0, H1, P1)

    if longitudinal_intermediate:
        cooss = cooss[1:]
    
    if transversal_intermediate:
        cooss = list(map(lambda coos: coos[1:],
                         cooss))

    vertex_data = {}
    vertex_data['-x edge'] = list(map(lambda coos: coos[0], cooss))
    vertex_data['x edge'] = list(map(lambda coos: coos[-1], cooss))
    vertex_data['-y edge'] = cooss[0]
    vertex_data['y edge'] = cooss[-1]
    
    vertss = list(map(lambda curve: list(map(lambda coo: bm.verts.new(coo), curve)),
                      cooss))

    return vertss, vertex_data



# def bezier_panel__auto_aligned(bm, vertex_distribution, n, m, handle_panel_triple,
#                  longitudinal_intermediate=False, transversal_intermediate=False):

#     cooss = bezier_cooss_lambs[
#         vertex_distribution](
#             n, m, handle_panel_triple)

#     if longitudinal_intermediate:
#         cooss = cooss[1:]
    
#     if transversal_intermediate:
#         cooss = list(map(lambda coos: coos[1:],
#                          cooss))

#     vertex_data = {}
#     vertex_data['-x edge'] = list(map(lambda coos: coos[0], cooss))
#     vertex_data['x edge'] = list(map(lambda coos: coos[-1], cooss))
#     vertex_data['-y edge'] = cooss[0]
#     vertex_data['y edge'] = cooss[-1]
    
#     vertss = list(map(lambda curve: list(map(lambda coo: bm.verts.new(coo), curve)),
#                       cooss))

#     return vertss, vertex_data




def bezier_vert_strip__from_handle_panels(bm, vertex_distribution, n, m, handle_panels,
                                          longitudinally_cyclic=False, transversal_intermediate=False):
    accumulated_vert_data = []
    accumulated_vertss = []
    vertss, vert_data = bezier_panel(bm, vertex_distribution, n, m, *handle_panels[0],
                                     longitudinal_intermediate=longitudinally_cyclic,
                                     transversal_intermediate=transversal_intermediate)
    accumulated_vertss.extend(vertss)
    accumulated_vert_data.extend(vert_data)

    for handle_panel in handle_panels[1:]:
        vertss, vert_data = bezier_panel(bm, vertex_distribution, n, m, *handle_panel,
                                         longitudinal_intermediate=True,
                                         transversal_intermediate=transversal_intermediate)
        accumulated_vertss.extend(vertss)
        accumulated_vert_data.extend(vert_data)
        
    return accumulated_vertss, accumulated_vert_data



# def bezier_vert_strip__from_handle_panels__auto_aligned(bm, vertex_distribution, n, m,
#                                                         handle_panel_triples,
#                                                         longitudinally_cyclic=False,
#                                                         transversal_intermediate=False):
#     accumulated_vert_data = []
#     accumulated_vertss = []
#     vertss, vert_data = bezier_panel__auto_aligned(
#         bm, vertex_distribution, n, m, handle_panel_triple[0],
#         longitudinal_intermediate=longitudinally_cyclic,
#         transversal_intermediate=transversal_intermediate)

#     accumulated_vertss.extend(vertss)
#     accumulated_vert_data.extend(vert_data)

#     for handle_panel_triple in handle_panels_triples[1:]:
#         vertss, vert_data = bezier_panel__auto_aligned(
#             bm, vertex_distribution, n, m, handle_panel_triple,
#             longitudinal_intermediate=True,
#             transversal_intermediate=transversal_intermediate)

#         accumulated_vertss.extend(vertss)
#         accumulated_vert_data.extend(vert_data)
        
#     return accumulated_vertss, accumulated_vert_data
        



def bezier_vert_mesh__from_handle_matrix(bm, vertex_distribution, n, m, handle_matrix,
                                         longitudinally_cyclic=False, transversally_cyclic=False):
    accumulated_vert_data = []
    accumulated_vertsss = []

    vertss, vert_data = bezier_vert_strip__from_handle_panels(
        bm, vertex_distribution, n, m, handle_matrix[0],
        longitudinally_cyclic=longitudinally_cyclic,
        transversal_intermediate=transversally_cyclic)
    accumulated_vertsss.append(vertss)
    accumulated_vert_data.append(vert_data)

    for handle_panel_strip in handle_matrix[1:]:
        vertss, vert_data = bezier_vert_strip__from_handle_panels(
            bm, vertex_distribution, n, m, handle_panel_strip,
            longitudinally_cyclic=longitudinally_cyclic,
            transversal_intermediate=True)
        accumulated_vertsss.append(vertss)
        accumulated_vert_data.append(vert_data)

    accumulated_vertsss = list(map(flatten_lists,
                                  map(list,
                                         zip(*accumulated_vertsss))))
    accumulated_vert_data = list(map(flatten_lists,
                                     map(list,
                                         zip(*accumulated_vert_data))))
    return accumulated_vertsss, accumulated_vert_data



def bezier_mesh__from_handle_matrix(vertex_distribution, n, m, handle_matrix,
                                    longitudinally_cyclic=False, transversally_cyclic=False):
    bm = bmesh.new()

    vertss, vert_data = bezier_vert_mesh__from_handle_matrix(
        bm, vertex_distribution, n, m, handle_matrix,
        longitudinally_cyclic=longitudinally_cyclic,
        transversally_cyclic=transversally_cyclic)

    faces = toroidal_connect(bm, vertss,
                             x_cyclic=transversally_cyclic,
                             y_cyclic=longitudinally_cyclic)

    return bm, vert_data





def install_vertss(bm, vertex_positionss):
    vertss = []
    for vertex_positions in vertex_positionss:
        verts = []
        for vertex_position in vertex_positions:
            verts.append(
                bm.verts.new(vertex_position)
            )
        vertss.append(verts)
    return vertss


def bezier_mesh__from_silhuette_data(bezier_f, n, m, silhuette_data, flip_normals=False):
    bm = bmesh.new()

    longitudinally_cyclic = silhuette_data['longitudinal']['cyclic']
    transversally_cyclic = silhuette_data['transversal']['cyclic']
    
    vertex_positionss = vertex_positionss__from_silhuette_data(
        bezier_f, n, m, silhuette_data)

    vertss = install_vertss(bm, vertex_positionss)

    faces = toroidal_connect(bm, vertss,
                             x_cyclic=transversally_cyclic,
                             y_cyclic=longitudinally_cyclic,
                             flip_normals=flip_normals)

    return bm


if __name__ == '__main__':
    print('mesh.py')
    print()
