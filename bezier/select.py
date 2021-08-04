import bpy

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)


from bezier.silhuette import get_silhuette_data, axis__from_name_data, get_name_core__from_active, get_name_data__from_active



def select_longitudinal_handle_splines(context, name_core):
    silhuette_data = get_silhuette_data(context, name_core)
    
    for spline_ob in silhuette_data['objects']['longitudinal']['handle']:
        spline_ob.select_set(True)

def select_transversal_handle_splines(context, name_core):
    silhuette_data = get_silhuette_data(context, name_core)
    
    for spline_ob in silhuette_data['objects']['transversal']['handle']:
        spline_ob.select_set(True)

def select_longitudinal_core_splines(context, name_core):
    silhuette_data = get_silhuette_data(context, name_core)
    
    for spline_ob in silhuette_data['objects']['longitudinal']['core']:
        spline_ob.select_set(True)

def select_transversal_core_splines(context, name_core):
    silhuette_data = get_silhuette_data(context, name_core)
    
    for spline_ob in silhuette_data['objects']['transversal']['core']:
        spline_ob.select_set(True)

def select_longitudinal_splines(context, name_core):
    silhuette_data = get_silhuette_data(context, name_core)
    
    for spline_ob in silhuette_data['objects']['longitudinal']['all']:
        spline_ob.select_set(True)

def select_transversal_splines(context, name_core):
    silhuette_data = get_silhuette_data(context, name_core)
    
    for spline_ob in silhuette_data['objects']['transversal']['all']:
        spline_ob.select_set(True)

def select_splines(context, name_core):
    silhuette_data = get_silhuette_data(context, name_core)
    
    for spline_ob in silhuette_data['objects']['all']:
        spline_ob.select_set(True)


def select_column(context, name_data):
    silhuette_data = get_silhuette_data(context, name_data['name'])
    axis = axis__from_name_data(name_data)
    n = int(name_data['n'])
    column_data = silhuette_data[axis]['columns'][n]
    for key in column_data.keys():
        if column_data[key] != None:
            column_data[key]['object'].select_set(True)



def select_longitudinal_core_splines__from_active(context):
    active_ob__name_core = get_name_core__from_active(context)
    select_longitudinal_core_splines(context, active_ob__name_core)

def select_transversal_core_splines__from_active(context):
    active_ob__name_core = get_name_core__from_active(context)
    select_transversal_core_splines(context, active_ob__name_core)

def select_longitudinal_handle_splines__from_active(context):
    active_ob__name_core = get_name_core__from_active(context)
    select_longitudinal_handle_splines(context, active_ob__name_core)

def select_transversal_handle_splines__from_active(context):
    active_ob__name_core = get_name_core__from_active(context)
    select_transversal_handle_splines(context, active_ob__name_core)

def select_longitudinal_splines__from_active(context):
    active_ob__name_core = get_name_core__from_active(context)
    select_longitudinal_splines(context, active_ob__name_core)

def select_transversal_splines__from_active(context):
    active_ob__name_core = get_name_core__from_active(context)
    select_transversal_splines(context, active_ob__name_core)

def select_splines__from_active(context):
    active_ob__name_core = get_name_core__from_active(context)
    select_splines(context, active_ob__name_core)


def select_column__from_active(context):
    active_ob__name_data = get_name_data__from_active(context)
    select_column(context, active_ob__name_data)


class Select_Longitudinal_Core_Splines__From_Active(bpy.types.Operator):
    bl_idname = 'object.select_longitudinal_core_splines__from_active'
    bl_label = 'SELECT longitudinal - cores'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        select_longitudinal_core_splines__from_active(context)
        return {'FINISHED'}

class Select_Transversal_Core_Splines__From_Active(bpy.types.Operator):
    bl_idname = 'object.select_transversal_core_splines__from_active'
    bl_label = 'SELECT transversal - cores'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        select_transversal_core_splines__from_active(context)
        return {'FINISHED'}

class Select_Longitudinal_Handle_Splines__From_Active(bpy.types.Operator):
    bl_idname = 'object.select_longitudinal_handle_splines__from_active'
    bl_label = 'SELECT longitudinal -  handles'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        select_longitudinal_handle_splines__from_active(context)
        return {'FINISHED'}

class Select_Transversal_Handle_Splines__From_Active(bpy.types.Operator):
    bl_idname = 'object.select_transversal_handle_splines__from_active'
    bl_label = 'SELECT transversal - handles'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        select_transversal_handle_splines__from_active(context)
        return {'FINISHED'}

class Select_Longitudinal_Splines__From_Active(bpy.types.Operator):
    bl_idname = 'object.select_longitudinal_splines__from_active'
    bl_label = 'SELECT longitudinals'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        select_longitudinal_splines__from_active(context)
        return {'FINISHED'}

class Select_Transversal_Splines__From_Active(bpy.types.Operator):
    bl_idname = 'object.select_transversal_splines__from_active'
    bl_label = 'SELECT transversals'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        select_transversal_splines__from_active(context)
        return {'FINISHED'}

class Select_Splines__From_Active(bpy.types.Operator):
    bl_idname = 'object.select_splines__from_active'
    bl_label = 'SELECT all'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        select_splines__from_active(context)
        return {'FINISHED'}

class Select_Column__From_Active(bpy.types.Operator):
    bl_idname = 'object.select_column__from_active'
    bl_label = 'select column from active'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        select_column__from_active(context)
        return {'FINISHED'}




keyless_operator_classes = [
    Select_Splines__From_Active,
    Select_Transversal_Splines__From_Active,
    Select_Longitudinal_Splines__From_Active,
    Select_Transversal_Handle_Splines__From_Active,
    Select_Longitudinal_Handle_Splines__From_Active,
    Select_Transversal_Core_Splines__From_Active,
    Select_Longitudinal_Core_Splines__From_Active,
    Select_Column__From_Active
]

keyless_op_data = []
for c in keyless_operator_classes:
    keyless_op_data.append({
        'class': c
    })
