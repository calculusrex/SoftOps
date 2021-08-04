import bpy


if __name__ == '__main__':
    print('\n', 'weight_paint__create_vertex_group_from_selected_bone.py', '\n')

    context = bpy.context

    print(context.active_pose_bone.name)
