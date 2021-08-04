import bpy
import functools as ft
from mathutils import Vector

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)

from get_bones import bones_within_fiber, get_fiber_vector_data



def displace_bone(bone, vector):
    bone.head += vector
    bone.tail += vector


def align_bone(bone, vector, adjust_tail):
    if adjust_tail:
        bone_vector = bone.tail - bone.head
        align_vector = (vector / vector.magnitude) * bone_vector.magnitude
        offset = align_vector - bone_vector
        bone.tail += offset

    else:
        bone_vector = bone.tail - bone.head
        align_vector = (vector / vector.magnitude) * bone_vector.magnitude
        offset = (align_vector - bone_vector) * -1
        bone.head += offset


def adjust_fiber(context):

    armature = context.active_object

    active_bone = context.active_bone
    
    fdat = bones_within_fiber(armature, active_bone.name)

    vdat = get_fiber_vector_data(fdat)

    if fdat['type'] == 'C':
        bend_target_point = fdat['bend_target'].head

        origin_orientation = bend_target_point - vdat['origin']
        origin_tracker_orientation = origin_orientation

        insertion_orientation = vdat['insertion'] - bend_target_point
        insertion_tracker_orientation = - insertion_orientation

    else:
        origin_bend_target_point = fdat['origin_bend_target'].head
        insertion_bend_target_point = fdat['insertion_bend_target'].head

        origin_orientation = origin_bend_target_point - vdat['origin']
        origin_tracker_orientation = origin_orientation

        insertion_orientation = vdat['insertion'] - insertion_bend_target_point
        insertion_tracker_orientation = - insertion_orientation

    insertion_z_axis = vdat['insertion_axes']['z']

    if fdat['type'] == 'DOUBLE':
        midpoint_orientation = vdat['midpoint_orientation']
        midpoint_displacement_vector = fdat['midpoint_insertion'].head - fdat['midpoint_origin'].tail

    
    align_bone(fdat['origin'], origin_orientation, False)
    fdat['origin'].align_roll(
        vdat['origin_axes']['z'])

    align_bone(fdat['origin_tracker'], origin_tracker_orientation, True)
    fdat['origin_tracker'].align_roll(
        vdat['origin_axes']['z'])

    align_bone(fdat['insertion'], insertion_orientation, True)
    fdat['insertion'].align_roll(
        insertion_z_axis)

    align_bone(fdat['insertion_tracker'], insertion_tracker_orientation, True)
    fdat['insertion_tracker'].align_roll(
        insertion_z_axis)

    if fdat['type'] == 'DOUBLE':

        align_bone(fdat['midpoint_origin'], midpoint_orientation, False)
        displace_bone(fdat['midpoint_origin'], midpoint_displacement_vector)
        fdat['midpoint_origin'].align_roll(
            fdat['midpoint_insertion'].z_axis)

        fdat['muscle_proximal'].tail += midpoint_displacement_vector
        fdat['muscle_distal'].head += midpoint_displacement_vector

        fdat['muscle_proximal'].align_roll(
            fdat['origin'].z_axis)

        fdat['muscle_distal'].align_roll(
            fdat['midpoint_origin'].z_axis)





class AdjustFiberBend(bpy.types.Operator):
    """Adjusts the orientation of the origin, insertion and their respective tracker bones to orient towords the bend_target"""
    bl_idname = "rigging.adjust_fiber_bend"
    bl_label = "Adjust Fiber Bend"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        adjust_fiber(context)
        return {'FINISHED'}


operator_data = []

operator_data.append({
    'class': AdjustFiberBend,
    'keymap': 'U',
    'ctrl': True,
    'alt': True,
    'shift': False,
})



if __name__ == '__main__':
    print('boom')

    adjust_fiber(bpy.context)
