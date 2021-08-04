import bpy
import bmesh


def octahedron(head, tail, base_position, base_side, bone_x, bone_y, bone_z):
    pass


def octahedron_meshing(context):

    armature = context.active_object

    data = {}
    for bone_name in armature.data.edit_bones.keys():
        print(bone_name)
        data[bone_name] = describe_bone_mesh(context, bone_name)

    install_mesh(context, data)


if __name__ == '__main__':
    print('armature_to_mesh.py')


    context = bpy.context
    
    octahedron_meshing(context)
    
