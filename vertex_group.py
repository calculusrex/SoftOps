import bpy

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)

from rename import coil__bone_name, uncoil__bone_name, other_side



class CreateVertexGroupFromActivePoseBone(bpy.types.Operator):
    """
    Creates a new vertex group with the name of the active pose bone
    - to be used in weight paint mode with pose bones visible
    """
    bl_idname = "armature.vertex_group_from_active_pose_bone"
    bl_label = "Vertex Group from Active Pose Bone"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active_bone_name = context.active_pose_bone.name
        active_bone_name_data = uncoil__bone_name(active_bone_name)
        vg_names = [active_bone_name]
        if active_bone_name_data['side'] != None:
            active_bone_name_data['side'] = other_side(active_bone_name_data['side'])
            vg_names.append(coil__bone_name(active_bone_name_data))
        for name in vg_names:
            context.active_object.vertex_groups.new(name=name)
        return {'FINISHED'}



operator_data = []

operator_data.append({
    'class': CreateVertexGroupFromActivePoseBone,
    'keymap': 'V',
    'ctrl': True,
    'alt': True,
    'shift': False,
})





if __name__ == '__main__':
    print('\n', 'vertex_group.py', '\n')

    context = bpy.context

    print(context.active_pose_bone.name)
