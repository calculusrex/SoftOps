import bpy

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)

from utils import flatten_lists
from mesh import generate_fusiform_muscle_mesh, generate_wide_muscle_mesh
from get_bones import bones_within_fiber, bones_within_muscle
from rename import uncoil__bone_name, coil__bone_name
from geometry import linear_falloff
from math import ceil


def identify_verts(obj, position_vectors):
    def find_vert(position_vector):
        return next(
            filter(lambda vert: vert.co == position_vector,
                   obj.data.vertices))
    verts = list(
        map(find_vert,
            position_vectors)
    )
    return verts


def select_object_and_make_active(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)


def get_vertss__from__vert_data(obj, vertex_data, fiber_type):
    vertss = {}

    vertss['origin'] = identify_verts(obj,
                                       vertex_data['origin'])
    if fiber_type == 'DOUBLE':
        vertss['proximal_body_loops'] = list(map(
            lambda loop: identify_verts(obj, loop),
            vertex_data['proximal_body']))

        vertss['distal_body_loops'] = list(map(
            lambda loop: identify_verts(obj, loop),
            vertex_data['distal_body']))
        
    else:
        vertss['body_loops'] = list(map(
            lambda loop: identify_verts(obj, loop),
            vertex_data['body']))

    vertss['insertion'] = identify_verts(obj,
                                         vertex_data['insertion'])
    
    if fiber_type == 'DOUBLE':
        vertss['all'] = vertss['origin'] + flatten_lists(vertss['proximal_body_loops']) + flatten_lists(vertss['distal_body_loops']) + vertss['insertion']
    else:
        vertss['all'] = vertss['origin'] + vertss['body_loops'] + vertss['insertion']

    return vertss


def vertex_group_assign_verts(obj, vg_name, verts_x_weights):
    vertex_group_exists = vg_name in obj.vertex_groups.keys()
    if not vertex_group_exists:
        vgroup = obj.vertex_groups.new(name=vg_name)
    else:
        vgroup = obj.vertex_groups[vg_name]
    weights = set(
        map(lambda vert_x_weight: vert_x_weight[1],
            verts_x_weights))
    for weight in weights:
        vert_indices = list(map(
            lambda vert: vert.index,
            map(lambda vert_x_index: vert_x_index[0],
                filter(lambda vert_x_weight: vert_x_weight[1] == weight,
                       verts_x_weights))))
        vgroup.add(
            vert_indices,
            weight=weight,
            type='REPLACE')


def assign_muscle_verts__double_fiber(muscle_object,
                                      fiber_data,
                                      vertss,
                                      falloff_influence_factor):

    falloff = linear_falloff(
        ceil(
            fiber_data['n_segments'] * falloff_influence_factor))

    origin_verts_x_weights = []
    origin_verts_x_weights.extend(
        list(map(
            lambda vert: (vert, falloff[0]),
            vertss['origin'])))
    for i in range(len(falloff[1:])):
        origin_verts_x_weights.extend(
            list(map(
                lambda vert: (vert, falloff[i+1]),
                vertss['proximal_body_loops'][i])))

    proximal_verts_x_weights = []
    proximal_verts_x_weights.extend(
        list(map(lambda vert: (vert, 1.0),
                 flatten_lists(
                     vertss['proximal_body_loops']))))
    for i in range(len(falloff[1:])):
        proximal_verts_x_weights.extend(
            list(map(
                lambda vert: (vert, falloff[i+1]),
                vertss['distal_body_loops'][i])))

    distal_verts_x_weights = []
    distal_verts_x_weights.extend(
        list(map(lambda vert: (vert, 1.0),
                 flatten_lists(
                     vertss['distal_body_loops']))))
    for i in range(len(falloff[1:])):
        distal_verts_x_weights.extend(
            list(map(
                lambda vert: (vert, falloff[i+1]),
                vertss['proximal_body_loops'][-(i+1)])))

    insertion_verts_x_weights = []
    insertion_verts_x_weights.extend(
        list(map(
            lambda vert: (vert, falloff[0]),
            vertss['insertion'])))
    for i in range(len(falloff[1:])):
        insertion_verts_x_weights.extend(
            list(map(
                lambda vert: (vert, falloff[i+1]),
                vertss['distal_body_loops'][-(i+1)])))

    vertex_group_assign_verts(muscle_object,
                              fiber_data['origin_parent'].name,
                              origin_verts_x_weights)

    vertex_group_assign_verts(muscle_object,
                              fiber_data['muscle_proximal'].name,
                              proximal_verts_x_weights)

    vertex_group_assign_verts(muscle_object,
                              fiber_data['muscle_distal'].name,
                              distal_verts_x_weights)

    vertex_group_assign_verts(muscle_object,
                              fiber_data['insertion_parent'].name,
                              insertion_verts_x_weights)



def assign_muscle_verts(muscle_object,
                        fiber_data,
                        vertss,
                        falloff_influence_factor):

    falloff = linear_falloff(
        ceil(
            fiber_data['n_segments'] * falloff_influence_factor))
    
    origin_verts_x_weights = []
    origin_verts_x_weights.extend(
        list(map(
            lambda vert: (vert, falloff[0]),
            vertss['origin'])))
    for i in range(len(falloff[1:])):
        origin_verts_x_weights.extend(
            list(map(
                lambda vert: (vert, falloff[i+1]),
                vertss['body_loops'][i])))

    muscle_verts_x_weights = []
    muscle_verts_x_weights.extend(
        list(map(lambda vert: (vert, 1.0),
                 flatten_lists(
                     vertss['body_loops']))))

    insertion_verts_x_weights = []
    insertion_verts_x_weights.extend(
        list(map(
            lambda vert: (vert, falloff[0]),
            vertss['insertion'])))
    for i in range(len(falloff[1:])):
        insertion_verts_x_weights.extend(
            list(map(
                lambda vert: (vert, falloff[i+1]),
                vertss['body_loops'][-(i+1)])))

    vertex_group_assign_verts(muscle_object,
                              fiber_data['origin_parent'].name,
                              origin_verts_x_weights)

    vertex_group_assign_verts(muscle_object,
                              fiber_data['muscle'].name,
                              muscle_verts_x_weights)

    vertex_group_assign_verts(muscle_object,
                              fiber_data['insertion_parent'].name,
                              insertion_verts_x_weights)




def install_fusiform_muscle(context,
                            section_vert_count=8,
                            origin_tendon_length=0.0,
                            origin_tendon_radius=0.003,
                            insertion_tendon_length=0.1,
                            insertion_tendon_radius=0.001,
                            flatness=1,
                            body_radius=0.005,
                            subdiv_level=2,
                            falloff_influence_factor=0.1):

    armature = context.active_object

    active_bone = context.active_bone

    fiber_data = bones_within_fiber(armature, active_bone.name)

    vertex_data, new_mesh = generate_fusiform_muscle_mesh(fiber_data,
                                                          section_vert_count=section_vert_count,
                                                          origin_tendon_length=origin_tendon_length,
                                                          origin_tendon_radius=origin_tendon_radius,
                                                          insertion_tendon_length=insertion_tendon_length,
                                                          insertion_tendon_radius=insertion_tendon_radius,
                                                          flatness=flatness,
                                                          body_radius=body_radius)


    if fiber_data['type'] == 'DOUBLE':
        obj_name = fiber_data['muscle_proximal'].name
        obj_name_data = uncoil__bone_name(obj_name)
        obj_name_data['sufs'] = []
        obj_name = coil__bone_name(obj_name_data)
    else:
        obj_name = fiber_data['muscle'].name

    update_existing_object = True

    # We check if the muscle object is allready installed.
    if obj_name in bpy.data.objects.keys():
        # so, it's allready installed, we gonna update it's mesh, not create a new object
        muscle_object = bpy.data.objects[obj_name]
        muscle_mesh = muscle_object.data
    else:
        # if not, we create a new mesh and a new object
        update_existing_object = False
        muscle_mesh = bpy.data.meshes.new(obj_name)
        muscle_object = bpy.data.objects.new(obj_name, muscle_mesh)
        context.collection.objects.link(muscle_object)

    new_mesh.to_mesh(muscle_mesh)
    new_mesh.free()

    vertss = get_vertss__from__vert_data(muscle_object, vertex_data, fiber_data['type'])

    if fiber_data['type'] == 'DOUBLE':
        assign_muscle_verts__double_fiber(muscle_object,
                                          fiber_data,
                                          vertss,
                                          falloff_influence_factor)
    else:    
        assign_muscle_verts(muscle_object,
                            fiber_data,
                            vertss,
                            falloff_influence_factor)

    # refferencing previously bound objects after the following code block might crash blender

    if not update_existing_object:

        bpy.ops.object.mode_set(mode='OBJECT')

        select_object_and_make_active(muscle_object)

        bpy.ops.object.modifier_add(type='ARMATURE')
        muscle_object.modifiers['Armature'].object = armature

        bpy.ops.object.modifier_add(type='SUBSURF')

        muscle_object.select_set(False)
        select_object_and_make_active(armature)

        bpy.ops.object.mode_set(mode='EDIT')

    muscle_object.modifiers['Subdivision'].levels = subdiv_level
    muscle_object.modifiers['Subdivision'].render_levels = subdiv_level



def install_wide_muscle(context,
                        section_vert_count=8,
                        origin_tendon_length=0.0,
                        origin_tendon_radius=0.003,
                        insertion_tendon_length=0.1,
                        insertion_tendon_radius=0.001,
                        flatness=1,
                        body_radius=0.005,
                        subdiv_level=2,
                        falloff_influence_factor=0.1):
    
    armature_obj = context.active_object

    active_bone = context.active_bone

    muscle_data = bones_within_muscle(armature_obj, active_bone.name)

    vertex_data, new_mesh = generate_wide_muscle_mesh(muscle_data,
                                                      section_vert_count=section_vert_count,
                                                      origin_tendon_length=origin_tendon_length,
                                                      origin_tendon_radius=origin_tendon_radius,
                                                      insertion_tendon_radius=insertion_tendon_radius,
                                                      insertion_tendon_length=insertion_tendon_length,
                                                      flatness=flatness,
                                                      body_radius=body_radius)

    first_fiber_data = muscle_data[0]
    if first_fiber_data['type'] == 'DOUBLE':
        obj_name = first_fiber_data['muscle_proximal'].name
        obj_name_data = uncoil__bone_name(obj_name)
        obj_name_data['sufs'] = []
        obj_name = coil__bone_name(obj_name_data)
    else:
        obj_name = first_fiber_data['muscle'].name

    update_existing_object = True
    if obj_name in bpy.data.objects.keys():
        # so, it's allready installed, we gonna update it's mesh, not create a new object
        muscle_object = bpy.data.objects[obj_name]
        muscle_mesh = muscle_object.data
    else:
        # if not, we create a new mesh and a new object
        update_existing_object = False
        muscle_mesh = bpy.data.meshes.new(obj_name)
        muscle_object = bpy.data.objects.new(obj_name, muscle_mesh)
        context.collection.objects.link(muscle_object)

    new_mesh.to_mesh(muscle_mesh)
    new_mesh.free()        

    vertss = []

    for i in range(len(muscle_data)):

        fiber_data = muscle_data[i]        

        vertss = get_vertss__from__vert_data(muscle_object, vertex_data[i], fiber_data['type'])

        if fiber_data['type'] == 'DOUBLE':
            assign_muscle_verts__double_fiber(muscle_object,
                                              fiber_data,
                                              vertss,
                                              falloff_influence_factor)
        else:
            assign_muscle_verts(muscle_object,
                                fiber_data,
                                vertss,
                                falloff_influence_factor)


    # refferencing previously bound objects after the following code block might crash blender

    if not update_existing_object:

        bpy.ops.object.mode_set(mode='OBJECT')

        select_object_and_make_active(muscle_object)

        bpy.ops.object.modifier_add(type='ARMATURE')
        muscle_object.modifiers['Armature'].object = armature_obj

        bpy.ops.object.modifier_add(type='SUBSURF')

        muscle_object.select_set(False)
        select_object_and_make_active(armature_obj)

        bpy.ops.object.mode_set(mode='EDIT')

    muscle_object.modifiers['Subdivision'].levels = subdiv_level
    muscle_object.modifiers['Subdivision'].render_levels = subdiv_level





class InstallFusiformMuscle(bpy.types.Operator):
    """
    - Generates a fusiform muscle mesh, following the curvature and twist of the selected muscle rig,
    - Creates an object manifesting that mesh,
    - Sets up the Armature modifier on that object and the deformation vertex groups.
    """
    bl_idname = "rigging.install_fusiform_muscle"
    bl_label = "Install Fusiform Muscle"
    bl_options = {'REGISTER', 'UNDO'}

    section_vert_count: bpy.props.IntProperty(
        name="Profile Vert Count", default=8, min=3, max=512) # !

    origin_tendon_length: bpy.props.FloatProperty(
        name="Origin Tendon Length", default=0.0, min=0.0, max=10.0)

    origin_tendon_radius: bpy.props.FloatProperty(
        name="Origin Tendon Radius", default=0.3, min=0.001, max=100.0)

    insertion_tendon_length: bpy.props.FloatProperty(
        name="Insertion Tendon Length", default=0, min=0.0, max=10.0)

    insertion_tendon_radius: bpy.props.FloatProperty(
        name="Insertion Tendon Radius", default=0.1, min=0.001, max=100.0)

    body_radius: bpy.props.FloatProperty(
        name="Body Radius", default=0.5, min=0.001, max=100.0)

    flatness: bpy.props.FloatProperty(
        name="Flatness", default=1.33, min=0.01, max=100)

    subdiv_level: bpy.props.IntProperty(
        name="Subdivision Level", default=2, min=0, max=5)

    falloff_influence_factor: bpy.props.FloatProperty(
        name="Tendon Insertion Falloff Influence Factor", default=0.01, min=0.01, max=0.4)

    def execute(self, context):

        install_fusiform_muscle(context,
                                section_vert_count=self.section_vert_count,
                                origin_tendon_length=self.origin_tendon_length/10,
                                origin_tendon_radius=self.origin_tendon_radius/100,
                                insertion_tendon_length=self.insertion_tendon_length/10,
                                insertion_tendon_radius=self.insertion_tendon_radius/100,
                                flatness=self.flatness,
                                body_radius=self.body_radius/100,
                                subdiv_level=self.subdiv_level,
                                falloff_influence_factor=self.falloff_influence_factor)

        return {'FINISHED'}


class InstallWideMuscle(bpy.types.Operator):
    """
    - Generates a wide muscle mesh, following the curvature and twist of muscle rigs sharing a name and numbered consecutively,
    - Creates an object manifesting that mesh,
    - Sets up the Armature modifier on that object and the deformation vertex groups.
    """
    bl_idname = "rigging.install_wide_muscle"
    bl_label = "Install Wide Muscle"
    bl_options = {'REGISTER', 'UNDO'}

    section_vert_count: bpy.props.IntProperty(
        name="Profile Vert Count", default=8, min=3, max=512) # !

    origin_tendon_length: bpy.props.FloatProperty(
        name="Origin Tendon Length", default=0.0, min=0.0, max=10.0)

    origin_tendon_radius: bpy.props.FloatProperty(
        name="Origin Tendon Radius", default=0.3, min=0.001, max=100.0)

    insertion_tendon_length: bpy.props.FloatProperty(
        name="Insertion Tendon Length", default=0.0, min=0.0, max=10.0)

    insertion_tendon_radius: bpy.props.FloatProperty(
        name="Insertion Tendon Radius", default=0.3, min=0.001, max=100.0)

    body_radius: bpy.props.FloatProperty(
        name="Body Radius", default=0.5, min=0.001, max=100.0)

    flatness: bpy.props.FloatProperty(
        name="Flatness", default=1.33, min=0.01, max=100)

    subdiv_level: bpy.props.IntProperty(
        name="Subdivision Level", default=2, min=0, max=5)

    falloff_influence_factor: bpy.props.FloatProperty(
        name="Tendon Insertion Falloff Influence Factor", default=0.01, min=0.01, max=0.4)

    def execute(self, context):

        install_wide_muscle(context,
                            section_vert_count=self.section_vert_count,
                            origin_tendon_length=self.origin_tendon_length/10,
                            origin_tendon_radius=self.origin_tendon_radius/100,
                            insertion_tendon_length=self.insertion_tendon_length/10,
                            insertion_tendon_radius=self.insertion_tendon_radius/100,
                            flatness=self.flatness,
                            body_radius=self.body_radius/100,
                            subdiv_level=self.subdiv_level,
                            falloff_influence_factor=self.falloff_influence_factor)

        return {'FINISHED'}



operator_data = []
operator_data.append({
    'class': InstallFusiformMuscle,
    'keymap': 'I',
    'ctrl': True,
    'alt': True,
    'shift': False,
})

operator_data.append({
    'class': InstallWideMuscle,
    'keymap': 'H',
    'ctrl': True,
    'alt': True,
    'shift': False,
})



if __name__ == '__main__':
    print('boom')


    install_wide_muscle(bpy.context,
                        insertion_tendon_length=0.2,
                        flatness=1.5)
    
