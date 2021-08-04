
import numpy as np



import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)


from bezier.implementation import bezier_curve_f__sym, bezier_curve_f__num
from bezier.implementation import bezier_curve_diff_f__sym, bezier_curve_diff_f__num
from bezier.implementation import bezier_curve_diff2_f__sym, bezier_curve_diff2_f__num
from bezier.implementation import bezier_curve_diff_domain_mapping_f__sym, bezier_curve_diff_domain_mapping_f__num


def normalize(xs):
    return xs / xs.max()


def bezier_discrete_uniform__sym(n, p0, h0, h1, p1):
    ps = [p0, h0, h1, p1]
    q = 1/n
    xs = np.arange(0, 1+q, q)
    coos = list(map(bezier_curve_f__sym(ps),
                    xs))
    diffs = list(map(bezier_curve_diff_f__sym(ps),
                     xs))
    diff2s = list(map(bezier_curve_diff2_f__sym(ps),
                      xs))
    return coos, diffs, diff2s

def bezier_discrete_uniform__num(n, p0, h0, h1, p1):
    ps = [p0, h0, h1, p1]
    q = 1/n
    xs = np.arange(0, 1+q, q)
    coos = list(map(bezier_curve_f__num(ps),
                    xs))
    diffs = list(map(bezier_curve_diff_f__num(ps),
                     xs))
    diff2s = list(map(bezier_curve_diff2_f__num(ps),
                      xs))
    return coos, diffs, diff2s



def bezier_discrete_adaptive__sym(n, p0, h0, h1, p1):
    ps = [p0, h0, h1, p1]
    q = 1/n
    xs = normalize(
        np.array(list(map(bezier_curve_diff_domain_mapping_f__sym(ps),
                          np.arange(0, 1+q, q)))))
    coos = list(map(bezier_curve_f__sym(ps),
                    xs))
    diffs = list(map(bezier_curve_diff_f__sym(ps),
                     xs))
    diff2s = list(map(bezier_curve_diff2_f__sym(ps),
                      xs))
    return coos, diffs, diff2s

def bezier_discrete_adaptive__num(n, p0, h0, h1, p1):
    ps = [p0, h0, h1, p1]
    q = 1/n
    xs = normalize(
        np.array(list(map(bezier_curve_diff_domain_mapping_f__num(ps),
                          np.arange(0, 1+q, q)))))
    coos = list(map(bezier_curve_f__num(ps),
                    xs))
    diffs = list(map(bezier_curve_diff_f__num(ps),
                     xs))
    diff2s = list(map(bezier_curve_diff2_f__num(ps),
                      xs))
    return coos, diffs, diff2s




if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    
    p0 = (0, 0, 0)
    h0 = (0, 1, 0)
    h1 = (1, 0, 1)
    p1 = (1, 0, 0)

    coos__uniform, diffs__uniform, diff2s__uniform = bezier_discrete_uniform__sym(32, p0, h0, h1, p1)
    coos__adaptive, diffs__adaptive, diff2s__adaptive = bezier_discrete_adaptive__sym(32, p0, h0, h1, p1)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    X = list(map(lambda x: x[0], coos__uniform))
    Y = list(map(lambda x: x[1], coos__uniform))
    Z = list(map(lambda x: x[2], coos__uniform))    
    ax.scatter(xs=X, ys=Y, zs=Z, color='b')

    X = list(map(lambda x: x[0], coos__adaptive))
    Y = list(map(lambda x: x[1], coos__adaptive))
    Z = list(map(lambda x: x[2], coos__adaptive))    
    ax.scatter(xs=X, ys=Y, zs=Z, color='r')

    plt.show()
