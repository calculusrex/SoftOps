bl_info = {
    "name": "SoftOps",
    "version": (0, 1, 0),
    "author": "Zorila Mircea",
    "blender": (2, 83, 0),
    "description": "Collection of biomechanical muscle rigging tools",
    "location": "3D Viewport hotkeys",
    "category": "Rigging",
}


import bpy
import functools as ft

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)

from rename import operator_data as rename_operator_data
from muscle_rig import operator_data as muscle_rig_operator_data
from adjust_fiber import operator_data as adjust_fiber_operator_data
from obj import operator_data as obj_operator_data
from menu import operator_data as menu_operator_data
from menu import  keyless_op_data as menu_keyless_op_data
from bezier.obj import keyless_op_data as bezier_obj_keyless_op_data
from pose import keyless_op_data as pose_keyless_op_data
from bezier.conform import keyless_op_data as bezier_conform_keyless_op_data
from bezier.install import keyless_op_data as bezier_install_keyless_op_data
from bezier.select import keyless_op_data as bezier_select_keyless_op_data
from bezier.silhuette import keyless_op_data as bezier_silhuette_keyless_op_data
from bezier.silhuette import operator_data as bezier_silhuette_op_data
from bezier.spline import operator_data as bezier_spline_op_data
from stretch_to_muscle_rig import keyless_op_data as stretch_to_muscle_rig_op_data
from vertex_group import operator_data as vertex_group_op_data
from bbone__from_stretchTo import keyless_op_data as bbone__from_stretchTo_op_data


operator_data = []
operator_datasets = [
    rename_operator_data,
    muscle_rig_operator_data,
    adjust_fiber_operator_data,
    obj_operator_data,
    menu_operator_data,
    bezier_silhuette_op_data,
    bezier_spline_op_data,
    vertex_group_op_data
]
for dataset in operator_datasets:
    operator_data.extend(dataset)

keyless_op_data = []
keyless_op_datasets = [
    menu_keyless_op_data,
    bezier_obj_keyless_op_data,
    pose_keyless_op_data,
    bezier_conform_keyless_op_data,
    bezier_install_keyless_op_data,
    bezier_select_keyless_op_data,
    bezier_silhuette_keyless_op_data,
    stretch_to_muscle_rig_op_data,
    bbone__from_stretchTo_op_data,
]
for dataset in keyless_op_datasets:
    keyless_op_data.extend(dataset)


addon_keymaps = []
    
def register():

    for operator in keyless_op_data:
        bpy.utils.register_class(operator['class'])

    for operator in operator_data:
        bpy.utils.register_class(operator['class'])

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View Generic', space_type='VIEW_3D') # assign space_type as ARMATURE_EDIT
        for operator in operator_data:
            kmi = km.keymap_items.new(operator['class'].bl_idname,
                                      operator['keymap'],
                                      'PRESS',
                                      ctrl=operator['ctrl'],
                                      alt=operator['alt'],
                                      shift=operator['shift'])
            addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    for operator in operator_data:
        bpy.utils.unregister_class(operator['class'])

    for operator in keyless_op_data:
        bpy.utils.unregister_class(operator['class'])


# if __name__ == '__main__':
#     register()
