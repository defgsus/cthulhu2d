from copy import copy

PRESETS = {
    "sin": {
        6: [0.04256348350843292, 7.464552321425516, -16.138151733079347, 4.687004784879394, 9.6109750039009, -8.134031543498292, 2.5417622091845935],
    }
}


class Polynomial:

    def __init__(self, degree=3, seq=None):
        """
        A polynomial of the form
            a + bx + cx² + dx³ + ...

        :param degree: int
        :param seq: sequence of coefficients, will override degree
        """
        if seq is None:
            self.degree = degree
            self.coefficients = [1.] * (degree + 1)
        else:
            self.coefficients = list(seq)
            self.degree = len(self.coefficients) - 1

    def __call__(self, t):
        v = self.coefficients[0]
        x = t
        for p in self.coefficients[1:]:
            v += p * x
            x *= x
        return v

    def copy(self):
        return self.__class__(seq=self.coefficients)

    @classmethod
    def create_sin(cls, degree):
        return cls(seq=PRESETS["sin"][degree])


class Periodic:

    def __init__(self, func, period=1., overlap=0.1):
        """
        A wrapper to make any function/callable object periodic
        :param func: anything callable with single float argument
        :param period: float, length of period
        :param overlap: float, factor of overlapping
        """
        self._func = func
        self.period = period
        self.overlap = overlap

    def copy(self):
        return self.__class__(
            func=copy(self._func),
            period=self.period,
            overlap=self.overlap,
        )

    def __call__(self, t):
        t = t % self.period
        v = self._func(t)
        if t > self.period - self.overlap:
            f = (1. - (self.period - t) / self.overlap) / 2.
            f = smooth1(f)
            v1 = self._func(t - self.period)
            return mix(v, v1, f)
        elif t < self.overlap:
            f = t / self.overlap / 2 + .5
            f = smooth1(f)
            v1 = self._func(t + self.period)
            return mix(v1, v, f)
        else:
            return v

    def __getattr__(self, item):
        if hasattr(self._func, item):
            return getattr(self._func, item)
        return self.__getattribute__(item)


def mix(a, b, f):
    return a * (1. - f) + b * f


def smooth1(x):
    return x * x * (3. - 2. * x)


def smooth2(x):
    # https://iquilezles.org/www/articles/texture/texture.htm
    return x * x * x * (6. * x * x - 15. * x + 10.)
