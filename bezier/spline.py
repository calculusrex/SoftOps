import bpy
import numpy as np

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)


from utils import rotate_index



def get_spline_node_handles(ob, pos):
    spline = ob.data.splines[0]
    bezier_point = spline.bezier_points[pos]
    up = bezier_point.handle_left.copy()
    core = bezier_point.co.copy()
    down = bezier_point.handle_right.copy()
    return up, core, down


# NOTHING FROM THIS FILE SEEMS TO BE IN USE

def align_handles__general(mag_f, h1, p1, h2):
    r1, r2 = (h1 - p1), (h2 - p1)

    downstream_direction = r2 - r1
    upstream_direction = -downstream_direction

    downstream_unit = downstream_direction / mag_f(downstream_direction)
    upstream_unit = upstream_direction / mag_f(upstream_direction)

    h1_ = p1 + (upstream_unit * mag_f(r1))
    h2_ = p1 + (downstream_unit * mag_f(r2))
    
    return h1_, p1, h2_



def align_handles__vector(h1, p1, h2):
    return align_handles__general(lambda v: v.magnitude,
                                  h1, p1, h2)
    

def align_handles__array(h1, p1, h2):
    return align_handles__general(np.linalg.norm,
                                  h1, p1, h2)


def align_handle_splineSegment__vector(H1, P1, H2):
    triples = zip(H1, P1, H2)
    aligned_triples = map(lambda params: align_handles__vector(*params),
                          triples)
    aligned_splineSegments = map(list, zip(*aligned_triples))
    H1_, P1_, H2_ = list(aligned_splineSegments)
    return H1_, P1_, H2_

def align_handle_spline__vector(H1s, P1s, H2s):
    splineSegment_triples = zip(H1s, P1s, H2s)
    aligned_splineSegment_triples = map(lambda params: align_handle_splineSegment__vector(*params),
                                        splineSegment_triples)
    aligned_splines = map(list, zip(*aligned_splineSegment_triples))
    H1s_, P1s_, H2s_ = list(aligned_splines)
    return H1s_, P1s_, H2s_

def align_handle_splines__vector(splines):
    subj_splines = splines[2:-2]
    aligned_splines = splines[:2].copy()
    for i in range(len(subj_splines) // 3):
        H1, P1, H2 = subj_splines[(3*i)], subj_splines[(3*i) + 1], subj_splines[(3*i) + 2]
        H1_, P1_, H2_ = align_handle_spline__vector(H1, P1, H2)
        aligned_splines.extend([H1_, P1_, H2_])
    aligned_splines.extend(splines[-2:])
    return aligned_splines

def align_handle_splineSegment__array(H1, P1, H2):
    triples = zip(H1, P1, H2)
    aligned_triples = map(lambda params: align_handles__array(*params),
                          triples)
    aligned_splineSegments = map(list, zip(*aligned_triples))
    H1_, P1_, H2_ = list(aligned_splineSegments)
    return H1_, P1_, H2_

def align_handle_spline__array(H1s, P1s, H2s):
    splineSegment_triples = zip(H1s, P1s, H2s)
    aligned_splineSegment_triples = map(lambda params: align_handle_splineSegment__array(*params),
                                        splineSegment_triples)
    aligned_splines = map(list, zip(*aligned_splineSegment_triples))
    H1s_, P1s_, H2s_ = list(aligned_splines)
    return H1s_, P1s_, H2s_

def align_handle_splines__array(splines):
    subj_splines = splines[2:-2]
    aligned_splines = splines[:2].copy()
    for i in range(len(subj_splines) // 3):
        H1, P1, H2 = subj_splines[(3*i)], subj_splines[(3*i) + 1], subj_splines[(3*i) + 2]
        H1_, P1_, H2_ = align_handle_spline__array(H1, P1, H2)
        aligned_splines.extend([H1_, P1_, H2_])
    aligned_splines.extend(splines[-2:])
    return aligned_splines




def rotate_bezier_point_position(bezier_ob, n):
        
    node_indices = list(range(
        len(list(bezier_ob.data.splines[0].bezier_points))))

    coos = list(map(lambda i: get_spline_node_handles(bezier_ob, i),
                    node_indices)).copy()


    new_indices = list(map(lambda i: rotate_index(len(coos), i, n),
                           node_indices))


    for i in node_indices:

        bp = bezier_ob.data.splines[0].bezier_points[i]
        
        up, core, down = coos[new_indices[i]]
        bp.co = core
        bp.handle_right = down
        bp.handle_left = up

def rotate_bezier_point_position__forward__from_selected(context):
    for bezier_object in context.selected_objects:
        rotate_bezier_point_position(bezier_object, 1)

def rotate_bezier_point_position__backward__from_selected(context):
    for bezier_object in context.selected_objects:
        rotate_bezier_point_position(bezier_object, -1)


class RotateSelectedBezierPointPositionForward(bpy.types.Operator):
    """Rotates the points forward, useful when dealing with cyclic bezier objects"""
    bl_idname = "object.rotate_bezier_point_position__forward__from_selected"
    bl_label = "Rotate Selected Bezier Point Position Forward"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rotate_bezier_point_position__forward__from_selected(context)
        return {'FINISHED'}

class RotateSelectedBezierPointPositionBackward(bpy.types.Operator):
    """Rotates the points backward, useful when dealing with cyclic bezier objects"""
    bl_idname = "object.rotate_bezier_point_position__backward__from_selected"
    bl_label = "Rotate Selected Bezier Point Position Backward"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rotate_bezier_point_position__backward__from_selected(context)
        return {'FINISHED'}



operator_data = []

operator_data.append({
    'class': RotateSelectedBezierPointPositionForward,
    'keymap': 'BACK_SLASH',
    'ctrl': False,
    'alt': True,
    'shift': True
})
operator_data.append({
    'class': RotateSelectedBezierPointPositionBackward,
    'keymap': 'QUOTE',
    'ctrl': False,
    'alt': True,
    'shift': True
})






if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    spline = [
        np.array([0, 0]),
        np.array([0.1, 0.9]),
        np.array([1.2, 0.1]),
        np.array([2, 0]),
        np.array([2.5, 0.3]),
        np.array([3.9, 0.8]),
        np.array([4, 0]),
        np.array([4.1, 0.9]),
        np.array([5.9, 0.8]),
        np.array([6, 0]),
        np.array([6.1, 0.9]),
        np.array([7.9, 0.8]),
        np.array([9, 0])
    ]


    plt.scatter(list(map(lambda p: p[0], spline)),
                list(map(lambda p: p[1], spline)),
                color='b')

    subject_spline = spline[2:-2].copy()


    aligned = spline[:2].copy()
    for i in range(len(subject_spline) // 3):
        h1, p1, h2 = subject_spline[(3*i)], subject_spline[(3*i)+1], subject_spline[(3*i)+2]
        aligned.extend(align_handles__array(h1, p1, h2))
    aligned.extend(spline[-2:])


    plt.scatter(list(map(lambda p: p[0], aligned)),
                list(map(lambda p: p[1], aligned)),
                color='r')


    plt.show()
    
    
