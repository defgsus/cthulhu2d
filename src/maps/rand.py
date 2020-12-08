import random


class RandomXY:

    _primes = (
        3010349,
        16785407,
        24036583,
        2147483647,
    )

    _pre_iter_depth = 0

    def __init__(self, seed):
        """
        :param seed: int
        """
        self.seed = seed

    def random(self, x, y, seed=None):
        # return random.random()
        return self.generator(x, y, seed).random()

    def noise(self, x, y, seed=None):
        ix, iy = int(x), int(y)
        fx, fy = x - ix, y - iy
        n0 = self.generator(ix, iy, seed).random()
        n1 = self.generator(ix+1, iy, seed).random()
        n2 = self.generator(ix, iy+1, seed).random()
        n3 = self.generator(ix+1, iy+1, seed).random()

        ny1 = n0 * (1 - fx) + n1 * fx
        ny2 = n2 * (1 - fx) + n3 * fx
        return ny1 * (1 - fy) + ny2 * fy

    def fractal_noise(self, x, y, num_layers=5, amount_factor=.5, scale_factor=4, offset=(1000, 1000), seed=None):
        amount_sum = 0.
        amount = 1.
        noise_value = 0.
        for i in range(num_layers):
            noise_value += amount * self.noise(x, y, seed=seed)
            amount_sum += amount
            x *= scale_factor
            y *= scale_factor
            x += offset[0]
            y += offset[1]
            amount *= amount_factor

        return noise_value / amount_sum

    def generator(self, x, y, seed=None):
        rnd = random.Random(self._combine_seed(x, y, seed))
        for i in range(self._pre_iter_depth):
            rnd.random()
        return rnd

    def _combine_seed(self, x, y, seed=None):
        if seed is None:
            seed = 0
        seed = (self.seed * self._primes[0]) ^ (seed * self._primes[1])
        seed = seed ^ (x * self._primes[1] + y * self._primes[2])
        # print("seed", seed)
        return seed
