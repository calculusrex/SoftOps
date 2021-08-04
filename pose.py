import bpy
import functools as ft

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)

from rename import is_bone_name_of_wide_muscle_rig, coil__bone_name, uncoil__bone_name, name__bone_name, number__bone_name, side__bone_name, sufs__bone_name
from utils import are_all_true, is_one_of_them_true
from edit_bones import select_n_set_active__edit_bone





def select_all_pose_bend_targets(context):
    for bone in context.visible_pose_bones:
        if 'bend_target' in bone.name:
            bone.bone.select = True

    bpy.ops.object.posemode_toggle()
    bpy.ops.object.posemode_toggle()


def select_bend_targets_within_fiber(context):
    armature = context.active_object
    active_pose_bone = context.active_pose_bone

    name_data = uncoil__bone_name(active_pose_bone.name)

    discriminator = lambda nd: nd['name'] == name_data['name'] and nd['side'] == name_data['side'] and nd['n'] == name_data['n']
    
    bend_target_bones = map(lambda b: b[0].bone,
                            list(filter(lambda b: 'bend' in b[1]['sufs'] and 'target' in b[1]['sufs'],
                                        filter(lambda b: discriminator(b[1]),
                                               map(lambda b: (b, uncoil__bone_name(b.name)),
                                                   context.visible_pose_bones)))))    
    for bt in bend_target_bones:
        bt.select = True

    active_pose_bone.bone.select = False
        
    bpy.ops.object.posemode_toggle()
    bpy.ops.object.posemode_toggle()


def clear_bend_target_user_transforms(context):
    bpy.ops.pose.select_all(action='DESELECT')
    bpy.ops.object.posemode_toggle()
    bpy.ops.object.posemode_toggle()

    select_all_pose_bend_targets(context)
    bpy.ops.object.posemode_toggle()
    bpy.ops.object.posemode_toggle()

    bpy.ops.pose.user_transforms_clear()
    bpy.ops.object.posemode_toggle()
    bpy.ops.object.posemode_toggle()


# def place_bend_target_on_fiber(context, bend_target):
#     bend_target_name_data = uncoil__bone_name(bend_target.name)
#     criterions = [
#         lambda pose_bone_data: pose_bone_data['name'] == bend_target_name_data['name'],
#         lambda pose_bone_data: pose_bone_data['n'] == bend_target_name_data['n'],
#         lambda pose_bone_data: pose_bone_data['side'] == bend_target_name_data['side']
#     ]
#     fiber_discriminator = lambda pose_bone_data: are_all_true(map(lambda crit: crit(pose_bone_data[1]), criterions))
#     fiber_bones = list(filter(fiber_discriminator,
#                               map(lambda pose_bone: (pose_bone, uncoil__bone_name(pose_bone.name)),
#                                   context.visible_pose_bones)))

#     print()
#     for fb in fiber_bones:
#         print(fb)
#     print()
    
#     bone_data = {}
#     for b, bdat in fiber_bones:
#         key = ft.reduce(lambda a, b: f'{a}_{b}',
#                         bdat['sufs'],
#                         'muscle')
#         print(key)
#         bone_data[key] = b

#     print()
#     print('bone_data: ', bone_data)
#     print()

#     print()
#     print("bend_target_name_data['sufs']: ", bend_target_name_data['sufs'])
#     print()
    
#     if 'origin' in bend_target_name_data['sufs']:
#         new_pos = (bone_data['muscle_origin'].location + bone_data['muscle_midpoint_insertion'].location) / 2
#     elif 'insertion' in bend_target_name_data['sufs']:
#         new_pos = (bone_data['muscle_midpoint_insertion'].location + bone_data['muscle_insertion'].location) / 2
#     else:
#         new_pos = (bone_data['muscle_origin'].location + bone_data['muscle_insertion'].location) / 2

#     print('new_pos: ', new_pos)

#     bend_target.location = new_pos


def place_bend_targets_on_fiber(context):
    bend_targets = list(filter(lambda b: 'bend_target' in b.name,
                               context.visible_pose_bones))
    for bend_target in bend_targets:
        place_bend_target_on_fiber(context, bend_target)
    


class SelectAllPoseBendTargets(bpy.types.Operator):
    """Select all fiber bend targets among context.visible_pose_bones."""
    bl_idname = "rigging.select_all_pose_bend_targets"
    bl_label = "Select All Pose Bend Targets"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        select_all_pose_bend_targets(context)

        return {'FINISHED'}

class SelectBendTargetsWithinFiber(bpy.types.Operator):
    """Select all fiber bend targets among the fiber marked by the active bone ."""
    bl_idname = "rigging.select_bend_targets_within_fiber"
    bl_label = "Select Bend Targets Within Fiber"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        select_bend_targets_within_fiber(context)

        return {'FINISHED'}

class ClearBendTargetUserTransforms(bpy.types.Operator):
    """Clear user transforms on all bend targets."""
    bl_idname = "rigging.clear_bend_target_user_transforms"
    bl_label = "Clear Bend Target User Transforms"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        clear_bend_target_user_transforms(context)

        return {'FINISHED'}

# class PlaceBendTargetsOnFiber(bpy.types.Operator):
#     """Places the fiber bend targets on their respective fibers, so the muscles are restored to a straight position regardless of orientation."""
#     bl_idname = "rigging.place_bend_targets_on_fiber"
#     bl_label = "Place Bend Targets On Fiber"
#     bl_options = {'REGISTER', 'UNDO'}

#     def execute(self, context):
#         place_bend_targets_on_fiber(context)

#         return {'FINISHED'}



keyless_op_data = []

keyless_op_data.append({
    'class': SelectAllPoseBendTargets,
})
keyless_op_data.append({
    'class': SelectBendTargetsWithinFiber,
})
keyless_op_data.append({
    'class': ClearBendTargetUserTransforms,
})
# keyless_op_data.append({
#     'class': PlaceBendTargetsOnFiber,
# })

