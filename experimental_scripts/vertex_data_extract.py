import bpy
from mathutils import Vector




def extract_vertex_data__from_selection(context):
    print('------------------------------------------------------------------')
    print('extract_vertex_data__from_selection()')
    print()
    
    data = []
    
    mode = context.active_object.mode # 'probably EDIT'

    # we need to switch from Edit mode to Object mode so the selection gets updated
    bpy.ops.object.mode_set(mode='OBJECT')
    selectedVerts = [v for v in context.active_object.data.vertices if v.select]
    for v in selectedVerts:
        print(v.co)
        vert_data = {}
        vert_data['coordinates'] = v.co
        vert_data['normal'] = v.normal
        data.append(vert_data)

    # back to whatever mode we were in
    bpy.ops.object.mode_set(mode=mode)

    return data

if __name__ == '__main__':
    print('vertex_data_extract.py')

    context = bpy.context

    data = extract_vertex_data__from_selection(context)

    print()
    for x in data:
        print(x)
