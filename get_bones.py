import bpy
import functools as ft
from mathutils import Vector

# import sys
# dev_path = '/home/feral/engineering/addon_workshop/softops'
# sys.path.insert(1, dev_path)

from rename import is_bone_name_of_wide_muscle_rig, coil__bone_name, uncoil__bone_name, name__bone_name, number__bone_name, side__bone_name, sufs__bone_name
from utils import are_all_true, is_one_of_them_true
from edit_bones import select_n_set_active__edit_bone


c_fiber_sufss = {}
c_fiber_sufss['muscle'] = []
c_fiber_sufss['origin'] = ['origin']
c_fiber_sufss['origin_tracker'] = ['origin', 'tracker']
c_fiber_sufss['insertion'] = ['insertion']
c_fiber_sufss['insertion_tracker'] = ['insertion', 'tracker']
c_fiber_sufss['bend_target'] = ['bend', 'target']

s_fiber_sufss = {}
s_fiber_sufss['muscle'] = []
s_fiber_sufss['origin'] = ['origin']
s_fiber_sufss['origin_tracker'] = ['origin', 'tracker']
s_fiber_sufss['insertion'] = ['insertion']
s_fiber_sufss['insertion_tracker'] = ['insertion', 'tracker']
s_fiber_sufss['origin_bend_target'] = ['origin', 'bend', 'target']
s_fiber_sufss['insertion_bend_target'] = ['insertion', 'bend', 'target']

double_fiber_sufss = {}
double_fiber_sufss['muscle_proximal'] = ['proximal']
double_fiber_sufss['muscle_distal'] = ['distal']
double_fiber_sufss['origin'] = ['origin']
double_fiber_sufss['origin_tracker'] = ['origin', 'tracker']
double_fiber_sufss['midpoint_origin'] = ['midpoint', 'origin']
double_fiber_sufss['midpoint_insertion'] = ['midpoint', 'insertion']
double_fiber_sufss['insertion'] = ['insertion']
double_fiber_sufss['insertion_tracker'] = ['insertion', 'tracker']
double_fiber_sufss['origin_bend_target'] = ['origin', 'bend', 'target']
double_fiber_sufss['insertion_bend_target'] = ['insertion', 'bend', 'target']

fiber_type__sufss = {}
fiber_type__sufss['C'] = c_fiber_sufss
fiber_type__sufss['S'] = s_fiber_sufss
fiber_type__sufss['DOUBLE'] = double_fiber_sufss

fiber_type__keys = {}
for ftype in fiber_type__sufss.keys():
    fiber_type__keys[ftype] = list(
        fiber_type__sufss[ftype].keys())


def key_from_sufs(sufs):
    if sufs == []:
        return 'muscle'
    else:
        ft.reduce(lambda a, b: f'{a}_{b}',
                  sufs)

def sufs_from_key(key):
    if key == 'muscle':
        return []
    else:
        return key.split('_')


def bone_name_sufs__in__sufss(bone, sufss):
    name_data = uncoil__bone_name(bone.name)
    return name_data['sufs'] in sufss


def do_sufss_apply(bones, sufss):
    return are_all_true(
        map(lambda bone: bone_name_sufs__in__sufss(bone, sufss.values()),
            bones))


def fiber_rig_type(bones):
    for key in fiber_type__sufss.keys():
        if do_sufss_apply(bones, fiber_type__sufss[key]):
            return key


def pick_bone(bones, name, n, sufs):
    for bone in bones:
        name_data = uncoil__bone_name(bone.name)
        right_name = name_data['name'] == name
        right_n = name_data['n'] == n
        right_sufs = name_data['sufs'] == sufs
        if are_all_true([right_name, right_n, right_sufs]):
            return bone


def grip_fiber_bones(bones__single_fiber, fiber_type):
    fiber_type_data = fiber_type__sufss[fiber_type]
    fiber_data = {}
    name_data = uncoil__bone_name(bones__single_fiber[0].name)
    fiber_data['type'] = fiber_type
    fiber_data['name'] = name_data['name']
    fiber_data['n'] = name_data['n']
    fiber_data['fiber_identifier'] = f'{name_data["name"]}_{name_data["n"]}'
    for key in fiber_type_data.keys():
        fiber_data[key] = pick_bone(bones__single_fiber,
                                    fiber_data['name'],
                                    fiber_data['n'],
                                    fiber_type_data[key])
    return fiber_data
    


def get_fiber_vector_data(fiber_data):

    vector_data = {}
    if fiber_data['type'] == 'DOUBLE':
        vector_data['origin'] = fiber_data['muscle_proximal'].head
        vector_data['insertion'] = fiber_data['muscle_distal'].tail
    else:
        vector_data['origin'] = fiber_data['muscle'].head
        vector_data['insertion'] = fiber_data['muscle'].tail
    
    vector_data['vector'] = vector_data['insertion'] - vector_data['origin']

    vector_data['reach'] = vector_data['vector'].magnitude

    vector_data['origin_axes'] = {}
    vector_data['origin_axes']['x'] = fiber_data['origin'].x_axis
    vector_data['origin_axes']['y'] = fiber_data['origin'].y_axis
    vector_data['origin_axes']['z'] = fiber_data['origin'].z_axis
    
    vector_data['insertion_axes'] = {}
    vector_data['insertion_axes']['x'] = fiber_data['insertion'].x_axis
    vector_data['insertion_axes']['y'] = fiber_data['insertion'].y_axis
    vector_data['insertion_axes']['z'] = fiber_data['insertion'].z_axis
    
    vector_data['origin_orientation'] = fiber_data['origin'].vector
    vector_data['origin_orientation'] /= vector_data['origin_orientation'].magnitude

    vector_data['insertion_orientation'] = fiber_data['insertion'].vector
    vector_data['insertion_orientation'] /= vector_data['insertion_orientation'].magnitude

    if fiber_data['type'] == 'DOUBLE':
        vector_data['midpoint_insertion'] = fiber_data['midpoint_insertion'].head
        vector_data['midpoint'] = fiber_data['muscle_proximal'].tail
        vector_data['vector_proximal'] = vector_data['midpoint_insertion'] - vector_data['origin']
        vector_data['vector_distal'] = vector_data['insertion'] - vector_data['midpoint']
        vector_data['n_segments'] = fiber_data['muscle_proximal'].bbone_segments
        vector_data['reach_proximal'] = (vector_data['midpoint'] - vector_data['origin']).magnitude
        vector_data['reach_distal'] = (vector_data['insertion'] - vector_data['midpoint']).magnitude

        vector_data['midpoint_axes'] = {}
        vector_data['midpoint_axes']['x'] = fiber_data['midpoint_insertion'].x_axis
        vector_data['midpoint_axes']['y'] = fiber_data['midpoint_insertion'].y_axis
        vector_data['midpoint_axes']['z'] = fiber_data['midpoint_insertion'].z_axis

        vector_data['midpoint_orientation'] = fiber_data['midpoint_insertion'].vector
        vector_data['midpoint_orientation'] /= vector_data['midpoint_orientation'].magnitude

    else:
        vector_data['n_segments'] = fiber_data['muscle'].bbone_segments

    return vector_data


def bones_within_fiber(armature_object, bone_from_fiber_rig__name):

    name_data = uncoil__bone_name(bone_from_fiber_rig__name)

    def is_within_fiber(bone):
        indiv_dat = uncoil__bone_name(bone.name)
        is_correct_side = indiv_dat['side'] == name_data['side']
        is_correct_name = indiv_dat['name'] == name_data['name']
        is_correct_n = indiv_dat['n'] == name_data['n']
        verdict = are_all_true(
            [is_correct_side, is_correct_name, is_correct_n])
        return verdict
    
    bones = list(filter(lambda bone: is_within_fiber(bone),
                        armature_object.data.edit_bones))

    fiber_type = fiber_rig_type(bones)
    
    bone_data = grip_fiber_bones(bones, fiber_type)

    bone_data['fiber_type'] = fiber_type

    if fiber_type == 'DOUBLE':
        bone_data['origin_parent'] = armature_object.data.edit_bones[
            bone_data['muscle_proximal']['origin_parent_name']]
        bone_data['insertion_parent'] = armature_object.data.edit_bones[
            bone_data['muscle_proximal']['insertion_parent_name']]
        bone_data['n_segments'] = bone_data['muscle_proximal'].bbone_segments
    else:
        bone_data['origin_parent'] = armature_object.data.edit_bones[
            bone_data['muscle']['origin_parent_name']]
        bone_data['insertion_parent'] = armature_object.data.edit_bones[
            bone_data['muscle']['insertion_parent_name']]
        bone_data['n_segments'] = bone_data['muscle'].bbone_segments

    
    return bone_data



def bones_within_muscle(armature_object, bone_from_fiber_rig__name):

    name_data = uncoil__bone_name(bone_from_fiber_rig__name)

    def is_within_muscle(bone):
        indiv_dat = uncoil__bone_name(bone.name)
        is_correct_side = indiv_dat['side'] == name_data['side']
        is_correct_name = indiv_dat['name'] == name_data['name']
        return are_all_true(
            [is_correct_side, is_correct_name])
        
    bones = list(filter(lambda bone: is_within_muscle(bone),
                        armature_object.data.edit_bones))

    fibers = list(set(map(lambda bone: number__bone_name(bone.name),
                          bones)))
    fibers.sort()

    muscle_data = []
    for i in fibers:
        local__name_data = name_data
        local__name_data['n'] = i
        local__name_data['sufs'] = []
        local__muscle_name = coil__bone_name(local__name_data)
        muscle_data.append(
            bones_within_fiber(armature_object, local__muscle_name))

    return muscle_data


def get_protofiber(armature_object, bone_from_fiber_rig__name):
    name_data = uncoil__bone_name(bone_from_fiber_rig__name)
    bone_data = {}
    if name_data['sufs'] == []:
        bone_data['position_marker'] = armature_object.data.edit_bones[bone_from_fiber_rig__name]
        name_data['sufs'] = ['insert']
        insertion_marker_name = coil__bone_name(name_data)
        bone_data['insertion_marker'] = armature_object.data.edit_bones[insertion_marker_name]
    else: # name_data['sufs'] == ['insert']:
        bone_data['insertion_marker'] = armature_object.data.edit_bones[bone_from_fiber_rig__name]
        name_data['sufs'] = []
        position_marker_name = coil__bone_name(name_data)
        bone_data['position_marker'] = armature_object.data.edit_bones[position_marker_name]
        
    return bone_data

def protofiber_relationship_data(protofiber_data):
    data = {}
    data['origin_parent'] = protofiber_data['position_marker'].parent
    data['insertion_parent'] = protofiber_data['insertion_marker'].parent
    return data


def delete_fiber(context):

    armature = context.active_object

    active_bone = context.active_bone

    bone_data = bones_within_fiber(armature, active_bone.name)
    bone_keys = fiber_type__sufss[bone_data['fiber_type']].keys()
    for key in bone_keys:
        prospect = bone_data[key]
        armature.data.edit_bones.remove(prospect)

    return bone_keys



def bone_vector_data(armature_obj, bone_name):
    bone = armature_obj.data.edit_bones[bone_name]

    data = {}

    data['vector'] = bone.vector
    data['head'] = bone.head
    data['tail'] = bone.tail
    data['length'] = data['vector'].magnitude
    data['magnitude'] = data['length']
    data['orientation'] = bone.y_axis
    data['x_axis'] = bone.x_axis
    data['y_axis'] = bone.y_axis
    data['z_axis'] = bone.z_axis

    return data



if __name__ == '__main__':
    context = bpy.context

    armature_object = context.active_object

    active_bone = context.active_bone

    muscle = bones_within_muscle(armature_object, active_bone.name)

    for fiber in muscle.keys():
        vdat = get_fiber_vector_data(muscle[fiber])
        print()
        print()
        print(fiber)
        print(muscle[fiber]['muscle'].name)
        print('head: ', muscle[fiber]['muscle'].head)

        print('origin pos: ', vdat['origin'])
        print('insertion pos: ', vdat['insertion'])
