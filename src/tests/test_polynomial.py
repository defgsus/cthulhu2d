import unittest
import time

from ..evo.pool import Pool, Phenotype, PhenotypeStatistics
from ..evo.params import ParametersBase, ParametersGroup, FloatParameter, FloatParameters
from ..evo.polynomial import Polynomial, Periodic
from ..util.textplot import print_curve


class TestPolynomial(unittest.TestCase):

    def test_polynomial(self):
        poly = Polynomial(degree=10)
        # print_curve(poly)

    def test_periodic_func(self):
        def func(t):
            return t * t

        p = Periodic(func, period=1.)
        # print_curve(p, (-1.2, 2.2))
        self.assertEqual(1., p.period)

    def test_periodic_polynomial(self):
        p = Periodic(Polynomial(degree=10), period=.9)
        # print_curve(p, (-1.2, 2.2))
        self.assertEqual(.9, p.period)
        self.assertEqual(10, p.degree)

    def test_sin(self):
        p = Polynomial.create_sin(6)
        print_curve(p)


if __name__ == '__main__':
    unittest.main()
