import bpy

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)



def select_n_set_active__edit_bone(armature, bone_name):
    bone = armature.data.edit_bones[bone_name]
    bone.select = True
    armature.data.edit_bones.active = bone


