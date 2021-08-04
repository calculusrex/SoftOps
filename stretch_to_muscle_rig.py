import bpy
import functools as ft


import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)

from rename import uncoil__bone_name, coil__bone_name, side__bone_name


def generate_nomenclature(context):
    name_data = uncoil__bone_name(context.active_bone.name)
    nomenclature = {}

    name_data['pres'] = ['DEF']
    name_data['sufs'] = []
    nomenclature['muscle'] = coil__bone_name(name_data)

    name_data['pres'] = ['MCH']
    name_data['sufs'] = ['insertion']
    nomenclature['insertion'] = coil__bone_name(name_data)

    return nomenclature


def fetch_insertion_parent(context):
    selected_bones_names = list(map(lambda b: b.name,
                                    context.selected_bones))

    active_bone_name = context.active_bone.name

    insertion_parent_name = list(
        filter(lambda n: n != active_bone_name,
               selected_bones_names))[0]

    return insertion_parent_name


def install_insertion(context):
    insertion_parent_name = fetch_insertion_parent(context)
    insertion_parent = context.active_object.data.edit_bones[
        insertion_parent_name]
    
    nomenclature = generate_nomenclature(context)

    muscle = context.active_object.data.edit_bones[
        nomenclature['muscle']]
    
    insertion = context.active_object.data.edit_bones.new(
        nomenclature['insertion'])

    insertion.head = muscle.tail
    insertion.tail = muscle.tail + (insertion_parent.vector / 10)
    insertion.align_roll(insertion_parent.z_axis)
    insertion.parent = insertion_parent

    return nomenclature


def rig_stretch_to(context, nomenclature):
    bpy.ops.object.posemode_toggle()

    muscle = context.active_object.pose.bones[nomenclature['muscle']]
    stretchTo_constraint = muscle.constraints.new('STRETCH_TO')
    stretchTo_constraint.target = context.active_object
    stretchTo_constraint.subtarget = nomenclature['insertion']

    bpy.ops.object.editmode_toggle()


def stretch_to_rig__from_active(context):
    bpy.context.object.data.use_mirror_x = False

    nomenclature = install_insertion(context)
    rig_stretch_to(context, nomenclature)

    bpy.context.object.data.use_mirror_x = True

    return nomenclature


class StretchToRigFromActive(bpy.types.Operator):
    """Installs and sets up a stretch to constraint rig on active from selected"""
    bl_idname = "rigging.stretch_to_rig_from_active"
    bl_label = "Stretch To Rig From Active"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        stretch_to_rig__from_active(context)

        return {'FINISHED'}



keyless_op_data = []

keyless_op_data.append({
    'class': StretchToRigFromActive,
})



if __name__ == '__main__':
    print()
    
    context = bpy.context

    stretch_to_rig__from_active(context)
    
