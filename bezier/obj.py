import bmesh
import bpy

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)

from rename import coil__bone_name as coil__object_name

from bezier.silhuette import get_silhuette_data__from_active
from bezier.handle_matrix import handle_matrix__from_active
from bezier.mesh import bezier_mesh__from_handle_matrix, bezier_mesh__from_silhuette_data

from bezier.vectors import uniform_num, adaptive_num


def install_bezier_surface(context, bezier_lamb_type, n, m):
    context = bpy.context

    silhuette_data = get_silhuette_data__from_active(context)

    longitudinally_cyclic = silhuette_data['longitudinal']['cyclic']
    transversally_cyclic = silhuette_data['transversal']['cyclic']
    
    handle_matrix = handle_matrix__from_active(
        context,
        longitudinally_cyclic=longitudinally_cyclic,
        transversally_cyclic=transversally_cyclic)

    bm, vert_data = bezier_mesh__from_handle_matrix(
        'uniform_num', 32, 32, handle_matrix,
        longitudinally_cyclic=longitudinally_cyclic,
        transversally_cyclic=transversally_cyclic)

    obj_name_data = {}
    obj_name_data['name'] = silhuette_data['name_core']
    obj_name_data['n'] = None
    obj_name_data['side'] = None
    obj_name_data['pres'] = ['MSH']
    obj_name_data['sufs'] = ['bezier', 'surface']
    obj_name = coil__object_name(obj_name_data)
    
    update_existing_object = True
    if obj_name in bpy.data.objects.keys():
        obj = bpy.data.objects[obj_name]
        me = obj.data
    else:
        update_existing_object = False
        me = bpy.data.meshes.new(obj_name)
        obj = bpy.data.objects.new(obj_name, me)
        context.collection.objects.link(obj)

    bm.to_mesh(me)
    bm.free()



def install_bezier_surface__auto_aligned(context, bezier_f, n, m, flip_normals=False):
    context = bpy.context

    silhuette_data = get_silhuette_data__from_active(context)

    longitudinally_cyclic = silhuette_data['longitudinal']['cyclic']
    transversally_cyclic = silhuette_data['transversal']['cyclic']

    bm = bezier_mesh__from_silhuette_data(
        bezier_f, n, m, silhuette_data, flip_normals=flip_normals)

    obj_name_data = {}
    obj_name_data['name'] = silhuette_data['name_core']
    obj_name_data['n'] = None
    obj_name_data['side'] = None
    obj_name_data['pres'] = ['MSH']
    obj_name_data['sufs'] = ['bezier', 'surface']
    obj_name = coil__object_name(obj_name_data)
    
    update_existing_object = True
    if obj_name in bpy.data.objects.keys():
        obj = bpy.data.objects[obj_name]
        me = obj.data
    else:
        update_existing_object = False
        me = bpy.data.meshes.new(obj_name)
        obj = bpy.data.objects.new(obj_name, me)
        context.collection.objects.link(obj)

    bm.to_mesh(me)
    bm.free()




class InstallBezierSurface_UniformNum(bpy.types.Operator):
    """
    - Generates a bezier surface mesh object.
    """
    bl_idname = "object.install_bezier_surface__uniform_num"
    bl_label = "Bezier Surface Uniform Nummeric"
    bl_options = {'REGISTER', 'UNDO'}
    longitudinal_vert_count: bpy.props.IntProperty(
        name="Longitudinal Vert Count", default=16, min=4, max=4096)
    transversal_vert_count: bpy.props.IntProperty(
        name="Transversal Vert Count", default=16, min=4, max=4096)

    def execute(self, context):
        install_bezier_surface(context, 'uniform_num',
                               self.longitudinal_vert_count,
                               self.transversal_vert_count)
        return {'FINISHED'}


class InstallBezierSurface_AdaptiveNum(bpy.types.Operator):
    """
    - Generates a bezier surface mesh object.
    """
    bl_idname = "object.install_bezier_surface__adaptive_num"
    bl_label = "Bezier Surface Adaptive Nummeric"
    bl_options = {'REGISTER', 'UNDO'}
    longitudinal_vert_count: bpy.props.IntProperty(
        name="Longitudinal Vert Count", default=16, min=4, max=4096)
    transversal_vert_count: bpy.props.IntProperty(
        name="Transversal Vert Count", default=16, min=4, max=4096)

    def execute(self, context):
        install_bezier_surface(context, 'adaptive_num',
                               self.longitudinal_vert_count,
                               self.transversal_vert_count)
        return {'FINISHED'}


class InstallBezierSurface_UniformSym(bpy.types.Operator):
    """
    - Generates a bezier surface mesh object.
    """
    bl_idname = "object.install_bezier_surface__uniform_sym"
    bl_label = "Bezier Surface Uniform Symbolic"
    bl_options = {'REGISTER', 'UNDO'}
    longitudinal_vert_count: bpy.props.IntProperty(
        name="Longitudinal Vert Count", default=16, min=4, max=4096)
    transversal_vert_count: bpy.props.IntProperty(
        name="Transversal Vert Count", default=16, min=4, max=4096)

    def execute(self, context):
        install_bezier_surface(context, 'uniform_sym',
                               self.longitudinal_vert_count,
                               self.transversal_vert_count)
        return {'FINISHED'}


class InstallBezierSurface_AdaptiveSym(bpy.types.Operator):
    """
    - Generates a bezier surface mesh object.
    """
    bl_idname = "object.install_bezier_surface__adaptive_sym"
    bl_label = "Bezier Surface Adaptive Symbolic"
    bl_options = {'REGISTER', 'UNDO'}
    longitudinal_vert_count: bpy.props.IntProperty(
        name="Longitudinal Vert Count", default=16, min=4, max=4096)
    transversal_vert_count: bpy.props.IntProperty(
        name="Transversal Vert Count", default=16, min=4, max=4096)

    def execute(self, context):
        install_bezier_surface(context, 'adaptive_sym',
                               self.longitudinal_vert_count,
                               self.transversal_vert_count)
        return {'FINISHED'}


class InstallBezierSurface_UniformNum_AutoAligned(bpy.types.Operator):
    """
    - Generates a bezier surface mesh object.
    """
    bl_idname = "object.install_bezier_surface__uniform_num__aa"
    bl_label = "Bezier Surface Uniform Num - AutoAligned"
    bl_options = {'REGISTER', 'UNDO'}
    longitudinal_vert_count: bpy.props.IntProperty(
        name="Longitudinal Vert Count", default=16, min=4, max=4096)
    transversal_vert_count: bpy.props.IntProperty(
        name="Transversal Vert Count", default=16, min=4, max=4096)
    flip_normals: bpy.props.BoolProperty(
        name="Flip Normals", default=False)

    def execute(self, context):
        install_bezier_surface__auto_aligned(context,
                                             uniform_num,
                                             self.longitudinal_vert_count,
                                             self.transversal_vert_count,
                                             flip_normals=self.flip_normals)
        return {'FINISHED'}


class InstallBezierSurface_AdaptiveNum_AutoAligned(bpy.types.Operator):
    """
    - Generates a bezier surface mesh object.
    """
    bl_idname = "object.install_bezier_surface__adaptive_num__aa"
    bl_label = "Bezier Surface Adaptive Num - AutoAligned"
    bl_options = {'REGISTER', 'UNDO'}
    longitudinal_vert_count: bpy.props.IntProperty(
        name="Longitudinal Vert Count", default=16, min=4, max=4096)
    transversal_vert_count: bpy.props.IntProperty(
        name="Transversal Vert Count", default=16, min=4, max=4096)
    flip_normals: bpy.props.BoolProperty(
        name="Flip Normals", default=False)

    def execute(self, context):
        install_bezier_surface__auto_aligned(context,
                                             adaptive_num,
                                             self.longitudinal_vert_count,
                                             self.transversal_vert_count,
                                             flip_normals=self.flip_normals)
        return {'FINISHED'}




keyless_op_data = []

keyless_op_data.append({
    'class': InstallBezierSurface_UniformNum,
})

keyless_op_data.append({
    'class': InstallBezierSurface_AdaptiveNum,
})

keyless_op_data.append({
    'class': InstallBezierSurface_UniformSym,
})

keyless_op_data.append({
    'class': InstallBezierSurface_AdaptiveSym,
})

keyless_op_data.append({
    'class': InstallBezierSurface_UniformNum_AutoAligned,
})

keyless_op_data.append({
    'class': InstallBezierSurface_AdaptiveNum_AutoAligned,
})

if __name__ == '__main__':
    print('obj.py')
