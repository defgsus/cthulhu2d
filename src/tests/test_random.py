import unittest
import time

from ..maps.rand import RandomXY


class TestRandom(unittest.TestCase):

    def dump_random(self, rnd: RandomXY, w=64, h=32, seed=None):
        for y in range(h):
            row = (
                int(rnd.random(x, y, seed) * 8)
                for x in range(w)
            )
            print("".join(
                f"\033[9{v}m{v}\033[0m" for v in row
            ))

    def dump_noise(self, rnd: RandomXY, w=128, h=32, scale=5, seed=None):
        for y in range(h):
            row = tuple(
                int(rnd.fractal_noise(x / scale, y / scale, seed=seed) * 8)
                for x in range(w)
            )
            #print(row)
            print("".join(
                f"\033[9{v}m{v}\033[0m" for v in row
            ))

    def test_xy(self):
        rnd = RandomXY(1)
        # rnd._pre_iter_depth = 1
        self.dump_noise(rnd)

    def test_timing(self):
        rnd = RandomXY(23)
        num_steps = 10000
        start_time = time.time()
        for i in range(num_steps):
            rnd.random(i, i, i)
        end_time = time.time()
        length = end_time - start_time
        print(f"{num_steps} random numbers took {round(length, 3)} seconds == "
              f"{int(num_steps/length)} numbers per second")


if __name__ == '__main__':
    unittest.main()
