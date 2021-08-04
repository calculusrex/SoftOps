import bpy
import functools as ft
from mathutils import Vector

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)



def align_bone(bone, vector, z_axis):
    bone_vector = bone.tail - bone.head
    align_vector = (vector / vector.magnitude) * bone_vector.magnitude
    offset = align_vector - bone_vector
    bone.tail += offset
    bone.align_roll(z_axis)


def extract_vector_data(bone):
    data = {
        'bone vector': bone.vector,
        'bone z axis': bone.z_axis
    }
    return data


def align_bone_from_bone(target_bone, refference_bone):
    refference_data = extract_vector_data(refference_bone)
    align_bone(
        target_bone,
        refference_data['bone vector'],
        refference_data['bone z axis'])

    
if __name__ == '__main__':
    print('align_selection_from_active.py')

    context = bpy.context

    bones = context.selected_bones

    bones.remove(context.active_bone)

    refference_data = extract_vector_data(context.active_bone)

    for bone in bones:
        align_bone(
            bone,
            refference_data['bone vector'],
            refference_data['bone z axis']
        )
        

    
