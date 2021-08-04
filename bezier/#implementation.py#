import sympy as sp
import numpy as np
import functools as ft
import mpmath as mpm
from scipy.integrate import quad as integrate_quad


# from sympy.vector import Vector as VectorSym
from sympy.vector import CoordSys3D, VectorAdd



def combinations__sym(n, k):
    return sp.factorial(n) / (sp.factorial(k) * (sp.factorial(n - k)))

def non_constant_factor__sym(n, k, t):
    return combinations__sym(n, k) * t**k * (1 - t)**(n - k)


# def integral_as_quad(expr, lims):
#     var, a, b = lims
#     return scipy.integrate.quad(sp.lambdify(var, expr), a, b)




N = CoordSys3D('N')

i, j, k = N.base_vectors()

x0, x1, x2, x3 = sp.symbols('x0, x1, x2, x3')
y0, y1, y2, y3 = sp.symbols('y0, y1, y2, y3')
z0, z1, z2, z3 = sp.symbols('z0, z1, z2, z3')

X0 = x0*i + y0*j + z0*k
X1 = x1*i + y1*j + z1*k
X2 = x2*i + y2*j + z2*k
X3 = x3*i + y3*j + z3*k

XS = sp.Array([X0, X1, X2, X3])

l, m = sp.symbols('l m')

# curve = VectorAdd(sp.summation(
#     non_constant_factor__sym(3, l, m) * XS[l],
#     (l, 0, 3)))

# curve_diff = sp.diff(curve, m)

mag_expression = lambda x0, x1, x2, x3, y0, y1, y2, y3, z0, z1, z2, z3: lambda m: np.sqrt((-3*m**2*x2 + 3*m**2*x3 + 3*m*x1*(2*m - 2) + 6*m*x2*(1 - m) - 3*x0*(1 - m)**2 + 3*x1*(1 - m)**2)**2 + (-3*m**2*y2 + 3*m**2*y3 + 3*m*y1*(2*m - 2) + 6*m*y2*(1 - m) - 3*y0*(1 - m)**2 + 3*y1*(1 - m)**2)**2 + (-3*m**2*z2 + 3*m**2*z3 + 3*m*z1*(2*m - 2) + 6*m*z2*(1 - m) - 3*z0*(1 - m)**2 + 3*z1*(1 - m)**2)**2)

# mag_expression = curve_diff.magnitude()




def bezier_curve_matrix__symbolic_P(P):
    n = len(ps) - 1
    i, t = sp.symbols('i t')
    N = CoordSys3D('N')
    a, b, c  = N.base_vectors()
    return t, VectorAdd(
        sp.summation(
            non_constant_factor__sym(n, i, t) * P[i],
            (i, 0, n)
        )
    ).to_matrix(N)


def bezier_curve_vectorAdd__symbolic_P(P):
    n = len(ps) - 1
    i, t = sp.symbols('i t')
    N = CoordSys3D('N')
    a, b, c  = N.base_vectors()
    return t, VectorAdd(
        sp.summation(
            non_constant_factor__sym(n, i, t) * P[i],
            (i, 0, n)
        )
    )





def bezier_curve__sym(ps):
    n = len(ps) - 1
    i, t = sp.symbols('i t')
    N = CoordSys3D('N')
    a, b, c  = N.base_vectors()
    P = sp.Array(
        list(map(lambda p: p[0]*a + p[1]*b + p[2]*c, ps))
    )
    return t, VectorAdd(
        sp.summation(
            non_constant_factor__sym(n, i, t) * P[i],
            (i, 0, n)
        )
    ).to_matrix(N)




def bezier_curve_vectorAdd__sym(ps):
    n = len(ps) - 1
    i, t = sp.symbols('i t')
    N = CoordSys3D('N')
    a, b, c  = N.base_vectors()
    P = sp.Array(
        list(map(lambda p: p[0]*a + p[1]*b + p[2]*c, ps))
    )
    return t, VectorAdd(
        sp.summation(
            non_constant_factor__sym(n, i, t) * P[i],
            (i, 0, n)
        )
    )



def bezier_curve_summation__sym(ps):
    n = len(ps) - 1
    i, t = sp.symbols('i t')
    N = CoordSys3D('N')
    a, b, c  = N.base_vectors()

    p0, p1, p2, p3 = sp.symbols('p0 p1 p2 p3')

    P = sp.Array([p0, p1, p2, p3])

    return t, sp.summation(
        non_constant_factor__sym(n, i, t) * P[i],
        (i, 0, n)
    )



def bezier_curve_f__sym(ps):
    t, R = bezier_curve__sym(ps)
    lamb = sp.lambdify(t, R.transpose(), 'numpy')
    return lambda x: lamb(x)[0]

def bezier_curve_f__num(ps):
    p0, p1, p2, p3 = ps
    
    def curve_f(t):
        factors = [
            (1 - t)**3,
            3 * t * (1 - t)**2,
            3 * t**2 * (1 - t),
            t**3
        ]
        return ft.reduce(lambda a, b: a + b,
                         map(np.prod, zip(factors, ps)))

    return curve_f



        


def bezier_curve_diff_f__sym(ps):
    t, R = bezier_curve__sym(ps)
    dR_dt = sp.diff(R, t)
    lamb = sp.lambdify(t, dR_dt.transpose(), 'numpy')
    return lambda x: lamb(x)[0]


def bezier_curve_diff_f__num(ps):
    p0, p1, p2, p3 = ps
    
    def curve_f(t):
        factors = [
            -3 * (1 - t)**2,
            3 * t * (2*t - 2) + 3 * (1 - t)**2,
            -3 * t**2 + 6 * t * (1 - t),
            3 * t**2
        ]
        return ft.reduce(lambda a, b: a + b,
                         map(np.prod, zip(factors, ps)))

    return curve_f





def bezier_curve_diff_magnitude_f__sym(ps):
    t, R = bezier_curve_vectorAdd__sym(ps)
    dR_dt = sp.diff(R, t)
    mag_expression = dR_dt.magnitude()
    lamb = sp.lambdify(t, mag_expression, 'numpy')
    return lamb

def bezier_curve_diff_magnitude_f__num(ps):
    p0, p1, p2, p3 = ps

    x0, y0, z0 = p0
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    x3, y3, z3 = p3
    
    def curve_f(t):

        term0 = -3*(t**2*x0 - 3*t**2*x1 + 3*t**2*x2 - t**2*x3 - 2*t*x0 + 4*t*x1 - 2*t*x2 + x0 - x1)
        term1 = -3*(t**2*y0 - 3*t**2*y1 + 3*t**2*y2 - t**2*y3 - 2*t*y0 + 4*t*y1 - 2*t*y2 + y0 - y1)
        term2 = -3*(t**2*z0 - 3*t**2*z1 + 3*t**2*z2 - t**2*z3 - 2*t*z0 + 4*t*z1 - 2*t*z2 + z0 - z1)
        
        return np.sqrt(term0**2 + term1**2 + term2**2)

    return curve_f





def bezier_curve_diff_domain_mapping_f__sym(ps):
    t, R = bezier_curve_vectorAdd__sym(ps)
    dR_dt = sp.diff(R, t)
    mag_expression = dR_dt.magnitude()
    lamb = lambda x: integrate_quad(sp.lambdify(t, mag_expression), 0, x)[0]
    return lamb

def bezier_curve_diff_domain_mapping_f__num(ps):

    mag_f = bezier_curve_diff_magnitude_f__num(ps)

    lamb = lambda x: integrate_quad(mag_f, 0, x)[0]

    return lamb



def bezier_curve_diff2_f__sym(ps):
    t, R = bezier_curve__sym(ps)
    d2R_dt2 = sp.diff(R, t, 2)
    lamb = sp.lambdify(t, d2R_dt2.transpose(), 'numpy')
    return lambda x: lamb(x)[0]


def bezier_curve_diff2_f__num(ps):
    p0, p1, p2, p3 = ps
    
    def curve_f(t):
        factors = [
            -(t - 1),
            t + 2 * (t - 1),
            -2 * t - (t - 1),
            t
        ]
        return 6 * ft.reduce(lambda a, b: a + b,
                             map(np.prod, zip(factors, ps)))

    return curve_f





if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    # sp.init_printing()

    ps = [
        [0, 0, 0],
        [0, 0, 1],
        [1, 1, 0],
        [1, 0, 0]
    ]

    curve__sym = bezier_curve_f__sym(ps)
    dCurve_dt__sym = bezier_curve_diff_f__sym(ps)
    d2Curve_dt2__sym = bezier_curve_diff2_f__sym(ps)
    mags_f__sym = bezier_curve_diff_magnitude_f__sym(ps)
    domain_mapping_f__sym = bezier_curve_diff_domain_mapping_f__sym(ps)
    
    curve__num = bezier_curve_f__num(
        list(map(np.array, ps)))
    dCurve_dt__num = bezier_curve_diff_f__num(
        list(map(np.array, ps)))
    d2Curve_dt2__num = bezier_curve_diff2_f__num(
        list(map(np.array, ps)))
    mags_f__num = bezier_curve_diff_magnitude_f__num(ps)
    domain_mapping_f__num = bezier_curve_diff_domain_mapping_f__sym(ps)    

    q = 1/100
    xs = np.arange(0, q+1, q)
    q2 = 1/10
    xs2 = np.arange(0, q2+1, q2)

    ys__sym = np.array(list(map(curve__sym, xs)))
    ys__num = np.array(list(map(lambda x: np.float64(curve__num(x)), xs)))

    ys__sym__diff = np.array(list(map(dCurve_dt__sym, xs)))
    ys__num__diff = np.array(list(map(lambda x: np.float64(dCurve_dt__num(x)), xs)))

    ys__sym__diff2 = np.array(list(map(d2Curve_dt2__sym, xs)))
    ys__num__diff2 = np.array(list(map(lambda x: np.float64(d2Curve_dt2__num(x)), xs)))

    mags__sym = np.array(list(map(mags_f__sym, xs)))
    mags__num = np.array(list(map(mags_f__num, xs)))

    domain_map__sym = np.array(list(map(domain_mapping_f__sym, xs)))
    domain_map__num = np.array(list(map(domain_mapping_f__num, xs)))
    
    # ys2__num = np.array(list(map(curve__num, xs2)))
    # ys2_diff__sym = np.array(list(map(dCurve_dt__sym, xs2)))
    # ys2_diff__num = np.array(list(map(lambda x: np.float32(dCurve_dt__num(x)), xs2)))
    # ys2_diff2__sym = np.array(list(map(d2Curve_dt2__sym, xs2)))
    # ys2_diff2__num = np.array(list(map(lambda x: np.float32(d2Curve_dt2__num(x)), xs2)))


    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.plot(xs=ys__sym__diff2[:,0],
            ys=ys__sym__diff2[:,1],
            zs=ys__sym__diff2[:,2],
            color='r')

    ax.scatter(xs=ys__num__diff2[:,0],
               ys=ys__num__diff2[:,1],
               zs=ys__num__diff2[:,2],
               color='b')
    
    plt.show()



    plt.plot(xs, mags__sym, color='r')
    plt.scatter(xs, mags__num, color='b')
    plt.plot(xs, domain_map__sym, color='r')
    plt.scatter(xs, domain_map__num, color='b')

    plt.show()

    # X, Y, Z, U, V, W = zip(
    #     *np.concatenate(
    #         [ys2__num, ys2_diff__num],
    #         axis=1))
    # ax.quiver(X, Y, Z, U, V, W, color='b')


    # X, Y, Z, U, V, W = zip(
    #     *np.concatenate(
    #         [ys2__num, ys2_diff__sym],
    #         axis=1))
    # ax.quiver(X, Y, Z, U, V, W, color='r', length=0.5)


    # X, Y, Z, U, V, W = zip(
    #     *np.concatenate(
    #         [ys2__num, ys2_diff2__num],
    #         axis=1))
    # ax.quiver(X, Y, Z, U, V, W, color='b')


    # X, Y, Z, U, V, W = zip(
    #     *np.concatenate(
    #         [ys2__num, ys2_diff2__sym],
    #         axis=1))
    # ax.quiver(X, Y, Z, U, V, W, color='r', length=0.5)



    # mag_f__sym = bezier_curve_diff_magnitude_f__sym(ps)
    # mag_f__num = bezier_curve_diff_magnitude_f__num(ps)
    
    # domain_mapping_f__sym = bezier_curve_diff_domain_mapping_f__sym(ps)
    # domain_mapping_f__num = bezier_curve_diff_domain_mapping_f__num(ps)

    # mags__sym = np.array(list(map(mag_f__sym, xs)))
    # mags__num = np.array(list(map(mag_f__num, xs)))
    # domain_map__sym = np.array(list(map(domain_mapping_f__sym, xs)))
    # domain_map__num = np.array(list(map(domain_mapping_f__num, xs)))
    

    # plt.show()

    # plt.plot(xs, mags__sym, color='r')
    # plt.scatter(xs, mags__num, color='b')
    # plt.plot(xs, domain_map__sym, color='k')
    # plt.plot(xs, domain_map__num, color='y')

    # plt.show()
    
