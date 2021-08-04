import bpy
import functools as ft

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)


from bezier.silhuette import get_silhuette_data__from_active

from bezier.identify_missing import identify_missing_splines__from_silhuette_data

from bezier.tensor_matrix import interpolated_tensor_matrix__from_silhuette_data
from bezier.tensor_matrix import silhuette_longitudinal_column_data__from_tensor_matrix, silhuette_transversal_column_data__from_tensor_matrix


    

                

def install_bezier_object(context, name, node_data, cyclic=False):
    print()
    for x in node_data:
        print(x)
    print()
    n = len(node_data)
    bpy.ops.curve.primitive_bezier_curve_add()
    ob = bpy.context.active_object
    ob.name = name
    ob.data.splines[0].use_cyclic_u = cyclic
    if n > 2:
        ob.data.splines[0].bezier_points.add(count=(n-2))
    for i in range(len(node_data)):
        bp = ob.data.splines[0].bezier_points[i]
        bp.co = node_data[i]['core']
        bp.handle_left = node_data[i]['up_handle']
        bp.handle_right = node_data[i]['down_handle']
        bp.handle_left_type = 'ALIGNED'
        bp.handle_right_type = 'ALIGNED'
    return ob



def install_missing_longitudinal_handles__from_active(context):
    silhuette_data = get_silhuette_data__from_active(context)

    longitudinally_cyclic = silhuette_data['longitudinal']['cyclic']
    transversally_cyclic = silhuette_data['transversal']['cyclic']
    
    tensor_matrix = interpolated_tensor_matrix__from_silhuette_data(silhuette_data)
    missing_spline_data = identify_missing_splines__from_silhuette_data(silhuette_data)
    missing_longitudinal_handle__data = list(filter(lambda x: x['role'] == 'handle',
                                                    missing_spline_data['longitudinal']))
    new_silhuette_data = silhuette_longitudinal_column_data__from_tensor_matrix(tensor_matrix)
    obs = []
    for missing__data in missing_longitudinal_handle__data:
        node_data = new_silhuette_data[
            missing__data['i']][
                missing__data['direction']]
        obs.append(
            install_bezier_object(
                context,
                missing__data['ob_name'],
                node_data,
                cyclic=longitudinally_cyclic
            ))
    return obs



def install_missing_transversal_handles__from_active(context):
    silhuette_data = get_silhuette_data__from_active(context)

    longitudinally_cyclic = silhuette_data['longitudinal']['cyclic']
    transversally_cyclic = silhuette_data['transversal']['cyclic']
    
    tensor_matrix = interpolated_tensor_matrix__from_silhuette_data(silhuette_data)
    missing_spline_data = identify_missing_splines__from_silhuette_data(silhuette_data)
    missing_longitudinal_handle__data = list(filter(lambda x: x['role'] == 'handle',
                                                    missing_spline_data['transversal']))
    new_silhuette_data = silhuette_transversal_column_data__from_tensor_matrix(tensor_matrix)
    obs = []
    for missing__data in missing_longitudinal_handle__data:
        node_data = new_silhuette_data[
            missing__data['i']][
                missing__data['direction']]
        obs.append(
            install_bezier_object(
                context,
                missing__data['ob_name'],
                node_data,
                cyclic=transversally_cyclic
            ))
    return obs




class InstallMissingLongitudinalHandles(bpy.types.Operator):
    '''
    - Installs the missing longitudinal handles for more control on the bezier surface geometry
    '''
    bl_idname = 'object.install_missing_longitudinal_handles'
    bl_label = 'Install Missing Longitudinal Handles'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        install_missing_longitudinal_handles__from_active(context)
        return {'FINISHED'}



class InstallMissingTransversalHandles(bpy.types.Operator):
    '''
    - Installs the missing transversal handles for more control on the bezier surface geometry
    '''
    bl_idname = 'object.install_missing_transversal_handles'
    bl_label = 'Install Missing Transversal Handles'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        install_missing_transversal_handles__from_active(context)
        return {'FINISHED'}





keyless_op_data = []

keyless_op_data.append({
    'class': InstallMissingLongitudinalHandles,
})

keyless_op_data.append({
    'class': InstallMissingTransversalHandles,
})



if __name__ == '__main__':
    print('install.py')
    print()
