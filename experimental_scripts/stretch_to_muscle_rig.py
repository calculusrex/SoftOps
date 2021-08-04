import bpy
import functools as ft


import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)

from rename import uncoil__bone_name, coil__bone_name, side__bone_name
from edit_bones import select_n_set_active__edit_bone


def deselect_all():
    bpy.ops.armature.select_all(action='DESELECT')

def is_selection_bilateral(context):
    return side__bone_name(context.active_bone.name) != None

def other_side(side):
    if side == 'L':
        return 'R'
    else:
        return 'L'

# muscle and insertion parent are bones
def install__stretch_to__target(armature, muscle, insertion_parent):

    insertion_name_data = uncoil__bone_name(muscle.name)
    insertion_name_data['pres'] = ['MCH']
    insertion_name_data['sufs'] = ['insertion']
    insertion_name = coil__bone_name(insertion_name_data)
    
    insertion = armature.edit_bones.new(insertion_name)

    insertion.head = muscle.tail
    insertion.tail = muscle.tail + (insertion_parent.vector / 10)
    insertion.align_roll(insertion_parent.z_axis)
    insertion.parent = insertion_parent
    return insertion


def active_side_selected_bone_pair(active_bone, selected_bones):
    active_side = side__bone_name(context.active_bone.name)

    muscle = context.active_bone

    active_muscle_name_data = uncoil__bone_name(context.active_bone.name)

    insertion_parent = list(
        filter(lambda b: uncoil__bone_name(b.name)['name'] != active_muscle_name_data['name'] and uncoil__bone_name(b.name)['side'] == active_side,
               selected_bones))[0]

    return muscle, insertion_parent


def inactive_side_selected_bone_pair(active_bone, selected_bones):
    active_side = side__bone_name(context.active_bone.name)
    inactive_side = other_side(active_side)

    active_muscle_name_data = uncoil__bone_name(context.active_bone.name)

    muscle = list(
        filter(lambda b: uncoil__bone_name(b.name)['name'] == active_muscle_name_data['name'] and uncoil__bone_name(b.name)['side'] == inactive_side,
               selected_bones))[0]

    insertion_parent = list(
        filter(lambda b: uncoil__bone_name(b.name)['name'] != active_muscle_name_data['name'] and uncoil__bone_name(b.name)['side'] == inactive_side,
               selected_bones))[0]

    return muscle, insertion_parent


def install__stretch_to__targets(armature, active_bone, selected_bones):

    active_muscle, active_insertion_parent = active_side_selected_bone_pair(
        active_bone, selected_bones)

    inactive_muscle, inactive_insertion_parent = inactive_side_selected_bone_pair(
        active_bone, selected_bones)

    active_insertion_target = install__stretch_to__target(
        armature, active_muscle, active_insertion_parent)

    inactive_insertion_target = install__stretch_to__target(
        armature, inactive_muscle, inactive_insertion_parent)

    return active_insertion_target, inactive_insertion_target


def stretch_to_rig__from_active(context):

    armature = context.active_object.data

    selected_bones = context.selected_bones
    active_bone = context.active_bone

    active_muscle, active_insertion_parent = active_side_selected_bone_pair(
        active_bone, selected_bones)

    inactive_muscle, inactive_insertion_parent = inactive_side_selected_bone_pair(
        active_bone, selected_bones)

    active_insertion_target, inactive_insertion_target = install__stretch_to__targets(
        armature, active_bone, selected_bones)

    bpy.ops.object.posemode_toggle()

    pose_active_muscle = context.active_object.pose.bones[active_muscle.name]
    pose_inactive_muscle = context.active_object.pose.bones[inactive_muscle.name]

    active_muscle_stretchTo_constraint = pose_active_muscle.constraints.new('STRETCH_TO')
    active_muscle_stretchTo_constraint.target = context.active_object
    active_muscle_stretchTo_constraint.subtarget = active_insertion_target.name

    inactive_muscle_stretchTo_constraint = pose_inactive_muscle.constraints.new('STRETCH_TO')
    inactive_muscle_stretchTo_constraint.target = context.active_object
    inactive_muscle_stretchTo_constraint.subtarget = inactive_insertion_target.name

    bpy.ops.object.editmode_toggle()


class StretchToRigFromActive(bpy.types.Operator):
    """Installs and sets up a stretch to constraint rig on active from selected"""
    bl_idname = "rigging.stretch_to_rig_from_active"
    bl_label = "Stretch To Rig From Active"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        stretch_to_rig__from_active(context)

        return {'FINISHED'}



keyless_op_data = []

keyless_op_data.append({
    'class': StretchToRigFromActive,
})
    


if __name__ == '__main__':
    print()
    
    context = bpy.context

    stretch_to_rig(context)
    
