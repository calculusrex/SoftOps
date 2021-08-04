import bpy
import functools as ft


import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)


from rename import uncoil__bone_name, coil__bone_name, suffix__bone_name, is_bone_name_of_muscle_rig
from get_bones import get_protofiber, protofiber_relationship_data, delete_fiber
from edit_bones import select_n_set_active__edit_bone
    

def muscle_c_fiber_from_active(context, bbone_segments):

    proto = context.active_bone
    armature_obj = context.active_object
    proto_dat = get_protofiber(armature_obj, proto.name)
    rel_dat = protofiber_relationship_data(proto_dat)
    armature_obj.data.edit_bones.remove(proto_dat['insertion_marker'])

    posmark = proto_dat['position_marker']
    select_n_set_active__edit_bone(armature_obj, posmark.name)
    
    
    origin_point = posmark.head.copy()
    insertion_point = posmark.tail.copy()

    general_orientation = insertion_point - origin_point
    general_orientation = general_orientation / general_orientation.magnitude

    z = posmark.z_axis

    control_bone_length = (origin_point - insertion_point).magnitude / 10

    muscle = posmark

    #######################
    # Origin Setup

    bpy.ops.armature.duplicate()
    origin = context.active_bone
    origin.name = suffix__bone_name(muscle.name, 'origin')
    origin.head = origin_point + (general_orientation * -1 * control_bone_length)
    origin.tail = origin_point
    origin.align_roll(z)

    bpy.ops.armature.duplicate()
    origin_tracker = context.active_bone
    origin_tracker.name = suffix__bone_name(muscle.name, 'origin_tracker')
    origin_tracker.head = origin_point
    origin_tracker.tail = origin_point + (general_orientation * control_bone_length)
    origin_tracker.align_roll(z)

    #######################
    # Insertion Setup

    bpy.ops.armature.duplicate()
    insertion = context.active_bone
    insertion.name = suffix__bone_name(muscle.name, 'insertion')
    insertion.head = insertion_point
    insertion.tail = insertion_point + (general_orientation * control_bone_length)
    insertion.align_roll(z)

    bpy.ops.armature.duplicate()
    insertion_tracker = context.active_bone
    insertion_tracker.name = suffix__bone_name(muscle.name, 'insertion_tracker')
    insertion_tracker.head = insertion_point
    insertion_tracker.tail = insertion_point + (general_orientation * -1 * control_bone_length)
    insertion_tracker.align_roll(z)

    bpy.ops.armature.duplicate()
    bend_target = context.active_bone
    bend_target.name = suffix__bone_name(muscle.name, 'bend_target')
    bend_target.head = (origin_point + insertion_point) / 2
    bend_target.tail = bend_target.head + (z * control_bone_length)
    bend_target.align_roll(muscle.y_axis)

    muscle.parent = origin
    origin.parent = origin_tracker
    insertion.parent = insertion_tracker

    origin_tracker.parent = rel_dat['origin_parent']
    insertion_tracker.parent = rel_dat['insertion_parent']

    bend_target.parent = rel_dat['origin_parent']

    muscle.bbone_segments = bbone_segments
    muscle.bbone_handle_type_start = 'ABSOLUTE'
    muscle.bbone_handle_type_end = 'ABSOLUTE'
    muscle.bbone_custom_handle_start = origin
    muscle.bbone_custom_handle_end = insertion

    muscle['origin_parent_name'] = rel_dat['origin_parent'].name
    muscle['insertion_parent_name'] = rel_dat['insertion_parent'].name

    ## Constraints

    bpy.ops.object.posemode_toggle()

    pose_muscle = context.active_object.pose.bones[muscle.name]
    pose_origin = context.active_object.pose.bones[origin.name]
    pose_origin_tracker = context.active_object.pose.bones[origin_tracker.name]
    pose_insertion = context.active_object.pose.bones[insertion.name]
    pose_insertion_tracker = context.active_object.pose.bones[insertion_tracker.name]
    pose_bend_target = context.active_object.pose.bones[bend_target.name]

    # Tracking Constraints

    origin_tracking_constraint = pose_origin_tracker.constraints.new('DAMPED_TRACK')
    origin_tracking_constraint.target = context.active_object
    origin_tracking_constraint.subtarget = pose_bend_target.name

    insertion_tracking_constraint = pose_insertion_tracker.constraints.new('DAMPED_TRACK')
    insertion_tracking_constraint.target = context.active_object
    insertion_tracking_constraint.subtarget = pose_bend_target.name

    # Stretch Constraints

    muscle_stretchTo_constraint = pose_muscle.constraints.new('STRETCH_TO')
    muscle_stretchTo_constraint.target = context.active_object
    muscle_stretchTo_constraint.subtarget = pose_insertion.name

    bpy.ops.object.editmode_toggle()
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.editmode_toggle()
    



def muscle_s_fiber_from_active(context, bbone_segments):

    proto = context.active_bone
    armature_obj = context.active_object
    proto_dat = get_protofiber(armature_obj, proto.name)
    rel_dat = protofiber_relationship_data(proto_dat)
    armature_obj.data.edit_bones.remove(proto_dat['insertion_marker'])

    posmark = proto_dat['position_marker']
    select_n_set_active__edit_bone(armature_obj, posmark.name)

    origin_point = posmark.head.copy()
    insertion_point = posmark.tail.copy()

    control_bone_length = (origin_point - insertion_point).magnitude / 10

    general_orientation = insertion_point - origin_point
    general_orientation = general_orientation / general_orientation.magnitude

    z = posmark.z_axis

    muscle = posmark

    ###########################
    # Origin Setup

    bpy.ops.armature.duplicate()
    origin = context.active_bone
    origin.name = suffix__bone_name(muscle.name, 'origin')
    origin.head = origin_point + (general_orientation * -1 * control_bone_length)
    origin.tail = origin_point
    origin.align_roll(z)

    bpy.ops.armature.duplicate()
    origin_tracker = context.active_bone
    origin_tracker.name = suffix__bone_name(muscle.name, 'origin_tracker')
    origin_tracker.head = origin_point
    origin_tracker.tail = origin_point + (general_orientation * control_bone_length)
    origin_tracker.align_roll(z)

    bpy.ops.armature.duplicate()
    origin_bend_target = context.active_bone
    origin_bend_target.name = suffix__bone_name(muscle.name, 'origin_bend_target')
    origin_bend_target.head = origin_point + ((insertion_point - origin_point) / 3)
    origin_bend_target.tail = origin_bend_target.head + (z * control_bone_length)
    origin_bend_target.align_roll(muscle.y_axis)

    ###########################
    # Insertion Setup

    bpy.ops.armature.duplicate()
    insertion = context.active_bone
    insertion.name = suffix__bone_name(muscle.name, 'insertion')
    insertion.head = insertion_point
    insertion.tail = insertion_point + (general_orientation * control_bone_length)
    insertion.align_roll(z)

    bpy.ops.armature.duplicate()
    insertion_tracker = context.active_bone
    insertion_tracker.name = suffix__bone_name(muscle.name, 'insertion_tracker')
    insertion_tracker.head = insertion_point
    insertion_tracker.tail = insertion_point + (general_orientation * -1 * control_bone_length)
    insertion_tracker.align_roll(z)

    bpy.ops.armature.duplicate()
    insertion_bend_target = context.active_bone
    insertion_bend_target.name = suffix__bone_name(muscle.name, 'insertion_bend_target')
    insertion_bend_target.head = insertion_point + ((origin_point - insertion_point) / 3)
    insertion_bend_target.tail = insertion_bend_target.head + (z * control_bone_length)
    insertion_bend_target.align_roll(muscle.y_axis)

    muscle.parent = origin
    origin.parent = origin_tracker
    insertion.parent = insertion_tracker

    origin_tracker.parent = rel_dat['origin_parent']
    insertion_tracker.parent = rel_dat['insertion_parent']

    origin_bend_target.parent = rel_dat['origin_parent']
    insertion_bend_target.parent = rel_dat['origin_parent']


    muscle.bbone_segments = bbone_segments
    muscle.bbone_handle_type_start = 'ABSOLUTE'
    muscle.bbone_handle_type_end = 'ABSOLUTE'
    muscle.bbone_custom_handle_start = origin
    muscle.bbone_custom_handle_end = insertion

    muscle['origin_parent_name'] = rel_dat['origin_parent'].name
    muscle['insertion_parent_name'] = rel_dat['insertion_parent'].name

    ## Constraints

    bpy.ops.object.posemode_toggle()
    
    pose_muscle = context.active_object.pose.bones[muscle.name]
    pose_origin = context.active_object.pose.bones[origin.name]
    pose_origin_tracker = context.active_object.pose.bones[origin_tracker.name]
    pose_insertion = context.active_object.pose.bones[insertion.name]
    pose_insertion_tracker = context.active_object.pose.bones[insertion_tracker.name]
    pose_origin_bend_target = context.active_object.pose.bones[origin_bend_target.name]
    pose_insertion_bend_target = context.active_object.pose.bones[insertion_bend_target.name]

    # Tracking Constraints

    origin_tracking_constraint = pose_origin_tracker.constraints.new('DAMPED_TRACK')
    origin_tracking_constraint.target = context.active_object
    origin_tracking_constraint.subtarget = pose_origin_bend_target.name

    insertion_tracking_constraint = pose_insertion_tracker.constraints.new('DAMPED_TRACK')
    insertion_tracking_constraint.target = context.active_object
    insertion_tracking_constraint.subtarget = pose_insertion_bend_target.name

    # Stretch Constraints

    muscle_stretchTo_constraint = pose_muscle.constraints.new('STRETCH_TO')
    muscle_stretchTo_constraint.target = context.active_object
    muscle_stretchTo_constraint.subtarget = pose_insertion.name

    bpy.ops.object.editmode_toggle()
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.editmode_toggle()


def muscle_double_fiber_from_active(context, bbone_segments):

    proto = context.active_bone
    armature_obj = context.active_object
    proto_dat = get_protofiber(armature_obj, proto.name)
    rel_dat = protofiber_relationship_data(proto_dat)
    armature_obj.data.edit_bones.remove(proto_dat['insertion_marker'])

    posmark = proto_dat['position_marker']
    select_n_set_active__edit_bone(armature_obj, posmark.name)
    
    origin_point = posmark.head.copy()
    insertion_point = posmark.tail.copy()
    middle_point = origin_point + ((insertion_point - origin_point) / 2)

    control_bone_length = (origin_point - insertion_point).magnitude / 10

    general_orientation = insertion_point - origin_point
    general_orientation = general_orientation / general_orientation.magnitude

    z = posmark.z_axis

    muscle = posmark
    muscle_name = muscle.name

    ##########################
    # Muscle Setup

    muscle_proximal = muscle

    bpy.ops.armature.duplicate()
    muscle_distal = context.active_bone

    muscle_proximal.name = suffix__bone_name(muscle_name, 'proximal')
    muscle_distal.name = suffix__bone_name(muscle_name, 'distal')

    muscle_proximal.tail = middle_point
    muscle_distal.head = middle_point
    
    muscle_proximal.align_roll(z)
    muscle_distal.align_roll(z)
    
    ##########################
    # Origin Setup
    
    bpy.ops.armature.duplicate()
    origin = context.active_bone
    origin.name = suffix__bone_name(muscle_name, 'origin')
    origin.head = origin_point + (general_orientation * -1 * control_bone_length)
    origin.tail = origin_point
    origin.align_roll(z)

    bpy.ops.armature.duplicate()
    origin_tracker = context.active_bone
    origin_tracker.name = suffix__bone_name(muscle_name, 'origin_tracker')
    origin_tracker.head = origin_point
    origin_tracker.tail = origin_point + (general_orientation * control_bone_length)
    origin_tracker.align_roll(z)

    bpy.ops.armature.duplicate()
    origin_bend_target = context.active_bone
    origin_bend_target.name = suffix__bone_name(muscle_name, 'origin_bend_target')
    origin_bend_target.head = origin_point + ((insertion_point - origin_point) / 4)
    origin_bend_target.tail = origin_bend_target.head + (z * control_bone_length)
    origin_bend_target.align_roll(muscle.y_axis)

    ##########################
    # Insertion Setup

    bpy.ops.armature.duplicate()
    insertion = context.active_bone
    insertion.name = suffix__bone_name(muscle_name, 'insertion')
    insertion.head = insertion_point
    insertion.tail = insertion_point + (general_orientation * control_bone_length)
    insertion.align_roll(z)

    bpy.ops.armature.duplicate()
    insertion_tracker = context.active_bone
    insertion_tracker.name = suffix__bone_name(muscle_name, 'insertion_tracker')
    insertion_tracker.head = insertion_point
    insertion_tracker.tail = insertion_point + (general_orientation * -1 * control_bone_length)
    insertion_tracker.align_roll(z)

    bpy.ops.armature.duplicate()
    insertion_bend_target = context.active_bone
    insertion_bend_target.name = suffix__bone_name(muscle_name, 'insertion_bend_target')
    insertion_bend_target.head = insertion_point + ((origin_point - insertion_point) / 4)
    insertion_bend_target.tail = insertion_bend_target.head + (z * control_bone_length)
    insertion_bend_target.align_roll(muscle.y_axis)

    ##########################
    # Midpoint Setup

    bpy.ops.armature.duplicate()
    midpoint_origin = context.active_bone
    midpoint_origin.name = suffix__bone_name(muscle_name, 'midpoint_origin')
    midpoint_origin.head = middle_point + (general_orientation * control_bone_length * -1)
    midpoint_origin.tail = middle_point
    midpoint_origin.align_roll(z)

    bpy.ops.armature.duplicate()
    midpoint_insertion = context.active_bone
    midpoint_insertion.name = suffix__bone_name(muscle_name, 'midpoint_insertion')
    midpoint_insertion.head = middle_point
    midpoint_insertion.tail = middle_point + (general_orientation * control_bone_length)
    midpoint_insertion.align_roll(z)
        

    muscle_proximal.parent = origin
    muscle_distal.parent = midpoint_origin
    origin.parent = origin_tracker
    insertion.parent = insertion_tracker
    midpoint_origin.parent = midpoint_insertion

    origin_tracker.parent = rel_dat['origin_parent']
    insertion_tracker.parent = rel_dat['insertion_parent']

    midpoint_insertion.parent = rel_dat['origin_parent']
    origin_bend_target.parent = rel_dat['origin_parent']
    insertion_bend_target.parent = rel_dat['origin_parent']

    muscle_proximal.bbone_segments = bbone_segments
    muscle_proximal.bbone_handle_type_start = 'ABSOLUTE'
    muscle_proximal.bbone_handle_type_end = 'ABSOLUTE'
    muscle_proximal.bbone_custom_handle_start = origin
    muscle_proximal.bbone_custom_handle_end = midpoint_insertion

    muscle_distal.bbone_segments = bbone_segments
    muscle_distal.bbone_handle_type_start = 'ABSOLUTE'
    muscle_distal.bbone_handle_type_end = 'ABSOLUTE'
    muscle_distal.bbone_custom_handle_start = midpoint_origin
    muscle_distal.bbone_custom_handle_end = insertion

    muscle_proximal['origin_parent_name'] = rel_dat['origin_parent'].name
    muscle_proximal['insertion_parent_name'] = rel_dat['insertion_parent'].name
    muscle_distal['origin_parent_name'] = rel_dat['origin_parent'].name
    muscle_distal['insertion_parent_name'] = rel_dat['insertion_parent'].name

    ## Constraints

    bpy.ops.object.posemode_toggle()
    
    pose_muscle_proximal = context.active_object.pose.bones[muscle_proximal.name]
    pose_muscle_distal = context.active_object.pose.bones[muscle_distal.name]
    pose_origin = context.active_object.pose.bones[origin.name]
    pose_origin_tracker = context.active_object.pose.bones[origin_tracker.name]
    pose_insertion = context.active_object.pose.bones[insertion.name]
    pose_insertion_tracker = context.active_object.pose.bones[insertion_tracker.name]
    pose_origin_bend_target = context.active_object.pose.bones[origin_bend_target.name]
    pose_insertion_bend_target = context.active_object.pose.bones[insertion_bend_target.name]
    pose_midpoint_origin = context.active_object.pose.bones[midpoint_origin.name]
    pose_midpoint_insertion = context.active_object.pose.bones[midpoint_insertion.name]

    # Tracking Constraints

    origin_tracking_constraint = pose_origin_tracker.constraints.new('DAMPED_TRACK')
    origin_tracking_constraint.target = context.active_object
    origin_tracking_constraint.subtarget = pose_origin_bend_target.name

    insertion_tracking_constraint = pose_insertion_tracker.constraints.new('DAMPED_TRACK')
    insertion_tracking_constraint.target = context.active_object
    insertion_tracking_constraint.subtarget = pose_insertion_bend_target.name

    # Stretch Constraints

    muscle_proximal_stretchTo_constraint = pose_muscle_proximal.constraints.new('STRETCH_TO')
    muscle_proximal_stretchTo_constraint.target = context.active_object
    muscle_proximal_stretchTo_constraint.subtarget = pose_midpoint_insertion.name

    muscle_distal_stretchTo_constraint = pose_muscle_distal.constraints.new('STRETCH_TO')
    muscle_distal_stretchTo_constraint.target = context.active_object
    muscle_distal_stretchTo_constraint.subtarget = pose_insertion.name

    bpy.ops.object.editmode_toggle()
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.editmode_toggle()

    

class MuscleCFiberfromActive(bpy.types.Operator):
    """Creates a muscle rig based on bendy bones from a selected bone."""
    bl_idname = "rigging.muscle_c_fiber_from_active"
    bl_label = "Muscle C Fiber From Active"
    bl_options = {'REGISTER', 'UNDO'}

    bbone_segments: bpy.props.IntProperty(name="BBone Segments", default=12, min=4, max=128)

    def execute(self, context):
        muscle_c_fiber_from_active(context, self.bbone_segments)

        return {'FINISHED'}


class MuscleSFiberfromActive(bpy.types.Operator):
    """Creates a muscle rig based on bendy bones from a selected bone (two tracking targets, one for the origin and one for the insertion)."""
    bl_idname = "rigging.muscle_s_fiber_from_active"
    bl_label = "Muscle S Fiber From Active"
    bl_options = {'REGISTER', 'UNDO'}

    bbone_segments: bpy.props.IntProperty(name="BBone Segments", default=12, min=4, max=128)

    def execute(self, context):
        muscle_s_fiber_from_active(context, self.bbone_segments)

        return {'FINISHED'}


class MuscleDoubleFiberfromActive(bpy.types.Operator):
    """Creates a muscle rig based on two bendy bones from the slected bone. With this double rig, you have control over the roll and orientation of the middle of the muscle, useful in long muscles which bend around structures."""
    bl_idname = "rigging.muscle_double_fiber_from_active"
    bl_label = "Muscle Double Fiber From Active"
    bl_options = {'REGISTER', 'UNDO'}

    bbone_segments: bpy.props.IntProperty(name="BBone Segments", default=12, min=4, max=128)

    def execute(self, context):
        muscle_double_fiber_from_active(context, self.bbone_segments)

        return {'FINISHED'}


class DeleteFiber(bpy.types.Operator):
    """Deletes all the bones that are associated with a fiber"""
    bl_idname = "rigging.delete_fiber"
    bl_label = "Delete Fiber"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        delete_fiber(context)
        return {'FINISHED'}



operator_data = []

operator_data.append({
    'class': MuscleCFiberfromActive,
    'keymap': 'J',
    'ctrl': True,
    'alt': True,
    'shift': False,
})

operator_data.append({
    'class': MuscleSFiberfromActive,
    'keymap': 'K',
    'ctrl': True,
    'alt': True,
    'shift': False,
})

operator_data.append({
    'class': MuscleDoubleFiberfromActive,
    'keymap': 'Y',
    'ctrl': True,
    'alt': True,
    'shift': False,
})

operator_data.append({
    'class': DeleteFiber,
    'keymap': 'X',
    'ctrl': True,
    'alt': True,
    'shift': False,
})
