import functools as ft

# import sys
# dev_path = '/home/feral/engineering/addon_workshop/softops'
# sys.path.insert(1, dev_path)



def map_domain(f, a, b):
    span = b - a
    g = lambda x: f(((1/span) * (x - a)))
    return g

# takes a function with normalized outputs and returns one with the outputs mapped to the range between a and b
def map_output(f, a, b):
    span = b - a
    g = lambda x: (span * f(x)) + a
    return g

def invert_domain(f):
    g = lambda x: f(1-x)
    return g


def unzip(pairs):
    xs = list(map(lambda pair: pair[0],
                  pairs))
    ys = list(map(lambda pair: pair[1],
                  pairs))
    return xs, ys


def flatten_lists(xss):
    if type(xss[0]) == list:
        ys = xss[0].copy()
        for xs in xss[1:]:
            ys.extend(xs)
        return ys
    else:
        return xss


def are_all_true(booleans):
    return ft.reduce(lambda a, b: a and b,
                     booleans)

def is_one_of_them_true(booleans):
    return ft.reduce(lambda a, b: a or b,
                     booleans)


# ((a, b), c) -> (a, b, c)
def flaten__triple(xss):
    xs, z = xss
    x, y = xs
    return x, y, z
    

def reverse_list(xs):
    ys = xs.copy()
    ys.reverse()
    return ys


def list_transpose(xss):
    return list(
        map(list,
            zip(*xss)))



def preferably_second_ones(xs, maybe_ys):
    return list(map(lambda a, b: a if b == None else b,
                    zip(xs, maybe_ys)))


def maybe_first(xs):
    if len(xs) == 0:
        return None
    else:
        return xs[0]


def rotate_index(length, i, n):
    return (i - n) % length


def one_false(bools):
    return ft.reduce(lambda a, b: a or b,
                     map(lambda x: not(x),
                         bools))

def one_true(bools):
    return ft.reduce(lambda a, b: a or b,
                     bools)
    

def overlapping_pairs(xs, cyclic=False):
    ys = xs[1:]
    if cyclic:
        ys.append(xs[0])
    return list(zip(xs, ys))
  

def rotate_list(c, xs):
    n = len(xs)
    c = c % n
    xs1 = list(map(lambda i: xs[i],
                   range(c, n)))
    xs1.extend(list(map(lambda i: xs[i],
                        range(0, c))))
    return xs1



def vector_mean(vectors):
    s = ft.reduce(lambda a, b: a + b,
                  vectors)
    n = len(vectors)
    return s / n



def is_even(n):
    return n % 2 == 0

def is_odd(n):
    return n % 2 != 0


if __name__ == '__main__':
    print()
    print('utils.py')
    print()

    
    
    
