

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)

from bezier.discrete import bezier_discrete_uniform__sym, bezier_discrete_adaptive__sym


just_coos = lambda xs: xs[0]


P0 = [
    (0.0, 0.0, 0.0),
    (0.0, 0.5, 0.5),
    (0.0, 3.5, 0.5),
    (0.0, 4.0, 0.0)
]

H0 = [
    (0.5, 0.0, 1.0),
    (0.5, 0.5, 1.0),
    (0.5, 3.5, -1.0),
    (0.5, 4.0, -1.0)
]

H1 = [
    (1.0, 0.0, 1.0),
    (1.0, 0.5, 1.0),
    (1.0, 3.5, -1.0),
    (1.0, 4.0, -1.0)
]

P1 = [
    (1.5, 0.0, 0.0),
    (1.5, 0.5, 0.5),
    (1.5, 3.5, 0.5),
    (1.5, 4.0, 0.0)
]

PS = [P0, H0, H1, P1]





# The parameters: P0, H0, H1, P1 represent curves which act as handles for the transversal surface
def bezier_cooss(discrete_function, n, m, P0, H0, H1, P1):

    P0_coos, P0_diffs, P0_diff2s = discrete_function(n, *P0)
    H0_coos, H0_diffs, H0_diff2s = discrete_function(n, *H0)
    H1_coos, H1_diffs, H1_diff2s = discrete_function(n, *H1)
    P1_coos, P1_diffs, P1_diff2s = discrete_function(n, *P1)

    cooss = list(map(lambda ps: just_coos(discrete_function(m, *ps)),
                     zip(P0_coos, H0_coos, H1_coos, P1_coos)))

    return cooss


def bezier_cooss__uniform__sym(n, m, P0, H0, H1, P1):
    
    return bezier_cooss(bezier_discrete_uniform__sym,
                        n, m, P0, H0, H1, P1)


def bezier_cooss__adaptive__sym(n, m, P0, H0, H1, P1):
    
    return bezier_cooss(bezier_discrete_adaptive__sym,
                        n, m, P0, H0, H1, P1)




if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    import functools as ft

    cooss = bezier_cooss__uniform__sym(32, 32, P0, H0, H1, P1)

    coos = ft.reduce(lambda xs0, xs1: xs0 + xs1,
                     cooss)
        
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    X = list(map(lambda x: x[0], coos))
    Y = list(map(lambda x: x[1], coos))
    Z = list(map(lambda x: x[2], coos))    
    ax.scatter(xs=X, ys=Y, zs=Z, color='b')

    plt.show()
