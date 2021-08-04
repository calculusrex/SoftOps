import bpy


import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)

from get_bones import bone_vector_data
from rename import coil__bone_name, uncoil__bone_name, suffix__bone_name



def gimbal__install_bones(context):
    armature_obj = context.active_object
    subject_bone = context.active_bone
    vdat = bone_vector_data(armature_obj, subject_bone.name)
    bone_data = {}

    bpy.ops.armature.duplicate()
    z_rot_ref = context.active_bone
    z_rot_ref.name = suffix__bone_name(subject_bone.name, 'gimbal_zRotRef')
    z_rot_ref.tail = vdat['head'] + (0.25 * vdat['magnitude'] * -vdat['x_axis'])
    z_rot_ref.align_roll(-vdat['y_axis'])
    z_rot_ref.parent = subject_bone.parent
    bone_data['z_rot_ref'] = z_rot_ref

    twist_ref = z_rot_ref # same bone serves as refference for the twist
    bone_data['twist_ref'] = twist_ref

    bpy.ops.armature.duplicate()
    x_rot_ref = context.active_bone
    x_rot_ref.name = suffix__bone_name(subject_bone.name, 'gimbal_xRotRef')
    x_rot_ref.tail = vdat['head'] + (0.25 * vdat['magnitude'] * -vdat['z_axis'])
    x_rot_ref.align_roll(-vdat['y_axis'])
    x_rot_ref.parent = subject_bone.parent
    bone_data['x_rot_ref'] = x_rot_ref


    bpy.ops.armature.duplicate()
    x_rot_mark = context.active_bone
    x_rot_mark.name = suffix__bone_name(subject_bone.name, 'gimbal_xRotMark')
    x_rot_mark.tail = vdat['head'] + 0.1 * vdat['vector']
    x_rot_mark.align_roll(vdat['z_axis'])
    x_rot_mark.parent = subject_bone.parent
    bone_data['x_rot_mark'] = x_rot_mark


    bpy.ops.armature.duplicate()
    z_rot_mark = context.active_bone
    z_rot_mark.name = suffix__bone_name(subject_bone.name, 'gimbal_zRotMark')
    z_rot_mark.tail = vdat['head'] + 0.12 * vdat['vector']
    z_rot_mark.align_roll(vdat['z_axis'])
    z_rot_mark.parent = subject_bone.parent
    bone_data['z_rot_mark'] = z_rot_mark


    bpy.ops.armature.duplicate()
    twist_mark = context.active_bone
    twist_mark.name = suffix__bone_name(subject_bone.name, 'gimbal_twistMark')
    twist_mark.tail = vdat['head'] + (0.1 * vdat['magnitude'] * vdat['z_axis'])
    twist_mark.align_roll(-vdat['y_axis'])
    twist_mark.parent = subject_bone.parent
    bone_data['twist_mark'] = twist_mark

    
    return bone_data



if __name__ == '__main__':
    print('boom')

    gimbal__install_bones(bpy.context)
    
