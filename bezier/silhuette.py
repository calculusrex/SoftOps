import bpy
import functools as ft
import numpy as np
from mathutils import Vector

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)


from utils import is_even, is_odd, are_all_true, maybe_first
from bezier.spline import rotate_bezier_point_position
from rename import coil__bone_name as coil__object_name
from rename import uncoil__bone_name as uncoil__object_name
from rename import number__bone_name as n__object_name



unit_vectors = {
    'i': Vector((1, 0, 0)),
    'j': Vector((0, 1, 0)),
    'k': Vector((0, 0, 1)),
}

i = Vector((1, 0, 0))
j = Vector((0, 1, 0))
k = Vector((0, 0, 1))



spline_roles = ['handle', 'core']
spline_axis = ['longitudinal', 'transversal']






def mirror_vector(subject_vector, normal_axis):
    x, y, z = (subject_vector.x * i), (subject_vector.y * j), (subject_vector.z * k)
    if normal_axis == 'x':
        return -x + y + z
    if normal_axis == 'y':
        return x + -y + z
    if normal_axis == 'z':
        return x + y + -z




def get_name_data__from_active(context):
    active_ob = context.active_object    
    active_ob__name_data = uncoil__object_name(active_ob.name)
    return active_ob__name_data





def get_name_data(ob):
    return uncoil__object_name(ob.name)


def get_name_core__from_active(context):
    name_data = uncoil__object_name(context.active_object.name)
    return name_data['name']


def axis__from_name_data(name_data):
    if 'longitudinal' in name_data['sufs']:
        return 'longitudinal'
    elif 'transversal' in name_data['sufs']:
        return 'transversal'
    else:
        return None

# CURRENTLY NOT IN USE
def role__from_name_data(name_data):
    if 'core' in name_data['sufs']:
        return 'core'
    elif 'handle' in name_data['sufs']:
        return 'handle'
    else:
        return None

# CURRENTLY NOT IN USE
def handle_side__from_name_data(name_data):
    if 'handle' in name_data['sufs'] and 'up' in name_data['sufs']:
        return 'up'
    elif 'handle' in name_data['sufs'] and 'down' in name_data['sufs']:
        return 'down'
    else:
        return None


def name_discriminator(name_data_f, name=None, side=None, n=None, sufs_present=[], pres_present=[]):    
    def discriminate(ob):
        name_data = name_data_f(ob)        
        evidence = []
        if name != None:
            evidence.append(name == name_data['name'])            
        if side != None:
            evidence.append(side == name_data['side'])            
        if n != None:
            evidence.append(n == int(name_data['n']))            
        if sufs_present != []:
            all_present = True
            for suf in sufs_present:
                if suf not in name_data['sufs']:
                    all_present = False
            evidence.append(all_present)            
        if pres_present != []:
            all_present = True
            for pref in pres_present:
                if pref not in name_data['pres']:
                    all_present = False
            evidence.append(all_present)            
        return ft.reduce(lambda a, b: a and b,
                         evidence,
                         True)
    return discriminate


def is_spline(ob):
    name_data = get_name_data(ob)
    return 'SPL' in name_data['pres']


def get_splines_by_name_core(context, name_core):
    all_splines = list(filter(is_spline,
                              bpy.data.objects))
    
    return list(filter(name_discriminator(get_name_data, name=name_core),
                       all_splines))

def vector_mean(vectors):
    s = ft.reduce(lambda a, b: a + b,
                  vectors)
    n = len(vectors)
    return s / n

# NOT IN USE, PROBABLY BROKEN, BUT INTERESTING CONCEPT
def convexity_vector(nodes):
    cs = list(map(lambda n: n['core'], nodes))
    o = (cs[0] + cs[-1]) / 2
    r = vector_mean(cs[1:-1])
    return r - o


def get_spline_data(context, ob, axis, role):
    spline = ob.data.splines[0]
    data = {}
    data['object'] = ob
    data['spline'] = spline
    data['name'] = ob.name
    data['name_data'] = uncoil__object_name(ob.name)

    data['nodes'] = []
    for bezier_point in spline.bezier_points:
        point_data = {}
        point_data['core'] = bezier_point.co.copy()
        point_data['up_handle'] = bezier_point.handle_left.copy()
        point_data['down_handle'] = bezier_point.handle_right.copy()

        data['nodes'].append(point_data)

    for i in range(len(data['nodes'])):
        data['nodes'][i]['pos'] = i

    data['axis'] = axis
    data['role'] = role
    # data['convexity_vector'] = convexity_vector(data['nodes'])
    data['cyclic'] = spline.use_cyclic_u
    
    return data


def get_column_data(silhuette_data, axis, i):
    data = {}
    data['core'] = silhuette_data[axis]['core'][i]
    data['up_handle'] = maybe_first(list(filter(name_discriminator(lambda spline_data: spline_data['name_data'],
                                                                   sufs_present=[axis, 'handle', 'up'],
                                                                   n=i),
                                                silhuette_data[axis]['handle'])))
    data['down_handle'] = maybe_first(list(filter(name_discriminator(lambda spline_data: spline_data['name_data'],
                                                                     sufs_present=[axis, 'handle', 'down'],
                                                                     n=i),
                                                  silhuette_data[axis]['handle'])))
    return data



    

def get_silhuette_data(context, name_core):
    obs = get_splines_by_name_core(context, name_core)
    data = {}
    data['name_core'] = name_core
    data['objects'] = {}
    data['objects']['all'] = obs
    for axis in spline_axis:
        data['objects'][axis] = {}
        data['objects'][axis]['all'] = list(filter(name_discriminator(get_name_data, sufs_present=[axis]),
                                                   obs))
        data['objects'][axis]['all'].sort(key=lambda o: int(n__object_name(o.name)))
        for role in spline_roles:
            data['objects'][axis][role] = list(filter(name_discriminator(get_name_data, sufs_present=[axis, role]),
                                                      obs))
            data['objects'][axis][role].sort(key=lambda o: int(n__object_name(o.name))) # they are not in consecutive bezier point manifold order
    for axis in spline_axis:
        data[axis] = {}
        for role in spline_roles:
            data[axis][role] = list(map(lambda ob: get_spline_data(context, ob, axis, role),
                                        data['objects'][axis][role]))
        data[axis]['all'] = data[axis]['core'] + data[axis]['handle']
        data[axis]['all'].sort(key=lambda spl_dat: int(spl_dat['name_data']['n']))

    data['all'] = data['longitudinal']['all'] + data['transversal']['all']

    data['longitudinal']['cyclic'] = are_all_true(map(lambda spl_dat: spl_dat['cyclic'],
                                          data['longitudinal']['all']))
    data['transversal']['cyclic'] = are_all_true(map(lambda spl_dat: spl_dat['cyclic'],
                                          data['transversal']['all']))

    for axis in spline_axis:
        data[axis]['columns'] = []
        for i in range(len(data[axis]['core'])):
            data[axis]['columns'].append(get_column_data(data, axis, i))

    return data



def get_silhuette_data__from_active(context):
    active_ob__name_core = get_name_core__from_active(context)
    silhuette_data = get_silhuette_data(context, active_ob__name_core)
    return silhuette_data




def bezier_point_data(bezier_point):
    data = {}
    data['core'] = bezier_point.co.copy()
    data['up_handle'] = bezier_point.handle_left.copy()
    data['down_handle'] = bezier_point.handle_right.copy()
    return data


def mirror__point_data(point_data, normal_axis):
    for key in point_data.keys():
        v = point_data[key].copy()
        point_data[key] = mirror_vector(v, normal_axis)    


def update_bezier_point(bezier_point, vector_data):
    bezier_point.co = vector_data['core']
    bezier_point.handle_left = vector_data['up_handle']
    bezier_point.handle_right = vector_data['down_handle']


def mirror_bezier_point(bezier_point, normal_axis):
    point_data = bezier_point_data(bezier_point)
    mirror_point_data(point_data, normal_axis)
    update_bezier_point(bezier_point, point_data)


def switch_handles__point_data(point_data):
    core = point_data['core'].copy()
    up_handle = point_data['up_handle'].copy()
    down_handle = point_data['down_handle'].copy()

    point_data['core'] = core
    point_data['up_handle'] = down_handle
    point_data['down_handle'] = up_handle


def align_node_axially(node, normal_axis):
    for key in ['core', 'up_handle', 'down_handle']:
        if normal_axis == 'x':
            node[key].x = 0
        elif normal_axis == 'y':
            node[key].y = 0
        else:
            node[key].z = 0
    return node


def point_data__symmetrize_handles__aligned(point_data, normal_axis, direction):
    up = point_data['up_handle'].copy()
    down = point_data['down_handle'].copy()
    r = point_data['core'].copy()
    u = up - r
    d = down - r
    if normal_axis == 'x':
        u = u.x * i
        d = d.x * i
        r.x = 0
    elif normal_axis == 'y':
        u = u.y * j
        d = d.y * j
        r.y = 0
    else: # normal_axis == 'z'
        u = u.z * k
        d = d.z * k
        r.z = 0
        
    if direction == 'upstream':
        e = -u
    else:
        e = d

    point_data['core'] = r    
    point_data['up_handle'] = r - e
    point_data['down_handle'] = r + e



def mirror_off_center_bezier_data(bezier_points__init, axis, side_to_mirror, cyclic=False):
    if cyclic:
        bezier_points = bezier_points__init[1:]
    else:
        bezier_points = bezier_points__init

    h = int(len(bezier_points) / 2)
    even = is_even(len(bezier_points))

    if even:
        if side_to_mirror == 'upstream':
            source_bezier_points = bezier_points[:h]
            destination_bezier_points = bezier_points[h:]
        else:
            source_bezier_points = bezier_points[h:]
            destination_bezier_points = bezier_points[:h]
    else:
        if side_to_mirror == 'upstream':
            source_bezier_points = bezier_points[:h]
            destination_bezier_points = bezier_points[h+1:]
        else:
            source_bezier_points = bezier_points[h+1:]
            destination_bezier_points = bezier_points[:h]
    
    mirrored_data = []
    for bp in source_bezier_points:
        point_data = bezier_point_data(bp)
        switch_handles__point_data(point_data)
        mirror__point_data(point_data, axis)        
        mirrored_data.append(point_data)
    mirrored_data.reverse()

    for point_data, bp in zip(mirrored_data, destination_bezier_points):
        update_bezier_point(bp, point_data)


def mirror_centered_data(bezier_points, axis, side_to_mirror, cyclic=False):
    n = len(bezier_points)
    h = int(n/2)
    if cyclic:
        if is_odd(n):
            midpoint_indices = [0]
        else:
            midpoint_indices = [0, h]
    else:
        if is_odd(n):
            midpoint_indices = [h]
        else:
            midpoint_indices = []

    sides_to_mirror = ['downstream', 'upstream']
    if side_to_mirror == 'downstream':
        sides_to_mirror.reverse()

    midpoint_data = []
    for i, side in zip(midpoint_indices, sides_to_mirror):
        midpoint = bezier_point_data(bezier_points[i])
        point_data__symmetrize_handles__aligned(midpoint,
                                                axis,
                                                side)
        
        update_bezier_point(bezier_points[i], midpoint)
        


def symmetrize_spline(spline_data, axis, side_to_mirror, cyclic=False):
    bezier_points = spline_data['object'].data.splines[0].bezier_points
    n = len(bezier_points)
    h = int(n / 2)

    mirror_off_center_bezier_data(
        bezier_points, axis, side_to_mirror, cyclic=cyclic)

    mirror_centered_data(
        bezier_points, axis, side_to_mirror, cyclic=cyclic)

def maybe_symmetrize_spline(spline_data, axis, side_to_mirror, cyclic=False):
    if spline_data != None:
        symmetrize_spline(spline_data, axis, side_to_mirror, cyclic=cyclic)


def switch_column_handle_splines(column):
    # core = column['core'].copy()
    # column['core'] = core
    if column['up_handle'] != None and column['down_handle'] != None:
        up_handle = column['up_handle'].copy()
        down_handle = column['down_handle'].copy()
        column['up_handle'] = down_handle
        column['down_handle'] = up_handle
    return column


def mirror_spline_node(node, normal_axis):
    for key in ['core', 'up_handle', 'down_handle']:
        node[key] = mirror_vector(node[key], normal_axis)
    return node


def mirror_spline(spline_data, normal_axis):
    for node in spline_data['nodes']:
        node = mirror_spline_node(node, normal_axis)
    return spline_data

def maybe_mirror_spline(spline_data, normal_axis):
    if spline_data == None:
        return None
    else:
        return mirror_spline(spline_data, normal_axis)

def align_spline_axially(spline_data, normal_axis):
    for node in spline_data['nodes']:
        node = align_node_axially(node, normal_axis)
    return spline_data


def mirror__column(column, normal_axis):
    print()
    print('mirror__column')
    print('column')
    print(column)
    print()
    for key in ['core', 'up_handle', 'down_handle']:
        column[key] = maybe_mirror_spline(column[key],
                                          normal_axis)
    return column



def update__column(source_column_data, destination_column):
    for key in ['core', 'up_handle', 'down_handle']:
        if source_column_data[key] != None and destination_column[key] != None:
            for i in range(len(destination_column[key]['nodes'])):
                update_bezier_point(destination_column[key]['spline'].bezier_points[i],
                                    source_column_data[key]['nodes'][i])

def update__spline(source_spline_data, destination_spline_data):
    for i in range(len(destination_spline_data['nodes'])):
        update_bezier_point(destination_spline_data['spline'].bezier_points[i],
                            source_spline_data['nodes'][i])



def symmetrize_off_center_columns(columns, axis, side_to_mirror, cyclic=False):
    print()
    print('symmetrize_off_center_columns')
    print()
    
    if cyclic:
        columns = columns[1:].copy()
    else:
        columns = columns.copy()

    n = len(columns)
    h = int(n / 2)
        
    if is_even(n):
        if side_to_mirror == 'upstream':
            source_columns = columns[:h].copy()
            destination_columns = columns[h:]
        else:
            source_columns = columns[h:].copy()
            destination_columns = columns[:h]
    else:
        if side_to_mirror == 'upstream':
            source_columns = columns[:h].copy()
            destination_columns = columns[h+1:]
        else:
            source_columns = columns[h+1:].copy()
            destination_columns = columns[:h]

    mirrored_columns = []
    for column in source_columns:
        column = switch_column_handle_splines(column)
        column = mirror__column(column, axis)        
        mirrored_columns.append(column)
    mirrored_columns.reverse()

    for source_column, destination_column in zip(mirrored_columns, destination_columns):
        update__column(source_column, destination_column)
        



def symmetrize_column_splines__aligned(column, axis, side_to_mirror):
    if column['down_handle'] != None and column['up_handle'] != None:

        if side_to_mirror == 'downstream':
            source_handle_spline = mirror_spline(
                column['down_handle'], axis)
            update__spline(source_handle_spline, column['up_handle'])
            
        else: # side_to_mirror == 'upstream':
            source_handle_spline = mirror_spline(
                column['up_handle'], axis)
            update__spline(source_handle_spline, column['down_handle'])

    source_core_data = align_spline_axially(column['core'], axis)
    update__spline(source_core_data, column['core'])



def symmetrize_axial_columns(columns, axis, side_to_mirror, cyclic=False):
    n = len(columns)
    h = int(n / 2)

    if cyclic:
        if is_odd(n):
            axial_indices = [0]
        else:
            axial_indices = [0, h]
    else:
        if is_odd(n):
            axial_indices = [h]
        else:
            axial_indices = []


    if side_to_mirror == 'upstream':
        sides_to_mirror = ['downstream', 'upstream']
    else: # downstream
        sides_to_mirror = ['upstream', 'downstream']

    for i, side in zip(axial_indices, sides_to_mirror):
        axial_col = columns[i].copy()
        symmetrize_column_splines__aligned(axial_col,
                                           axis,
                                           side)


def symmetrize_columns__normal_plane_parallel(columns, normal_axis, side_to_mirror, cyclic=False):

    symmetrize_off_center_columns(
        columns, normal_axis, side_to_mirror, cyclic=cyclic
    )

    symmetrize_axial_columns(
        columns, normal_axis, side_to_mirror, cyclic=cyclic
    )



def symmetrize_columns__normal_plane_intersecting(columns, normal_axis, side_to_mirror, cyclic=False):
    for column in columns:
        for key in ['core', 'up_handle', 'down_handle']:
            maybe_symmetrize_spline(column[key], normal_axis, side_to_mirror, cyclic=cyclic)        


def symmetrize_silhuette(silhuette_data, normal_axis, side_to_mirror):

    if normal_axis == 'y':
        plane_parallel_axis = 'transversal'
        plane_intersecting_axis = 'longitudinal'
    else: # normal_axis == 'x' or normal_axis == 'z'
        plane_parallel_axis = 'longitudinal'
        plane_intersecting_axis = 'transversal'

    plane_parallel_columns = silhuette_data[plane_parallel_axis]['columns']
    plane_intersecting_columns = silhuette_data[plane_intersecting_axis]['columns']

    cyclic = silhuette_data[plane_intersecting_axis]['cyclic']
    if not cyclic:
        if side_to_mirror == 'upstream':
            side_to_mirror = 'downstream'
        else:
            side_to_mirror = 'upstream'
    
    symmetrize_columns__normal_plane_parallel(
        plane_parallel_columns, normal_axis, side_to_mirror, cyclic=cyclic)

    symmetrize_columns__normal_plane_intersecting(
        plane_intersecting_columns, normal_axis, side_to_mirror, cyclic=cyclic)



def update_spline_numbering(i, spline_data):
    spline_data['name_data']['n'] = i
    spline_data['object'].name = coil__object_name(
        spline_data['name_data'])

    
def update_column_numbering(i, column):
    for key in ['core', 'up_handle', 'down_handle']:
        update_spline_numbering(i, column[key])


def rotate_spline(c, spline_data):
    rotate_bezier_point_position(spline_data['object'], c)

def rotate_columns(c, columns):
    n = len(columns)
    rotate_index = lambda i: (i - c) % n
    for column in columns:
        i = column['core']['name_data']['n']
        update_column_numbering(rotate_index(i), column)


def rotate_silhuette(c, silhuette_data):
    
    rotate_columns(c, silhuette_data['longitudinal']['columns'])

    for column in silhuette_data['transversal']['columns']:
        for key in ['core', 'up_handle', 'down_handle']:
            rotate_spline(c, column[key])


def refresh_silhuette_spline_names(silhuette_data):
    for axis in ['transversal', 'longitudinal']:
        for col in silhuette_data[axis]['columns']:
            for key in ['core', 'up_handle', 'down_handle']:
                if col[key] != None:
                    print()
                    print('name_data')
                    print(col[key]['name_data'])
                    col[key]['object'].name = coil__object_name(col[key]['name_data'])


def refresh_silhuette_spline_names__from_active(context):
    silhuette_data = get_silhuette_data__from_active(context)
    refresh_silhuette_spline_names(silhuette_data)


def symmetrize_silhuette__from_active(context, axis, side_to_mirror):
    silhuette_data = get_silhuette_data__from_active(context)
    if axis == 'z':
        n = len(silhuette_data['longitudinal']['columns'])
        c = int(n / 4)
        rotate_silhuette(c, silhuette_data)

    silhuette_data = get_silhuette_data__from_active(context)
    symmetrize_silhuette(silhuette_data, axis, side_to_mirror)    

    if axis == 'z':
        n = len(silhuette_data['longitudinal']['columns'])
        c = int(n / 4)
        rotate_silhuette(-c, silhuette_data)
        
        refresh_silhuette_spline_names(silhuette_data)



class RefreshSilhuetteSplineNames(bpy.types.Operator):
    bl_idname = 'object.refresh_silhuette_spline_names'
    bl_label = 'Refresh Silhuette Spline Names'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        refresh_silhuette_spline_names__from_active(context)
        return {'FINISHED'}


        
class SymmetrizeSilhuette_NegX(bpy.types.Operator):
    bl_idname = 'object.symmetrize_silhuette_neg_x'
    bl_label = 'Symmetrize Silhuette -X'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        symmetrize_silhuette__from_active(context, 'x', 'upstream')
        return {'FINISHED'}

class SymmetrizeSilhuette_PosX(bpy.types.Operator):
    bl_idname = 'object.symmetrize_silhuette_pos_x'
    bl_label = 'Symmetrize Silhuette +X'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        symmetrize_silhuette__from_active(context, 'x', 'downstream')
        return {'FINISHED'}


class SymmetrizeSilhuette_NegY(bpy.types.Operator):
    bl_idname = 'object.symmetrize_silhuette_neg_y'
    bl_label = 'Symmetrize Silhuette -Y'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        symmetrize_silhuette__from_active(context, 'y', 'upstream')
        return {'FINISHED'}

class SymmetrizeSilhuette_PosY(bpy.types.Operator):
    bl_idname = 'object.symmetrize_silhuette_pos_y'
    bl_label = 'Symmetrize Silhuette +Y'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        symmetrize_silhuette__from_active(context, 'y', 'downstream')
        return {'FINISHED'}


class SymmetrizeSilhuette_NegZ(bpy.types.Operator):
    bl_idname = 'object.symmetrize_silhuette_neg_z'
    bl_label = 'Symmetrize Silhuette -Z'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        symmetrize_silhuette__from_active(context, 'z', 'upstream')
        return {'FINISHED'}

class SymmetrizeSilhuette_PosZ(bpy.types.Operator):
    bl_idname = 'object.symmetrize_silhuette_pos_z'
    bl_label = 'Symmetrize Silhuette +Z'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        symmetrize_silhuette__from_active(context, 'z', 'downstream')
        return {'FINISHED'}


keyless_operator_classes = [
    SymmetrizeSilhuette_PosX,
    SymmetrizeSilhuette_NegX,
    SymmetrizeSilhuette_PosY,
    SymmetrizeSilhuette_NegY,
    SymmetrizeSilhuette_PosZ,
    SymmetrizeSilhuette_NegZ
]

keyless_op_data = []
for c in keyless_operator_classes:
    keyless_op_data.append({
        'class': c
    })


operator_data = []
operator_data.append({
    'class': RefreshSilhuetteSplineNames,
    'keymap': 'O',
    'ctrl': False,
    'alt': True,
    'shift': True,
})



if __name__ == '__main__':
    print('silhuette.py')
