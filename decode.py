import bpy
import functools as ft
import inspect

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)



def member_tree_walk(nme, obj, path, xs, depth):
    if '__' in nme or depth == 0:
        # print(ft.reduce(lambda a, b: f'{a}.{b}', path))
        return [ft.reduce(lambda a, b: f'{a}.{b}', path)]
    else:
        for name, val in inspect.getmembers(obj):
            xs.extend(member_tree_walk(name, val, path + [name], [], depth-1))
        return xs


if __name__ == '__main__':

    bone = bpy.context.active_bone

    xs = member_tree_walk('bone', bone, ['bone'], [], 3)

    patterns = ['animation', 'river']

    for x in xs:
        for p in patterns:
            if p in x:
                print(x)
    
    
