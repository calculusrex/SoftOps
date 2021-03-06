import bpy
import functools as ft



def other_side(side):
    if side == 'L':
        return 'R'
    else:
        return 'L'

def uncoil__bone_name(bone_name):
    data = {}
    xs = bone_name.split(".")
    name_affixed = xs[0]
    if len(xs) > 1 and (xs[1] == 'L' or xs[1] == 'R'):
        data['side'] = xs[1]
    else:
        data['side'] = None
    xs = name_affixed.split("__")
    if len(xs) == 1:
        data['name'] = xs[0]
        data['pres'] = []
        data['sufs'] = []
    else:
        data['name'] = xs[1]
        if xs[0] == '':
            data['pres'] = []
        else:
            data['pres'] = xs[0].split('_')
        if xs[2] == '':
            data['sufs'] = []
        else:
            data['sufs'] = xs[2].split('_')
    data['pres'].reverse()
    if '_' in data['name']:
        data['name'], data['n'] = tuple(data['name'].split('_'))
        data['n'] = int(data['n'])
    else:
        data['n'] = None
    return data

def coil__bone_name(name_data):
    name_data['pres'].reverse()
    if name_data['pres'] == []:
        prefix = ''
    else:
        prefix = ft.reduce(lambda a, b: f'{a}_{b}',
                           name_data['pres'])
    if name_data['sufs'] == []:
        suffix = ''
    else:
        suffix = ft.reduce(lambda a, b: f'{a}_{b}',
                           name_data['sufs'])
    name = name_data['name']
    side = name_data['side']
    n = name_data['n']
    if n == None:
        accretion = f'{prefix}__{name}__{suffix}'
    else:
        accretion = f'{prefix}__{name}_{n}__{suffix}'
    if side == None:
        return accretion
    else:            
        return f'{accretion}.{side}'

def side__bone_name(bone_name):
    bone_name_data = uncoil__bone_name(bone_name)
    return bone_name_data['side']

def number__bone_name(bone_name):
    data = uncoil__bone_name(bone_name)
    return data['n']

def name__bone_name(bone_name):
    bone_name_data = uncoil__bone_name(bone_name)
    return bone_name_data['name']

def sufs__bone_name(bone_name):
    data = uncoil__bone_name(bone_name)
    return data['sufs']

def pres__bone_name(bone_name):
    data = uncoil__bone_name(bone_name)
    return data['pres']

def is_bone_name_of_muscle_rig(bone_name, muscle_name):
    bone_name_data = uncoil__bone_name(bone_name)
    muscle_name_data = uncoil__bone_name(muscle_name)
    side = bone_name_data['side'] == muscle_name_data['side']
    name = bone_name_data['name'] == muscle_name_data['name']
    n = bone_name_data['n'] == muscle_name_data['n']
    return side and name and n

def is_bone_name_of_wide_muscle_rig(bone_name, muscle_name):
    bone_name_data = uncoil__bone_name(bone_name)
    muscle_name_data = uncoil__bone_name(muscle_name)
    side = bone_name_data['side'] == muscle_name_data['side']
    name = bone_name_data['name'] == muscle_name_data['name']
    return side and name

def rename__bone_name(bone_name, name):
    data = uncoil__bone_name(bone_name)
    data['name'] = name
    return coil__bone_name(data)

def prefix__bone_name(bone_name, prefix):
    data = uncoil__bone_name(bone_name)
    data['pres'].append(prefix)
    return coil__bone_name(data)

def remove_prefix__bone_name(bone_name):
    data = uncoil__bone_name(bone_name)
    if len(data['pres']) != 0:
        data['pres'].pop()
    return coil__bone_name(data)

def suffix__bone_name(bone_name, suffix):
    data = uncoil__bone_name(bone_name)
    data['sufs'].append(suffix)
    return coil__bone_name(data)

def remove_suffix__bone_name(bone_name):
    data = uncoil__bone_name(bone_name)
    if len(data['sufs']) != 0:
        data['sufs'].pop()
    return coil__bone_name(data)

def increment__bone_name(bone_name):
    data = uncoil__bone_name(bone_name)
    if data['n'] == None:
        data['n'] = 0
    else:
        data['n'] += 1
    return coil__bone_name(data)

def decrement__bone_name(bone_name):
    data = uncoil__bone_name(bone_name)
    if data['n'] == 0:
        data['n'] = None
    elif data['n'] != None:
        data['n'] -= 1
    return coil__bone_name(data)

def flip_side__bone_name(bone_name):
    elements = bone_name.split('.')
    if len(elements) == 1:
        elements.append("L")
    elif elements[1] == 'L':
        elements[1] = 'R'
    else:
        elements[1] = 'L'
    return ft.reduce(lambda a, b: f'{a}.{b}',
                     elements[:2])

def remove_trailing_elements__bone_name(bone_name):
    elements = bone_name.split('.')
    return ft.reduce(lambda a, b: f'{a}.{b}',
                     elements[:2])


def prefix__bone(bone, prefix):
    bone.name = prefix__bone_name(bone.name, prefix)
    
def suffix__bone(bone, suffix):
    bone.name = suffix__bone_name(bone.name, suffix)

def flip_side__bone(bone):
    bone.name = flip_side__bone_name(bone.name)

def remove_trailing_elements__bone(bone):
    bone.name = remove_trailing_elements__bone_name(bone.name)

def remove_prefix__bone(bone):
    bone.name = remove_prefix__bone_name(bone.name)

def remove_suffix__bone(bone):
    bone.name = remove_suffix__bone_name(bone.name)

def rename__bone(bone, name):
    bone.name = rename__bone_name(bone.name, name)

def increment__bone(bone):
    bone.name = increment__bone_name(bone.name)

def decrement__bone(bone):
    bone.name = decrement__bone_name(bone.name)


def prefix__selected_bones(context, prefix):
    for bone in context.selected_bones:
        prefix__bone(bone, prefix)

def suffix__selected_bones(context, suffix):
    for bone in context.selected_bones:
        suffix__bone(bone, suffix)

def flip_side__selected_bones(context):
    for bone in context.selected_bones:
        flip_side__bone(bone)

def remove_trailing_elements__selected_bones(context):
    for bone in context.selected_bones:
        remove_trailing_elements__bone(bone)

def remove_prefix__selected_bones(context):
    for bone in context.selected_bones:
        remove_prefix__bone(bone)

def remove_suffix__selected_bones(context):
    for bone in context.selected_bones:
        remove_suffix__bone(bone)

def rename__selected_bones(context, name):
    for bone in context.selected_bones:
        rename__bone(bone, name)

def increment__selected_bones(context):
    for bone in context.selected_bones:
        increment__bone(bone)

def decrement__selected_bones(context):
    for bone in context.selected_bones:
        decrement__bone(bone)




def prefix__selected_objects(context, prefix):
    for bone in context.selected_objects:
        prefix__bone(bone, prefix)

def suffix__selected_objects(context, suffix):
    for bone in context.selected_objects:
        suffix__bone(bone, suffix)

def flip_side__selected_objects(context):
    for bone in context.selected_objects:
        flip_side__bone(bone)

def remove_trailing_elements__selected_objects(context):
    for bone in context.selected_objects:
        remove_trailing_elements__bone(bone)

def remove_prefix__selected_objects(context):
    for bone in context.selected_objects:
        remove_prefix__bone(bone)

def remove_suffix__selected_objects(context):
    for bone in context.selected_objects:
        remove_suffix__bone(bone)

def rename__selected_objects(context, name):
    for bone in context.selected_objects:
        rename__bone(bone, name)

def increment__selected_objects(context):
    for bone in context.selected_objects:
        increment__bone(bone)

def decrement__selected_objects(context):
    for bone in context.selected_objects:
        decrement__bone(bone)

        

class PrefixSelectedBones(bpy.types.Operator):
    """Puts a custom string at the begining of the names of selected bones."""
    bl_idname = "armature.prefix_selected_bones"
    bl_label = "Prefix Selected Bones"
    bl_options = {'REGISTER', 'UNDO'}

    prefix: bpy.props.StringProperty(name="Prefix")

    def execute(self, context):
        prefix__selected_bones(context, self.prefix)
        return {'FINISHED'}

class SuffixSelectedBones(bpy.types.Operator):
    """Puts a custom string at the end of the first dot sepparated element of the names of selected bones."""
    bl_idname = "armature.suffix_selected_bones"
    bl_label = "Suffix Selected Bones"
    bl_options = {'REGISTER', 'UNDO'}

    suffix: bpy.props.StringProperty(name="Suffix")

    def execute(self, context):
        suffix__selected_bones(context, self.suffix)
        return {'FINISHED'}

class FlipSideSelectedBones(bpy.types.Operator):
    """In blender, bones can be edited simmetrically if they have .L and .R suffixed to their names. These suffixes denote their side. this operator flips the side, replacing L with R and R with L."""
    bl_idname = "armature.flip_side_selected_bones"
    bl_label = "Flip Side Selected Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        flip_side__selected_bones(context)
        return {'FINISHED'}

class RemoveTrailingElementsSelectedBones(bpy.types.Operator):
    """It just leaves the name of the bone and the side, sepparated by a dot"""
    bl_idname = "armature.remove_trailing_elements_selected_bones"
    bl_label = "Remove Trailing Elements Selected Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        remove_trailing_elements__selected_bones(context)
        return {'FINISHED'}

class RemovePrefixSelectedBones(bpy.types.Operator):
    """Removes the first underline sepparated string from the name of the selected bones"""
    bl_idname = "armature.remove_prefix_selected_bones"
    bl_label = "Remove Prefix Selected Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        remove_prefix__selected_bones(context)
        return {'FINISHED'}

class RemoveSuffixSelectedBones(bpy.types.Operator):
    """Removes the first underline sepparated string from the name of the selected bones"""
    bl_idname = "armature.remove_suffix_selected_bones"
    bl_label = "Remove Suffix Selected Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        remove_suffix__selected_bones(context)
        return {'FINISHED'}

class RenameSelectedBones(bpy.types.Operator):
    """Changes the bone name, the first element in the dot sepparated chain of strings in the bone.name"""
    bl_idname = "armature.rename_selected_bones"
    bl_label = "Rename Selected Bones"
    bl_options = {'REGISTER', 'UNDO'}

    name: bpy.props.StringProperty(name="Name")

    def execute(self, context):
        rename__selected_bones(context, self.name)
        return {'FINISHED'}

class IncrementSelectedBones(bpy.types.Operator):
    """Increments the bone name, affixes a _ sepparated integer to the core name"""
    bl_idname = "armature.increment_selected_bones"
    bl_label = "Increment Selected Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        increment__selected_bones(context)
        return {'FINISHED'}

class DecrementSelectedBones(bpy.types.Operator):
    """Decrements the bone name, affixes a _ sepparated integer to the core name (or removes it entirely)"""
    bl_idname = "armature.decrement_selected_bones"
    bl_label = "Decrement Selected Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        decrement__selected_bones(context)
        return {'FINISHED'}






class PrefixSelectedObjects(bpy.types.Operator):
    """Puts a custom string at the begining of the names of selected objects."""
    bl_idname = "armature.prefix_selected_objects"
    bl_label = "Prefix Selected Objects"
    bl_options = {'REGISTER', 'UNDO'}

    prefix: bpy.props.StringProperty(name="Prefix")

    def execute(self, context):
        prefix__selected_objects(context, self.prefix)
        return {'FINISHED'}

class SuffixSelectedObjects(bpy.types.Operator):
    """Puts a custom string at the end of the first dot sepparated element of the names of selected objects."""
    bl_idname = "armature.suffix_selected_objects"
    bl_label = "Suffix Selected Objects"
    bl_options = {'REGISTER', 'UNDO'}

    suffix: bpy.props.StringProperty(name="Suffix")

    def execute(self, context):
        suffix__selected_objects(context, self.suffix)
        return {'FINISHED'}

class FlipSideSelectedObjects(bpy.types.Operator):
    """In blender, objects can be edited simmetrically if they have .L and .R suffixed to their names. These suffixes denote their side. this operator flips the side, replacing L with R and R with L."""
    bl_idname = "armature.flip_side_selected_objects"
    bl_label = "Flip Side Selected Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        flip_side__selected_objects(context)
        return {'FINISHED'}

class RemoveTrailingElementsSelectedObjects(bpy.types.Operator):
    """It just leaves the name of the object and the side, sepparated by a dot"""
    bl_idname = "armature.remove_trailing_elements_selected_objects"
    bl_label = "Remove Trailing Elements Selected Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        remove_trailing_elements__selected_objects(context)
        return {'FINISHED'}

class RemovePrefixSelectedObjects(bpy.types.Operator):
    """Removes the first underline sepparated string from the name of the selected objects"""
    bl_idname = "armature.remove_prefix_selected_objects"
    bl_label = "Remove Prefix Selected Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        remove_prefix__selected_objects(context)
        return {'FINISHED'}

class RemoveSuffixSelectedObjects(bpy.types.Operator):
    """Removes the first underline sepparated string from the name of the selected objects"""
    bl_idname = "armature.remove_suffix_selected_objects"
    bl_label = "Remove Suffix Selected Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        remove_suffix__selected_objects(context)
        return {'FINISHED'}

class RenameSelectedObjects(bpy.types.Operator):
    """Changes the object name, the first element in the dot sepparated chain of strings in the object.name"""
    bl_idname = "armature.rename_selected_objects"
    bl_label = "Rename Selected Objects"
    bl_options = {'REGISTER', 'UNDO'}

    name: bpy.props.StringProperty(name="Name")

    def execute(self, context):
        rename__selected_objects(context, self.name)
        return {'FINISHED'}

class IncrementSelectedObjects(bpy.types.Operator):
    """Increments the object name, affixes a _ sepparated integer to the core name"""
    bl_idname = "armature.increment_selected_objects"
    bl_label = "Increment Selected Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        increment__selected_objects(context)
        return {'FINISHED'}

class DecrementSelectedObjects(bpy.types.Operator):
    """Decrements the object name, affixes a _ sepparated integer to the core name (or removes it entirely)"""
    bl_idname = "armature.decrement_selected_objects"
    bl_label = "Decrement Selected Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        decrement__selected_objects(context)
        return {'FINISHED'}

    

operator_data = []

operator_data.append({
    'class': PrefixSelectedBones,
    'keymap': 'LEFT_BRACKET',
    'ctrl': True,
    'alt': True,
    'shift': False,
})

operator_data.append({
    'class': SuffixSelectedBones,
    'keymap': 'RIGHT_BRACKET',
    'ctrl': True,
    'alt': True,
    'shift': False,
})

operator_data.append({
    'class': FlipSideSelectedBones,
    'keymap': 'F',
    'ctrl': True,
    'alt': True,
    'shift': False,
})

operator_data.append({
    'class': RemovePrefixSelectedBones,
    'keymap': 'MINUS',
    'ctrl': True,
    'alt': True,
    'shift': False,
})

operator_data.append({
    'class': RemoveSuffixSelectedBones,
    'keymap': 'EQUAL',
    'ctrl': True,
    'alt': True,
    'shift': False,
})

operator_data.append({
    'class': RenameSelectedBones,
    'keymap': 'M',
    'ctrl': True,
    'alt': True,
    'shift': False,
})

operator_data.append({
    'class': IncrementSelectedBones,
    'keymap': 'N',
    'ctrl': True,
    'alt': True,
    'shift': False,
})

operator_data.append({
    'class': DecrementSelectedBones,
    'keymap': 'P',
    'ctrl': True,
    'alt': True,
    'shift': False,
})




operator_data.append({
    'class': PrefixSelectedObjects,
    'keymap': 'LEFT_BRACKET',
    'ctrl': False,
    'alt': True,
    'shift': True,
})

operator_data.append({
    'class': SuffixSelectedObjects,
    'keymap': 'RIGHT_BRACKET',
    'ctrl': False,
    'alt': True,
    'shift': True,
})

operator_data.append({
    'class': FlipSideSelectedObjects,
    'keymap': 'F',
    'ctrl': False,
    'alt': True,
    'shift': True,
})

operator_data.append({
    'class': RemovePrefixSelectedObjects,
    'keymap': 'MINUS',
    'ctrl': False,
    'alt': True,
    'shift': True,
})

operator_data.append({
    'class': RemoveSuffixSelectedObjects,
    'keymap': 'MINUS',
    'ctrl': False,
    'alt': True,
    'shift': False,
})

operator_data.append({
    'class': RenameSelectedObjects,
    'keymap': 'M',
    'ctrl': False,
    'alt': True,
    'shift': True,
})

operator_data.append({
    'class': IncrementSelectedObjects,
    'keymap': 'N',
    'ctrl': False,
    'alt': True,
    'shift': True,
})

operator_data.append({
    'class': DecrementSelectedObjects,
    'keymap': 'P',
    'ctrl': False,
    'alt': True,
    'shift': True,
})
