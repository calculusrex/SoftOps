import bpy
from mathutils import Vector

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)

from rename import other_side, uncoil__bone_name, coil__bone_name


def fetch_bone_names__from_stretchTo(context):
    active_bone_name = context.active_bone.name
    selected_bone_name = list(
        filter(lambda name: name != active_bone_name,
               map(lambda b: b.name,
                   context.selected_bones)))[0]
    insertion_bone_name_data = uncoil__bone_name(active_bone_name)
    insertion_bone_name_data['pres'] = ['MCH']
    insertion_bone_name_data['sufs'] = ['insertion']
    insertion_bone_name = coil__bone_name(insertion_bone_name_data)
    return {
        'muscle': active_bone_name,
        'bend_target_parent': selected_bone_name,
        'insertion': insertion_bone_name
    }


def install_trackers(context, nomenclature):
    muscle = context.object.data.edit_bones[nomenclature['muscle']]
    insertion = context.object.data.edit_bones[nomenclature['insertion']]

    origin_tracker_name_data = uncoil__bone_name(muscle.name)
    origin_tracker_name_data['pres'] = ['MCH']
    origin_tracker_name_data['sufs'] = ['originTracker']
    origin_tracker_name = coil__bone_name(origin_tracker_name_data)
    origin_tracker = context.object.data.edit_bones.new(name=origin_tracker_name)
    origin_tracker.head = muscle.head
    origin_tracker.tail = muscle.head + muscle.vector/10
    origin_tracker.align_roll(muscle.z_axis)
    origin_tracker.parent = muscle.parent
    nomenclature['originTracker'] = origin_tracker.name

    insertion_tracker_name_data = uncoil__bone_name(muscle.name)
    insertion_tracker_name_data['pres'] = ['MCH']
    insertion_tracker_name_data['sufs'] = ['insertionTracker']
    insertion_tracker_name = coil__bone_name(insertion_tracker_name_data)
    insertion_tracker = context.object.data.edit_bones.new(name=insertion_tracker_name)
    insertion_tracker.head = muscle.tail
    insertion_tracker.tail = muscle.tail - muscle.vector/10
    insertion_tracker.align_roll(muscle.z_axis)
    insertion_tracker.parent = insertion
    nomenclature['insertionTracker'] = insertion_tracker.name

    return nomenclature

def install_handles(context, nomenclature):
    muscle = context.object.data.edit_bones[nomenclature['muscle']]

    origin_handle_name_data = uncoil__bone_name(muscle.name)
    origin_handle_name_data['pres'] = ['MCH']
    origin_handle_name_data['sufs'] = ['originHandle']
    origin_handle_name = coil__bone_name(origin_handle_name_data)
    origin_handle = context.object.data.edit_bones.new(name=origin_handle_name)
    origin_handle.head = muscle.head - muscle.vector/10
    origin_handle.tail = muscle.head
    origin_handle.align_roll(muscle.z_axis)
    origin_handle.parent = context.object.data.edit_bones[
        nomenclature['originTracker']]
    nomenclature['originHandle'] = origin_handle.name

    insertion_handle_name_data = uncoil__bone_name(muscle.name)
    insertion_handle_name_data['pres'] = ['MCH']
    insertion_handle_name_data['sufs'] = ['insertionHandle']
    insertion_handle_name = coil__bone_name(insertion_handle_name_data)
    insertion_handle = context.object.data.edit_bones.new(name=insertion_handle_name)
    insertion_handle.head = muscle.tail
    insertion_handle.tail = muscle.tail + muscle.vector/10
    insertion_handle.align_roll(muscle.z_axis)
    insertion_handle.parent = context.object.data.edit_bones[
        nomenclature['insertionTracker']]
    nomenclature['insertionHandle'] = insertion_handle.name

    muscle.parent = origin_handle
    
    return nomenclature

def install_bend_target(context, nomenclature):
    muscle = context.object.data.edit_bones[nomenclature['muscle']]
    bend_target_parent = context.object.data.edit_bones[nomenclature['bend_target_parent']]

    bend_target_name_data = uncoil__bone_name(muscle.name)
    bend_target_name_data['pres'] = ['MCH']
    bend_target_name_data['sufs'] = ['bendTarget']
    bend_target_name = coil__bone_name(bend_target_name_data)
    bend_target = context.object.data.edit_bones.new(name=bend_target_name)
    bend_target.head = muscle.head + muscle.vector/2
    bend_target.tail = muscle.head+muscle.vector/2 + muscle.z_axis*muscle.vector.magnitude/10
    bend_target.align_roll(-muscle.y_axis)
    bend_target.parent = context.object.data.edit_bones[
        nomenclature['bend_target_parent']]
    nomenclature['bendTarget'] = bend_target.name
    
    return nomenclature

def install_bbone(context, nomenclature, n_segments):
    nomenclature = install_trackers(context, nomenclature)
    nomenclature = install_handles(context, nomenclature)
    nomenclature = install_bend_target(context, nomenclature)
    
    muscle = context.object.data.edit_bones[nomenclature['muscle']]
    muscle.bbone_segments = n_segments
    muscle.bbone_handle_type_start = 'ABSOLUTE'
    muscle.bbone_handle_type_end = 'ABSOLUTE'
    muscle.bbone_custom_handle_start = context.object.data.edit_bones[
        nomenclature['originHandle']]
    muscle.bbone_custom_handle_end = context.object.data.edit_bones[
        nomenclature['insertionHandle']]
    
    return nomenclature

    
def rig_bbone(context, nomenclature):
    bpy.ops.object.posemode_toggle()

    muscle = context.object.pose.bones[nomenclature['muscle']]
    stretch_to_constraint = muscle.constraints['Stretch To']
    stretch_to_constraint.subtarget = nomenclature['insertionHandle']

    origin_tracker = context.object.pose.bones[nomenclature['originTracker']]
    origin_tracker_damped_track = origin_tracker.constraints.new('DAMPED_TRACK')
    origin_tracker_damped_track.target = context.object
    origin_tracker_damped_track.subtarget = nomenclature['bendTarget']

    insertion_tracker = context.object.pose.bones[nomenclature['insertionTracker']]
    insertion_tracker_damped_track = insertion_tracker.constraints.new('DAMPED_TRACK')
    insertion_tracker_damped_track.target = context.object
    insertion_tracker_damped_track.subtarget = nomenclature['bendTarget']
    
    bpy.ops.object.editmode_toggle()


def bbone__from_stretchTo(context, n_segments):
    bpy.context.object.data.use_mirror_x = False

    nomenclature = fetch_bone_names__from_stretchTo(context)
    nomenclature = install_bbone(context, nomenclature, n_segments)
    rig_bbone(context, nomenclature)

    bpy.context.object.data.use_mirror_x = True

    return nomenclature


####################################################################################
## Adjust

def generate_nomenclature(context):
    name_data = uncoil__bone_name(context.active_bone.name)
    nomenclature = {}

    name_data['pres'] = ['DEF']
    name_data['sufs'] = []
    nomenclature['muscle'] = coil__bone_name(name_data)

    name_data['pres'] = ['MCH']
    name_data['sufs'] = ['insertion']
    nomenclature['insertion'] = coil__bone_name(name_data)

    name_data['pres'] = ['MCH']
    name_data['sufs'] = ['originTracker']
    nomenclature['originTracker'] = coil__bone_name(name_data)

    name_data['pres'] = ['MCH']
    name_data['sufs'] = ['insertionTracker']
    nomenclature['insertionTracker'] = coil__bone_name(name_data)

    name_data['pres'] = ['MCH']
    name_data['sufs'] = ['originHandle']
    nomenclature['originHandle'] = coil__bone_name(name_data)

    name_data['pres'] = ['MCH']
    name_data['sufs'] = ['insertionHandle']
    nomenclature['insertionHandle'] = coil__bone_name(name_data)

    name_data['pres'] = ['MCH']
    name_data['sufs'] = ['bendTarget']
    nomenclature['bendTarget'] = coil__bone_name(name_data)

    return nomenclature


def adjust_bone_direction(context, bone_name, head_pivoting, towards_target, nomenclature):
    muscle = context.object.data.edit_bones[nomenclature['muscle']]
    
    bend_target = context.object.data.edit_bones[nomenclature['bendTarget']]
    target_position = bend_target.head

    bone = context.object.data.edit_bones[bone_name]

    if head_pivoting:
        direction_vector = target_position - bone.head
        direction_vector = direction_vector / direction_vector.magnitude
        direction_vector = direction_vector * bone.vector.magnitude
        if towards_target:
            bone.tail = bone.head + direction_vector
        else:
            bone.tail = bone.head - direction_vector
    else:
        direction_vector = target_position - bone.tail
        direction_vector = direction_vector / direction_vector.magnitude
        direction_vector = direction_vector * bone.vector.magnitude
        if towards_target:
            bone.head = bone.tail - direction_vector
        else:
            bone.head = bone.tail + direction_vector

    bone.align_roll(muscle.z_axis)
        


def adjust_trackers(context, nomenclature):
    muscle = context.object.data.edit_bones[nomenclature['muscle']]

    adjust_bone_direction(
        context, nomenclature['originTracker'],
        True, True,
        nomenclature)

    adjust_bone_direction(
        context, nomenclature['insertionTracker'],
        True, True,
        nomenclature)

    adjust_bone_direction(
        context, nomenclature['originHandle'],
        False, True,
        nomenclature)

    adjust_bone_direction(
        context, nomenclature['insertionHandle'],
        True, False,
        nomenclature)

    
def adjust_bbone_rig(context):
    bpy.context.object.data.use_mirror_x = False

    nomenclature = generate_nomenclature(context)
    adjust_trackers(context, nomenclature)

    bpy.context.object.data.use_mirror_x = True



class BBoneFromStretchTo(bpy.types.Operator):
    """
    Create a bbone rig from a simple stretch-to rig.
    select the main limb bone the muscle runs parallel to and then the muscle bone as active.
    the active bone will be transformed into a bbone, the selected will be the parent of the
    bend target.
    """
    bl_idname = "rigging.bbone_from_stretch_to"
    bl_label = "BBone From Stretch To"
    bl_options = {'REGISTER', 'UNDO'}

    bbone_segments: bpy.props.IntProperty(name="BBone Segments", default=6, min=4, max=128)

    def execute(self, context):
        bbone__from_stretchTo(context, self.bbone_segments)

        return {'FINISHED'}    


class AdjustBBoneRig(bpy.types.Operator):
    """Adjusts direction of the muscle bbone rig's mechanism bones after the bend target"""
    bl_idname = "rigging.adjust_bbone_rig"
    bl_label = "Adjust BBone Rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        adjust_bbone_rig(context)

        return {'FINISHED'}


keyless_op_data = []

keyless_op_data.append({
    'class': AdjustBBoneRig,
})

keyless_op_data.append({
    'class': BBoneFromStretchTo,
})





if __name__ == '__main__':
    print('bbone__from_stretchTo.py')

    context = bpy.context

    bbone__from_stretchTo(context, 6)

    # adjust_bbone_rig(context)
