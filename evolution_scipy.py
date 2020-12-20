import math
import time

from scipy.optimize import differential_evolution, basinhopping

from src.evo.polynomial import Polynomial, print_curve
from src.util.timer import Timer


NUM_CALLS = 0

def evaluate_polynomial(args, degree, target_array):
    global NUM_CALLS
    NUM_CALLS += 1
    poly = Polynomial(degree=degree)
    poly.parameters = args
    error = 0.

    fac = 1. / (len(target_array) - 1)
    for i, target_value in enumerate(target_array):
        t = i * fac
        error += math.pow(poly(t) - target_array[i], 2)
    return math.sqrt(error) / len(args)


def optimize_polynomial_de(polynomial: Polynomial, target_func):
    target_array = tuple(
        target_func(i / 100) for i in range(101)
    )
    res = differential_evolution(
        func=evaluate_polynomial,
        bounds=[(-50, 50)] * len(poly.parameters),
        args=(polynomial.degree, target_array),
        #workers=-1,
        maxiter=100,
        popsize=15,
        mutation=.5,
        recombination=.2,
        #init="latinhypercube",
        init="random",
        updating="deferred",
    )
    print(res)
    polynomial.parameters = res.x


def optimize_polynomial_minimize(polynomial: Polynomial, target_func):
    target_array = tuple(
        target_func(i / 100) for i in range(101)
    )
    res = basinhopping(
        func=evaluate_polynomial,
        x0=polynomial.parameters,
        niter=10,
        minimizer_kwargs={
            "args": (polynomial.degree, target_array)
        }
    )
    print(res)
    polynomial.parameters = res.x


def sin_func(t: float):
    return math.sin(t * math.pi * 2.)


crazy_array = [3, 0, 1, 3, 0, 2, 1, 3]

def crazy_func(t: float):
    idx = int(t * len(crazy_array) + .5)
    idx = max(0, min(len(crazy_array) - 1, int(idx)))
    return crazy_array[idx]



def test_poly_time(poly: Polynomial, target_func):
    target_array = tuple(
        target_func(i / 99) for i in range(100)
    )
    num_calls = 10000
    with Timer(num_calls) as timer:
        for i in range(num_calls):
            evaluate_polynomial(list(range(poly.degree)), poly.degree, target_array)
    timer.print("de_polynomial")


if __name__ == "__main__":

    poly = Polynomial(degree=4)
    target_func = crazy_func

    if 0:
        print_curve(target_func)
        test_poly_time(poly, target_func); exit()
    else:
        NUM_CALLS = 0
        with Timer() as timer:
            optimize_polynomial_de(poly, target_func)
        timer.count = NUM_CALLS
        timer.print("optimize")

        poly.dump()
