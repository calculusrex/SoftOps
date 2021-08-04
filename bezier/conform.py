import bpy
import functools as ft
from mathutils import Vector #
import time

# import sys
# dev_path = '/home/feral/engineering/addon_workshop/softops'
# sys.path.insert(1, dev_path)

from bezier.silhuette import get_name_core__from_active, get_silhuette_data
from utils import preferably_second_ones, rotate_index




def align_handles(h1, p1, h2):
    a = h1 - p1
    b = h2 - p1
    down = b - a
    down /= down.magnitude
    up = -down
    a_ = up * a.magnitude
    b_ = down * b.magnitude
    h1_ = p1 + a_
    h2_ = p1 + b_
    return h1_, p1, h2_


def align_up_handle(h1, p1, h2):
    a = h1 - p1
    b = h2 - p1
    down = b / b.magnitude
    up = -down
    a_ = up * a.magnitude
    h1_ = p1 + a_
    return h1_, p1, h2


def align_down_handle(h1, p1, h2):
    a = h1 - p1
    b = h2 - p1
    up = a / a.magnitude
    down = -up
    b_ = down * a.magnitude
    h2_ = p1 + b_
    return h1, p1, h2_



def node_handles__from_bezier_point(bp):
    core = bp.co.copy()
    up = bp.handle_left.copy()
    down = bp.handle_right.copy()
    return up, core, down


def get_spline_node_handles(ob, pos):
    spline = ob.data.splines[0]
    bezier_point = spline.bezier_points[pos]
    up = bezier_point.handle_left.copy()
    core = bezier_point.co.copy()
    down = bezier_point.handle_right.copy()
    return up, core, down
    


def update_spline_node(ob, pos, up, core, down):
    spline = ob.data.splines[0]
    bezier_point = spline.bezier_points[pos]
    bezier_point.co = core
    bezier_point.handle_left = up
    bezier_point.handle_right = down    




def conform_spline_node(ob, pos, up=None, core=None, down=None):
    current_handles = get_spline_node_handles(ob, pos)

    up, core, down = preferably_second_ones(current_handles,
                                            [up, core, down])

    update_spline_node(ob, pos, up, core, down)    


def conform_spline_node__auto_align(ob, pos, up=None, core=None, down=None):
    if up == None and core == None and down == None:
        up, core, down = get_spline_node_handles(ob, pos)

    elif up == None and down == None:
        up, _, down = get_spline_node_handles(ob, pos)
        up, core, down = align_handles(up, core, down)
        
    elif up == None and core == None: 
        up, core, _ = get_spline_node_handles(ob, pos)
        up, _, _ = align_up_handle(up, core, down)

    elif core == None and down == None:
        _, core, down = get_spline_node_handles(ob, pos)
        _, _, down = align_down_handle(up, core, down)

    elif core == None:
        _, core, _ = get_spline_node_handles(ob, pos)
        up, _, down = align_handles(up, core, down)

    elif up == None:
        up, _, _ = get_spline_node_handles(ob, pos)
        up, _, _ = align_up_handle(up, core, down)

    elif down == None:
        _, _, down = get_spline_node_handles(ob, pos)
        _, _, down = align_down_handle(up, core, down)

    else:
        up, core, down = align_handles(up, core, down)
        
    update_spline_node(ob, pos, up, core, down)



def maybe_point_triples__from_column(column_data, key):
    if column_data[key] == None:
        none_triples = list(map(lambda _: (None, None, None),
                                range(len(column_data['core']['nodes']))))
        return none_triples

    else:
        point_triples = list(map(lambda point_data: (point_data['up_handle'], point_data['core'], point_data['down_handle']),
                                 column_data[key]['nodes']))
        return point_triples
                             
    

# : COLUMN DATA -> ( [ (h1_0, p1_0, h2_0) ], [ (h1_1, p1_1, h2_1) ], [ (h1_2, p1_2, h2_2) ] )
def column_node_vectors(column_data):
    h1_triples, p1_triples, h2_triples = list(
        map(lambda key: maybe_point_triples__from_column(column_data, key),
            ['up_handle', 'core', 'down_handle']))

    return h1_triples, p1_triples, h2_triples


# : COLUMN DATA -> [ ( (h1_0, h1_1, h1_2), (p1_0, p1_1, p1_2), (h2_0, h2_1, h2_2) ) ]
def spline_conform_data__from_column(column_data):
    h1_triples, p1_triples, h2_triples = column_node_vectors(column_data)
    transposed_nodes = list(zip(h1_triples, p1_triples, h2_triples))
    nodes = list(map(lambda t_node: list(zip(*t_node)),
                     transposed_nodes))
    return nodes


def conform_data__from_silhuette_data(silhuette_data, axis):
    return list(map(spline_conform_data__from_column,
                    silhuette_data[axis]['columns']))


def conform_column(column_data, pos, up_handle_triple, core_triple, down_handle_triple, spline_role=None):
    if spline_role == 'core':
        conform_spline_node__auto_align(column_data['core']['object'],
                                        pos,
                                        *core_triple)

    elif spline_role == 'handle':
        if column_data['up_handle'] != None:
            conform_spline_node__auto_align(column_data['up_handle']['object'],
                                            pos,
                                            *up_handle_triple)

        if column_data['down_handle'] != None:
            conform_spline_node__auto_align(column_data['down_handle']['object'],
                                            pos,
                                            *down_handle_triple)

    else:
        if column_data['up_handle'] != None:
            conform_spline_node__auto_align(column_data['up_handle']['object'],
                                            pos,
                                            *up_handle_triple)

        conform_spline_node__auto_align(column_data['core']['object'],
                                        pos,
                                        *core_triple)

        if column_data['down_handle'] != None:
            conform_spline_node__auto_align(column_data['down_handle']['object'],
                                            pos,
                                            *down_handle_triple)




def conform_longitudinal_to_transversal(silhuette_data, spline_role=None, auto_align=True): # try implement non-aligned conforming too

    conform_data = conform_data__from_silhuette_data(silhuette_data, axis='transversal')
    
    for l_index in range(len(silhuette_data['longitudinal']['columns'])):
        for t_index in range(len(silhuette_data['transversal']['columns'])):
            up_handle_triple, core_triple, down_handle_triple = conform_data[t_index][l_index]
            conform_column(
                silhuette_data['longitudinal']['columns'][l_index],
                t_index,
                up_handle_triple, core_triple, down_handle_triple,
                spline_role=spline_role
            )


def conform_transversal_to_longitudinal(silhuette_data, spline_role=None, auto_align=True): # try implement non-aligned conforming too

    conform_data = conform_data__from_silhuette_data(silhuette_data, axis='longitudinal')
    
    for t_index in range(len(silhuette_data['transversal']['columns'])):
        for l_index in range(len(silhuette_data['longitudinal']['columns'])):
            up_handle_triple, core_triple, down_handle_triple = conform_data[l_index][t_index]
            conform_column(
                silhuette_data['transversal']['columns'][t_index],
                l_index,
                up_handle_triple, core_triple, down_handle_triple,
                spline_role=spline_role
                
            )


def conform_longitudinal_splines_to_transversal(silhuette_data, auto_align=True):
    conform_longitudinal_to_transversal(silhuette_data, auto_align=True)

def conform_longitudinal_handles_to_transversal(silhuette_data, auto_align=True):
    conform_longitudinal_to_transversal(silhuette_data, spline_role='handle', auto_align=True)

def conform_longitudinal_cores_to_transversal(silhuette_data, auto_align=True):
    conform_longitudinal_to_transversal(silhuette_data, spline_role='core', auto_align=True)


def conform_transversal_splines_to_longitudinal(silhuette_data, auto_align=True):
    conform_transversal_to_longitudinal(silhuette_data, auto_align=True)

def conform_transversal_handles_to_longitudinal(silhuette_data, auto_align=True):
    conform_transversal_to_longitudinal(silhuette_data, spline_role='handle', auto_align=True)

def conform_transversal_cores_to_longitudinal(silhuette_data, auto_align=True):
    conform_transversal_to_longitudinal(silhuette_data, spline_role='core', auto_align=True)
            
            

            
    


def conform_longitudinal_splines_to_transversal__from_active(context):
    name_core = get_name_core__from_active(context)
    silhuette_data = get_silhuette_data(context, name_core)
    conform_longitudinal_splines_to_transversal(silhuette_data)

def conform_longitudinal_handles_to_transversal__from_active(context):
    name_core = get_name_core__from_active(context)
    silhuette_data = get_silhuette_data(context, name_core)
    conform_longitudinal_handles_to_transversal(silhuette_data)

def conform_longitudinal_cores_to_transversal__from_active(context):
    name_core = get_name_core__from_active(context)
    silhuette_data = get_silhuette_data(context, name_core)
    conform_longitudinal_cores_to_transversal(silhuette_data)


def conform_transversal_splines_to_longitudinal__from_active(context):
    name_core = get_name_core__from_active(context)
    silhuette_data = get_silhuette_data(context, name_core)
    conform_transversal_splines_to_longitudinal(silhuette_data)

def conform_transversal_handles_to_longitudinal__from_active(context):
    name_core = get_name_core__from_active(context)
    silhuette_data = get_silhuette_data(context, name_core)
    conform_transversal_handles_to_longitudinal(silhuette_data)

def conform_transversal_cores_to_longitudinal__from_active(context):
    name_core = get_name_core__from_active(context)
    silhuette_data = get_silhuette_data(context, name_core)
    conform_transversal_cores_to_longitudinal(silhuette_data)







class ConformLongitudinalSplinesToTransversal_FromActive(bpy.types.Operator):
    bl_idname = 'object.conform_long_splines_to_transversal_from_active'
    bl_label = 'LON -> TRAN'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        conform_longitudinal_splines_to_transversal__from_active(context)
        return {'FINISHED'}

class ConformLongitudinalHandlesToTransversal_FromActive(bpy.types.Operator):
    bl_idname = 'object.conform_long_handles_to_transversal_from_active'
    bl_label = 'LON handles -> TRAN'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        conform_longitudinal_handles_to_transversal__from_active(context)
        return {'FINISHED'}

class ConformLongitudinalCoresToTransversal_FromActive(bpy.types.Operator):
    bl_idname = 'object.conform_long_cores_to_transversal_from_active'
    bl_label = 'LON cores -> TRAN'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        conform_longitudinal_cores_to_transversal__from_active(context)
        return {'FINISHED'}



class ConformTransversalSplinesToLongitudinal_FromActive(bpy.types.Operator):
    bl_idname = 'object.conform_trans_splines_to_longitudinal_from_active'
    bl_label = 'TRAN -> LON'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        conform_transversal_splines_to_longitudinal__from_active(context)
        return {'FINISHED'}

class ConformTransversalHandlesToLongitudinal_FromActive(bpy.types.Operator):
    bl_idname = 'object.conform_trans_handles_to_longitudinal_from_active'
    bl_label = 'TRAN handles -> LON'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        conform_transversal_handles_to_longitudinal__from_active(context)
        return {'FINISHED'}

class ConformTransversalCoresToLongitudinal_FromActive(bpy.types.Operator):
    bl_idname = 'object.conform_trans_cores_to_longitudinal_from_active'
    bl_label = 'TRAN cores -> LON'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        conform_transversal_cores_to_longitudinal__from_active(context)
        return {'FINISHED'}









keyless_operator_classes = [
    ConformLongitudinalSplinesToTransversal_FromActive,
    ConformTransversalSplinesToLongitudinal_FromActive,
    ConformLongitudinalHandlesToTransversal_FromActive,
    ConformTransversalHandlesToLongitudinal_FromActive,
    ConformLongitudinalCoresToTransversal_FromActive,
    ConformTransversalCoresToLongitudinal_FromActive,
]

keyless_op_data = []
for c in keyless_operator_classes:
    keyless_op_data.append({
        'class': c
    })
    






if __name__ == '__main__':
    print('boom')

    from mesh_basic import plot_vectors

    context = bpy.context

    plot = lambda vectors: plot_vectors(context, vectors)
    
    name_core = get_name_core__from_active(context)
    print()
    print('name_core: ', name_core)
    print()
    
    silhuette_data = get_silhuette_data(context, name_core)

    conform_data = conform_data__from_silhuette_data(silhuette_data, axis='transversal')

    for l_index in range(len(silhuette_data['longitudinal']['columns'])):
        for t_index in range(len(silhuette_data['transversal']['columns'])):
            node_index = l_index
            up_handle_triple, core_triple, down_handle_triple = conform_data[t_index][node_index]

            column_data = silhuette_data['longitudinal']['columns'][l_index]

            pos = t_index
            
            if column_data['up_handle'] != None:
                conform_spline_node__auto_align(column_data['up_handle']['object'],
                                                pos,
                                                *up_handle_triple)

            conform_spline_node__auto_align(column_data['core']['object'],
                                            pos,
                                            *core_triple)

            if column_data['down_handle'] != None:
                conform_spline_node__auto_align(column_data['down_handle']['object'],
                                                pos,
                                                *down_handle_triple)






            # conform_column(
            #     silhuette_data['longitudinal']['columns'][l_index],
            #     t_index,
            #     up_handle_triple, core_triple, down_handle_triple
            # )
