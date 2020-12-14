

class Polynomial:

    def __init__(self, degree=3, seq=None):
        """

        :param degree: int
        :param seq: sequence of coefficients, will override degree
        """
        if seq is None:
            self.degree = degree
            self.parameters = [1.] * degree
        else:
            self.parameters = list(seq)
            self.degree = len(self.parameters)

    def __call__(self, t):
        v = self.parameters[0]
        x = t
        for p in self.parameters[1:]:
            v += p * x
            x *= x
        return v

    def copy(self):
        return self.__class__(seq=self.parameters)

    def dump(self, range=(0, 1), steps=50, file=None):
        print_curve(self, range=range, steps=steps, file=file)


class PolynomialPeriod(Polynomial):

    def __init__(self, degree=3, seq=None, max=1, overlap=0.1, amplitude=1., offset=0.):
        super().__init__(degree=degree, seq=seq)
        self.max = max
        self.overlap = overlap
        self.amplitude = amplitude
        self.offset = offset

    def copy(self):
        return self.__class__(
            seq=self.parameters,
            max=self.max,
            overlap=self.overlap,
            amplitude=self.amplitude,
        )

    def __call__(self, t):
        t = t % self.max
        v = super().__call__(t)
        if t > self.max - self.overlap:
            f = (1. - (self.max - t) / self.overlap) / 2.
            f = smooth1(f)
            v1 = super().__call__(t - self.max)
            return mix(v, v1, f) * self.amplitude + self.offset
        elif t < self.overlap:
            f = t / self.overlap / 2 + .5
            f = smooth1(f)
            v1 = super().__call__(t + self.max)
            return mix(v1, v, f) * self.amplitude + self.offset
        else:
            return v * self.amplitude + self.offset


def mix(a, b, f):
    return a * (1. - f) + b * f


def smooth1(x):
    return x * x * (3. - 2. * x)


def smooth2(x):
    # https://iquilezles.org/www/articles/texture/texture.htm
    return x * x * x * (6. * x * x - 15. * x + 10.)

def print_curve(func, range=(0, 1), steps=50, file=None):
    import numpy as np
    x_values = np.linspace(range[0], range[1], steps)

    min_v = min(func(x) for x in x_values)
    max_v = max(func(x) for x in x_values)

    for x in x_values:
        v = func(x)
        width = int((v - min_v) / (max_v - min_v) * 60)
        print(f"{round(x, 3):5} {round(v, 5):8} {' ' * width}#", file=file)
