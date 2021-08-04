import bpy
import functools as ft

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)

from bezier.silhuette import get_silhuette_data__from_active
from rename import coil__bone_name as coil__object_name



def identify_missing_longitudinal_splines__from_tensor_matrix(tensor_matrix):
    identified_missing_spline_indices = []
    for row_index in range(len(tensor_matrix)):
        for spline_index in range(len(tensor_matrix[row_index][0])):
            missing_spline = False
            for node in tensor_matrix[row_index]:
                if None in node[spline_index]:
                    missing_spline = True
            if missing_spline:
                identified_missing_spline_indices.append(
                    {'row': row_index, 'spline': spline_index}
                )
    return identified_missing_spline_indices



def exhaustive_column_names(core_name, axis, index):
    name_data = []
    name_data.append({
        'core_name': core_name,
        'i': index,
        'axis': axis,
        'role': 'core',
        'ob_name': coil__object_name({
            'name': core_name, 'n': index, 'side': None,
            'pres': ['SPL'], 'sufs': [axis, 'core'],            
        })
    })
    for direction in ['up', 'down']:
        name_data.append({
            'core_name': core_name,
            'i': index,
            'axis': axis,
            'role': 'handle',
            'direction': direction,
            'ob_name': coil__object_name({
                'name': core_name, 'n': index, 'side': None,
                'pres': ['SPL'], 'sufs': [axis, 'handle', direction],
            })
        })
    return name_data



def exhaustive_silhuette_names(name_core, transversal_node_n, longitudinal_node_n):
    name_data = {}

    name_data['longitudinal'] = []
    for i in range(transversal_node_n):
        name_data['longitudinal'].extend(exhaustive_column_names(name_core, 'longitudinal', i))

    name_data['transversal'] = []
    for i in range(longitudinal_node_n):
        name_data['transversal'].extend(exhaustive_column_names(name_core, 'transversal', i))

    return name_data



def identify_missing_splines__from_silhuette_data(silhuette_data):
    name_core = silhuette_data['name_core']
    transversal_node_n = len(
        silhuette_data['transversal']['all'][0]['spline'].bezier_points)
    
    longitudinal_node_n = len(
        silhuette_data['longitudinal']['all'][0]['spline'].bezier_points)
    
    exhaustive_name_data = exhaustive_silhuette_names(name_core, transversal_node_n, longitudinal_node_n)
    ob_names_in_silhuette = list(map(lambda ob: ob.name, silhuette_data['objects']['all']))

    data = {}
    data['transversal'] = list(filter(lambda d: d['ob_name'] not in ob_names_in_silhuette,
                                      exhaustive_name_data['transversal']))
    data['longitudinal'] = list(filter(lambda d: d['ob_name'] not in ob_names_in_silhuette,
                                       exhaustive_name_data['longitudinal']))
    return data



def identify_missing_splines__from_active(context):
    silhuette_data = get_silhuette_data__from_active(context)
    return identify_missing_splines__from_silhuette_data(silhuette_data)




if __name__ == '__main__':
    print('identify_missing.py')

    context = bpy.context

    missing_spline_data = identify_missing_splines__from_active(context)

    print()
    for axis in ['transversal', 'longitudinal']:
        print(axis)
        for record in missing_spline_data[axis]:
            print(record)
        print()
    print()

    
