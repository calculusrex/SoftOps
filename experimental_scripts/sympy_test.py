import bpy
import bmesh
import numpy as np
from mathutils import Vector

import sympy as sp


def plot_curve(context, expr, bounds, n_points):

    current_mode = context.active_object.mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    current_mesh = bpy.context.active_object.data
    bm = bmesh.new()
    bm.from_mesh(current_mesh)
    f = sp.lambdify(x, expr, 'numpy')
    a, b = bounds
    z_coo_vals = f(
        np.arange(a, b, (b-a)/n_points))
    for z in z_coo_vals:
        coo = Vector((0, 0, z))
        print(coo)
        bm.verts.new(coo)
    bm.to_mesh(current_mesh)
    bm.free()

    bpy.ops.object.mode_set(mode=current_mode)


if __name__ == '__main__':
    print('sympy_test.py')

    context = bpy.context
    
    x = sp.Symbol('x')

    expr = 2 * x**2 + 6 * x + 3

    plot_curve(context, expr, (0, 1), 128)
