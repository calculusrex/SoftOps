import bpy
import bmesh
import numpy as np
from mathutils import Vector
from math import ceil, floor

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)

from geometry import vector_angle
from utils import reverse_list, flatten_lists, overlapping_pairs

def vertex_loop(vctrs):
    new_mesh = bmesh.new()
    new_verts = []
    for v in vctrs:
        new_verts.append(new_mesh.verts.new(v))
    for i in range(len(new_verts) - 1):
        new_mesh.edges.new(
            (new_verts[i], new_verts[i+1])
        )
    new_mesh.edges.new(
        (new_verts[-1], new_verts[0]))
    return new_mesh


def vertex_curve__from_position_vectors(position_vectors):
    
    bm = bmesh.new()

    verts = []
    edges = []

    for pos in position_vectors:
        verts.append(bm.verts.new(pos))

    for i in range(len(verts) - 1):
        edges.append(bm.edges.new((verts[i], verts[i+1])))

    return bm


def connect_sheet(mesh, vertss, flip=False):
    new_facess = []
    for i in range(len(vertss) - 1):
        new_faces = []
        for j in range(len(vertss[0]) - 1):
            if flip:
                new_faces.append(mesh.faces.new((
                    vertss[i][j],
                    vertss[i][j+1],
                    vertss[i + 1][j + 1],
                    vertss[i+1][j],
                )))                
            else:
                new_faces.append(mesh.faces.new((
                    vertss[i][j],
                    vertss[i + 1][j],
                    vertss[i + 1][j + 1],
                    vertss[i][j + 1],
                )))
        new_facess.append(new_faces)
    return new_facess



def connect_cyllinder(mesh, vertss):
    new_facess = []
    for i in range(len(vertss) - 1):
        new_faces = []
        for j in range(len(vertss[0]) - 1):
            new_faces.append(mesh.faces.new((
                vertss[i][j],
                vertss[i + 1][j],
                vertss[i + 1][j + 1],
                vertss[i][j + 1],
            )))
        new_faces.append(mesh.faces.new((
            vertss[i][-1],
            vertss[i + 1][-1],
            vertss[i + 1][0],
            vertss[i][0],
        )))
        new_facess.append(new_faces)

    return new_facess


def fore(i, n):
    if i == (n - 1):
        return 0
    else:
        return i + 1

def hind(i):
    if i == 0:
        return -1
    else:
        return i - 1


def adjecent_vectors(i, verts):
    n = len(verts)
    x, y, z = verts[hind(i)], verts[i], verts[fore(i, n)]
    a, b, c = x.co, y.co, z.co
    m, n = b-a, c-b
    return m, n

def fore_loop(a, b, xs):
    if b < a:
        ys = xs[a:]
        zs = xs[:(b+1)]
        return ys + zs
    else:
        return xs[a:(b+1)]

def hind_loop(a, b, xs):
    if b < a:
        return xs[b:(a+1)]
    else:
        ys = xs[b:]
        zs = xs[:(a+1)]
        return ys + zs

def half_fold_zip(xs):
    n = ceil(len(xs)/2)
    ys = xs[:n].copy()
    zs = xs[n:].copy()
    zs.reverse()
    
    return list(
        map(list,
            zip(ys, zs)))


def connect_cap__fusiform(mesh, verts, fiber_data):
    vert_data = []
    n = len(verts)
    for i in range(n):
        v = {}
        v['index'] = i
        v['vert'] = verts[i]
        v['fore_vert'] = verts[fore(i, n)]
        v['hind_vert'] = verts[hind(i)]
        v['fore_vector'] = v['fore_vert'].co - v['vert'].co
        v['hind_vector'] = v['vert'].co - v['hind_vert'].co
        v['tangent_vector'] = (v['fore_vector'] + v['hind_vector']) / 2
        v['chain_angle'] = vector_angle(v['fore_vector'],
                                        v['hind_vector'])
        vert_data.append(v)

    A = min(vert_data, key=lambda x: x['chain_angle'])

    search_domain = vert_data.copy()
    search_domain.remove(A)

    B = min(zip(vert_data,
                map(lambda v: abs(A['tangent_vector'].dot(v['vert'].co - A['vert'].co)),
                    search_domain)),
            key=lambda x: x[1])[0]

    same_parity__index = A['index'] % 2 == B['index'] % 2
    if same_parity__index:
        fore_prospect_marker = A['tangent_vector'].dot(
            vert_data[fore(B['index'], n)]['vert'].co - A['vert'].co)
        hind_prospect_marker = A['tangent_vector'].dot(
            vert_data[hind(B['index'])]['vert'].co - A['vert'].co)
        if fore_prospect_marker < hind_prospect_marker:
            B = vert_data[fore(B['index'], n)]
        else:
            B = vert_data[hind(B['index'])]

    fores = fore_loop(A['index'], B['index'], vert_data)
    hinds = hind_loop(A['index'], B['index'], vert_data)

    fore_band = half_fold_zip(fores)
    hind_band = half_fold_zip(hinds)

    faces = []
    faces.extend(
        connect_sheet(mesh,
                      list(map(lambda xs: list(map(lambda x: x['vert'], xs)),
                               fore_band))))
    faces.extend(
        connect_sheet(mesh,
                      list(map(lambda xs: list(map(lambda x: x['vert'], xs)),
                               hind_band))))

    return faces


def connect_cap__wide(mesh, verts, fibers_data):
    vert_data = []
    n = len(verts)
    for i in range(n):
        v = {}
        v['index'] = i
        v['vert'] = verts[i]
        v['fore_vert'] = verts[fore(i, n)]
        v['hind_vert'] = verts[hind(i)]
        v['fore_vector'] = v['fore_vert'].co - v['vert'].co
        v['hind_vector'] = v['vert'].co - v['hind_vert'].co
        v['tangent_vector'] = (v['fore_vector'] + v['hind_vector']) / 2
        v['chain_angle'] = vector_angle(v['fore_vector'],
                                        v['hind_vector'])
        vert_data.append(v)

    A = max(vert_data, key=lambda x: x['fore_vector'].magnitude) # different from connect_cap__fusiform
    
    search_domain = vert_data.copy()
    search_domain.remove(A)
    search_domain.sort(
        key=lambda x: abs(A['fore_vector'].magnitude - x['hind_vector'].magnitude)) # different from connect_cap__fusiform
    search_domain = search_domain[:(((len(fibers_data)-1) * 2) - 1)] # different from connect_cap__fusiform
    
    B = min(zip(search_domain,
                map(lambda v: abs(A['fore_vector'].dot(v['vert'].co - A['vert'].co)),
                    search_domain)),
            key=lambda x: x[1])[0] # different from connect_cap__fusiform

    same_parity__index = A['index'] % 2 == B['index'] % 2
    if same_parity__index:
        fore_prospect_marker = A['tangent_vector'].dot(
            vert_data[fore(B['index'], n)]['vert'].co - A['vert'].co)
        hind_prospect_marker = A['tangent_vector'].dot(
            vert_data[hind(B['index'])]['vert'].co - A['vert'].co)
        if fore_prospect_marker < hind_prospect_marker:
            B = vert_data[fore(B['index'], n)]
        else:
            B = vert_data[hind(B['index'])]

    fores = fore_loop(A['index'], B['index'], vert_data)
    hinds = hind_loop(A['index'], B['index'], vert_data)

    fore_band = half_fold_zip(fores)
    hind_band = half_fold_zip(hinds)


    faces = []
    faces.extend(
        connect_sheet(mesh,
                      list(map(lambda xs: list(map(lambda x: x['vert'], xs)),
                               fore_band))))
    faces.extend(
        connect_sheet(mesh,
                      list(map(lambda xs: list(map(lambda x: x['vert'], xs)),
                               hind_band))))

    return faces



def connect_cyllinder__capped(mesh, vertss, mesh_type, muscle_data):
    face_data = {}
    new_facess = []
    for i in range(len(vertss) - 1):
        new_faces = []
        for j in range(len(vertss[0]) - 1):
            new_faces.append(mesh.faces.new((
                vertss[i][j],
                vertss[i + 1][j],
                vertss[i + 1][j + 1],
                vertss[i][j + 1],
            )))
        new_faces.append(mesh.faces.new((
            vertss[i][-1],
            vertss[i + 1][-1],
            vertss[i + 1][0],
            vertss[i][0],
        )))
        new_facess.append(new_faces)
    face_data['body_facess'] = new_facess
    if mesh_type == 'WIDE':
        connect_cap_f = connect_cap__wide
    else:
        connect_cap_f = connect_cap__fusiform

    face_data['proximal_cap'] = connect_cap_f(mesh, vertss[0], muscle_data)
    face_data['distal_cap'] = connect_cap_f(mesh, reverse_list(vertss[-1]), muscle_data)

    return face_data



def sheet_vertss(mesh, pss):
    vert_loops = []
    for ps in pss:
        new_verts = []
        for p in ps:
            new_verts.append(mesh.verts.new(p))
        vert_loops.append(new_verts)
    
    return vert_loops


def cyllindrical_mesh(pss, mesh_type, muscle_data):
    new_mesh = bmesh.new()
    vert_loops = sheet_vertss(new_mesh, pss)
    facess = connect_cyllinder__capped(new_mesh, vert_loops, mesh_type, muscle_data)

    return vert_loops, facess, new_mesh


def flat_mesh(pss):
    mesh = bmesh.new()
    vertss = sheet_vertss(mesh, pss)
    facess = connect_sheet(mesh, vertss)
    
    return vertss, facess, mesh



def plot_vectors(context, vectors):
    bm = bmesh.new()

    if '__plot__' in bpy.data.objects.keys():
        ob = bpy.data.objects['__plot__']
        me = ob.data
        bm.from_mesh(me)
    else:
        me = bpy.data.meshes.new('__plot__')
        ob = bpy.data.objects.new('__plot__', me)
        context.collection.objects.link(ob)


    verts = []
    for v in vectors:
        verts.append(bm.verts.new(v))
    edges = []
    for i in range(len(verts) - 1):
        edges.append(
            bm.edges.new((verts[i], verts[i+1]))
        )

    bm.to_mesh(me)
    bm.free()



def toroidal_connect(bm, vertss, x_cyclic, y_cyclic, flip_normals=False):
    face_vertsss = flatten_lists(list(map(lambda xs: overlapping_pairs(xs, cyclic=x_cyclic),
                                          map(lambda xs: list(zip(*xs)),
                                              overlapping_pairs(vertss, cyclic=y_cyclic)))))
    faces = []
    for face_vertss in face_vertsss:
        if flip_normals:
            a, d = face_vertss[0]
            b, c = face_vertss[1]
        else:    
            a, b = face_vertss[0]
            d, c = face_vertss[1]
        faces.append(bm.faces.new((a, b, c, d)))

    return faces
        
    

    




if __name__ == '__main__':
    print('boom')
    
    vectors = list(map(lambda x: Vector((x, 0, x**4)),
                       np.arange(0, 1, 0.01)))
    
        
    plot_vectors(bpy.context, vectors)
