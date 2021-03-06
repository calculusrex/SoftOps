import bpy
from mathutils import Vector

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)

from rename import other_side, uncoil__bone_name, coil__bone_name



def find_muscle_insertion_target(context, armature, muscle):
    return list(
        filter(lambda b: b.head == muscle.tail and uncoil__bone_name(b.name)['sufs'] == ['insertion'],
               context.object.data.edit_bones))[0]


def install__spanner__active_side(context, armature):
    active_muscle = context.active_bone
    selected_bones = context.selected_bones

    muscle_name__without_side = active_muscle.name.split('.')[0]
    active_side = active_muscle.name.split('.')[1]

    if len(selected_bones) % 2 == 0:
        active_spanner_locator = list(
            filter(lambda b: b.name.split('.')[0] != muscle_name__without_side and b.name.split('.')[1] == active_side,
                   selected_bones)
        )[0]
    else:
        active_spanner_locator = list(
            filter(lambda b: b.name.split('.')[0] != muscle_name__without_side,
                   selected_bones)
        )[0]

    active_spanner_name_data = uncoil__bone_name(active_muscle.name)
    active_spanner_name_data['sufs'] = ['spanner']
    active_spanner_name_data['pres'] = ['MCH']
    active_spanner_name = coil__bone_name(active_spanner_name_data)

    active_spanner = armature.data.edit_bones.new(name=active_spanner_name)
    active_spanner.head = active_spanner_locator.head + active_spanner_locator.vector / 2
    active_spanner.tail = active_muscle.head + active_muscle.vector / 2

    return active_spanner, active_spanner_locator, active_muscle

def install__spanner__inactive_side(context, armature):
    active_muscle = context.active_bone
    selected_bones = context.selected_bones

    muscle_name__without_side = active_muscle.name.split('.')[0]
    active_side = active_muscle.name.split('.')[1]
    inactive_side = other_side(active_side)

    inactive_muscle = list(
        filter(lambda b: b.name.split('.')[0] == muscle_name__without_side and b.name.split('.')[1] == inactive_side,
               selected_bones)
    )[0]

    if len(selected_bones) % 2 == 0:
        inactive_spanner_locator = list(
            filter(lambda b: b.name.split('.')[0] != muscle_name__without_side and b.name.split('.')[1] == inactive_side,
                   selected_bones)
        )[0]
    else:
        inactive_spanner_locator = list(
            filter(lambda b: b.name.split('.')[0] != muscle_name__without_side,
                   selected_bones)
        )[0]

    inactive_spanner_name_data = uncoil__bone_name(inactive_muscle.name)
    inactive_spanner_name_data['sufs'] = ['spanner']
    inactive_spanner_name_data['pres'] = ['MCH']
    inactive_spanner_name = coil__bone_name(inactive_spanner_name_data)

    inactive_spanner = armature.data.edit_bones.new(name=inactive_spanner_name)
    inactive_spanner.head = inactive_spanner_locator.head + inactive_spanner_locator.vector / 2
    inactive_spanner.tail = inactive_muscle.head + inactive_muscle.vector / 2

    return inactive_spanner, inactive_spanner_locator, inactive_muscle


def install__spanner_rig(context, armature, active_muscle, selected_bones):

    active_spanner, active_spanner_locator, active_muscle = install__spanner__active_side(
        context, armature)
    inactive_spanner, inactive_spanner_locator, inactive_muscle = install__spanner__inactive_side(
        context, armature)

    active_side = active_muscle.name.split('.')[1]
    
    active_spanner.align_roll(-active_muscle.x_axis)
    inactive_spanner.align_roll(inactive_muscle.x_axis)

    active_insertion_bone = find_muscle_insertion_target(context, armature, active_muscle)
    inactive_insertion_bone = find_muscle_insertion_target(context, armature, inactive_muscle)

    if active_spanner_locator == inactive_spanner_locator:
        spanner_parent_name_data = uncoil__bone_name(active_muscle.name)
        spanner_parent_name_data['pres'] = ['MCH']
        spanner_parent_name_data['sufs'] = ['spannerParent']
        spanner_parent_name_data['side'] = None
        spanner_parent_name = coil__bone_name(spanner_parent_name_data)
        spanner_parent = armature.data.edit_bones.new(
            name=spanner_parent_name)

        spanner_parent.head = active_spanner.head
        spanner_parent.tail = active_spanner.head + active_insertion_bone.vector / 4
        spanner_parent.align_roll(active_insertion_bone.z_axis)

        active_spanner_parent = spanner_parent
        inactive_spanner_parent = spanner_parent

        active_spanner.parent = active_spanner_parent
        inactive_spanner.parent = inactive_spanner_parent

        spanner_parent.parent = active_spanner_locator
        active_spanner_parent = spanner_parent
        inactive_spanner_parent = spanner_parent
        
    else:
        spanner_parent_name_data = uncoil__bone_name(active_muscle.name)
        spanner_parent_name_data['pres'] = ['MCH']
        spanner_parent_name_data['sufs'] = ['spannerParent']

        spanner_parent_name_data['side'] = active_side
        active_spanner_parent_name = coil__bone_name(spanner_parent_name_data)
        active_spanner_parent = armature.data.edit_bones.new(
            name=active_spanner_parent_name)

        spanner_parent_name_data['side'] = other_side(active_side)
        inactive_spanner_parent_name = coil__bone_name(spanner_parent_name_data)
        inactive_spanner_parent = armature.data.edit_bones.new(
            name=inactive_spanner_parent_name)

        active_spanner_parent.head = active_spanner.head
        active_spanner_parent.tail = active_spanner.head + active_insertion_bone.vector / 4
        active_spanner_parent.align_roll(active_insertion_bone.z_axis)

        inactive_spanner_parent.head = inactive_spanner.head
        inactive_spanner_parent.tail = inactive_spanner.head + inactive_insertion_bone.vector / 4
        inactive_spanner_parent.align_roll(inactive_insertion_bone.z_axis)

        active_spanner.parent = active_spanner_parent
        inactive_spanner.parent = inactive_spanner_parent

        active_spanner_parent.parent = active_spanner_locator
        inactive_spanner_parent.parent = inactive_spanner_locator
        

    ## Names:
    name = {}
    name['active_muscle'] = active_muscle.name
    name['active_spanner'] = active_spanner.name
    name['active_spanner_locator'] = active_spanner_locator.name
    name['active_insertion_bone'] = active_insertion_bone.name
    name['active_spanner_parent'] = active_spanner_parent.name

    name['inactive_muscle'] = inactive_muscle.name
    name['inactive_spanner'] = inactive_spanner.name
    name['inactive_spanner_locator'] = inactive_spanner_locator.name
    name['inactive_insertion_bone'] = inactive_insertion_bone.name
    name['inactive_spanner_parent'] = inactive_spanner_parent.name

    bpy.ops.object.posemode_toggle()

    pose_active_spanner_parent = context.object.pose.bones[name['active_spanner_parent']]
    pose_inactive_spanner_parent = context.object.pose.bones[name['inactive_spanner_parent']]

    pose_active_insertion_bone = context.object.pose.bones[name['active_insertion_bone']]
    pose_inactive_insertion_bone = context.object.pose.bones[name['inactive_insertion_bone']]

    active_spanner_parent_copyRotation_constraint = pose_active_spanner_parent.constraints.new('COPY_ROTATION')
    active_spanner_parent_copyRotation_constraint.target = context.active_object
    active_spanner_parent_copyRotation_constraint.subtarget = name['active_insertion_bone']
    active_spanner_parent_copyRotation_constraint.influence = 0.5


    pose_inactive_spanner_parent = context.object.pose.bones[name['inactive_spanner_parent']]
    pose_inactive_spanner_parent = context.object.pose.bones[name['inactive_spanner_parent']]

    pose_inactive_insertion_bone = context.object.pose.bones[name['inactive_insertion_bone']]
    pose_inactive_insertion_bone = context.object.pose.bones[name['inactive_insertion_bone']]

    inactive_spanner_parent_copyRotation_constraint = pose_inactive_spanner_parent.constraints.new('COPY_ROTATION')
    inactive_spanner_parent_copyRotation_constraint.target = context.active_object
    inactive_spanner_parent_copyRotation_constraint.subtarget = name['inactive_insertion_bone']
    inactive_spanner_parent_copyRotation_constraint.influence = 0.5

    
    bpy.ops.object.editmode_toggle()

    edit_bones = {}
    edit_bones['active_muscle'] = name['active_muscle']
    edit_bones['active_spanner'] = name['active_spanner']
    edit_bones['active_spanner_locator'] = name['active_spanner_locator']
    edit_bones['active_insertion_bone'] = name['active_insertion_bone']
    edit_bones['active_spanner_parent'] = name['active_spanner_parent']

    edit_bones['inactive_muscle'] = name['inactive_muscle']
    edit_bones['inactive_spanner'] = name['inactive_spanner']
    edit_bones['inactive_spanner_locator'] = name['inactive_spanner_locator']
    edit_bones['inactive_insertion_bone'] = name['inactive_insertion_bone']
    edit_bones['inactive_spanner_parent'] = name['inactive_spanner_parent']

    return edit_bones


def install_bbone_handles_and_handle_parents(context, armature, muscle_name):
    muscle = armature.data.edit_bones[muscle_name]
    
    name_data = uncoil__bone_name(muscle.name)
    name_data['pres'] = ['MCH']

    origin_parent = muscle.parent
    insertion_parent = find_muscle_insertion_target(context, armature, muscle)

    name_data['sufs'] = ['originBendTracker']
    origin_tracker = armature.data.edit_bones.new(
        coil__bone_name(name_data))
    origin_tracker.head = muscle.head
    origin_tracker.tail = muscle.head + muscle.vector/10
    origin_tracker.parent = origin_parent
    origin_tracker.align_roll(muscle.z_axis)

    name_data['sufs'] = ['originHandle']
    origin_handle = armature.data.edit_bones.new(
        coil__bone_name(name_data))
    origin_handle.head = muscle.head - muscle.vector/10
    origin_handle.tail = muscle.head
    origin_handle.parent = origin_tracker
    origin_handle.align_roll(muscle.z_axis)

    name_data['sufs'] = ['insertionBendTracker']
    insertion_tracker = armature.data.edit_bones.new(
        coil__bone_name(name_data))
    insertion_tracker.head = muscle.tail
    insertion_tracker.tail = muscle.tail - muscle.vector/10
    insertion_tracker.parent = insertion_parent
    insertion_tracker.align_roll(muscle.z_axis)

    name_data['sufs'] = ['insertionHandle']
    insertion_handle = armature.data.edit_bones.new(
        coil__bone_name(name_data))
    insertion_handle.head = muscle.tail
    insertion_handle.tail = muscle.tail + muscle.vector/10
    insertion_handle.parent = insertion_tracker
    insertion_handle.align_roll(muscle.z_axis)

    name_data['sufs'] = ['bendTarget']
    bend_target = armature.data.edit_bones.new(
        coil__bone_name(name_data))
    bend_target.head = muscle.head + muscle.vector/2
    bend_target.tail = muscle.head + muscle.vector/2 + muscle.z_axis * (muscle.vector/10).magnitude
    bend_target.parent = muscle.parent
    bend_target.align_roll(muscle.y_axis)

    bone_nomenclature = {
        'muscle': muscle.name,
        'originHandle': origin_handle.name, 'originBendTracker': origin_tracker.name,
        'insertionHandle': insertion_handle.name, 'insertionBendTracker': insertion_tracker.name,
        'bendTarget': bend_target.name
    }
    
    return bone_nomenclature


def bbone_rig(context, armature, muscle_name, bbone_segment_n):
    bbone_mechanical_nomenclature = install_bbone_handles_and_handle_parents(
        context, armature, muscle_name)

    muscle = armature.data.edit_bones[
        bbone_mechanical_nomenclature['muscle']]
    muscle.bbone_segments = bbone_segment_n
    muscle.bbone_handle_type_start = 'ABSOLUTE'
    muscle.bbone_handle_type_end = 'ABSOLUTE'
    muscle.bbone_custom_handle_start = armature.data.edit_bones[
        bbone_mechanical_nomenclature['originHandle']]
    muscle.bbone_custom_handle_end = armature.data.edit_bones[
        bbone_mechanical_nomenclature['insertionHandle']]

    bpy.ops.object.posemode_toggle()

    origin_bend_target = armature.pose.bones[
        bbone_mechanical_nomenclature['originBendTracker']]
    
    insertion_bend_target = armature.pose.bones[
        bbone_mechanical_nomenclature['insertionBendTracker']]

    muscle = armature.pose.bones[
        bbone_mechanical_nomenclature['muscle']]
    
    origin_damped_track = origin_bend_target.constraints.new('DAMPED_TRACK')
    origin_damped_track.target = armature
    origin_damped_track.subtarget = bbone_mechanical_nomenclature['bendTarget']

    insertion_damped_track = insertion_bend_target.constraints.new('DAMPED_TRACK')
    insertion_damped_track.target = armature
    insertion_damped_track.subtarget = bbone_mechanical_nomenclature['bendTarget']
    
    bpy.ops.object.editmode_toggle()

    return bbone_mechanical_nomenclature
    
    

def bbone__from_stretchTo(context, bbone_segment_n):
    
    armature = context.object

    active_muscle = context.active_bone
    selected_bones = context.selected_bones

    spanner_rig_bone_nomenclature = install__spanner_rig(
        context, armature, active_muscle, selected_bones)
    active_spanner = armature.data.edit_bones[
        spanner_rig_bone_nomenclature['active_spanner']]
    inactive_spanner = armature.data.edit_bones[
        spanner_rig_bone_nomenclature['inactive_spanner']]

    active_bbone_mechanical_nomenclature = bbone_rig(
        context, armature,
        spanner_rig_bone_nomenclature['active_muscle'], bbone_segment_n)
    active_bend_target = armature.data.edit_bones[
        active_bbone_mechanical_nomenclature['bendTarget']]

    inactive_bbone_mechanical_nomenclature = bbone_rig(
        context, armature,
        spanner_rig_bone_nomenclature['inactive_muscle'], bbone_segment_n)
    inactive_bend_target = armature.data.edit_bones[
        inactive_bbone_mechanical_nomenclature['bendTarget']]

    active_bend_target.parent = active_spanner
    inactive_bend_target.parent = inactive_spanner

    return (
        spanner_rig_bone_nomenclature,
        active_bbone_mechanical_nomenclature,
        inactive_bbone_mechanical_nomenclature,
    )
    

if __name__ == '__main__':
    print('bbone__from_stretchTo.py')

    context = bpy.context

    bbone__from_stretchTo(context, 6)

    # armature = context.object

    # muscle = context.active_bone

    # bbone_mechanicals = install_bbone_handles_and_handle_parents(context, armature, muscle)

    # for key in bbone_mechanicals.keys():
    #     print(key, bbone_mechanicals[key])
