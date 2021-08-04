import bpy
from mathutils import Vector

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)

from rename import other_side, uncoil__bone_name, coil__bone_name




def fetch_vector_data(context):
    

    vector_data = {}
    return vector_data


def piston__from_active_bone(context, *params):
    vector_data = fetch_vector_data(context)
    proximal_cyllinder_data = generate_proximal_cyllinder(context, *params)
    distal_cyllinder_data = generate_distal_cyllinder(context, *params)


if __name__ == '__main__':
    print('piston.py')

    
