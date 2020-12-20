import math
import time

from tqdm import tqdm

from src.evo.polynomial import Polynomial, Periodic
from src.evo.pool import Pool, Phenotype
from src.evo.params import FloatParameters, ParametersGroup
from src.util.timer import Timer
from src.util.textplot import print_curve


class PolyPhenotype6(Phenotype):

    def __init__(self, target_func):
        super().__init__()
        self.target_func = target_func
        self._poly = None
        self._params_to_apply = None

    def copy(self):
        return PolyPhenotype6(self.target_func)

    def start_trial(self):
        self._poly = Polynomial(degree=6)
        if self._params_to_apply:
            self._poly.coefficients = list(self._params_to_apply.coeff.values)
            self._params_to_apply = None

    def finish_trial(self):
        pass#self._poly = None

    def get_parameters(self):
        return ParametersGroup(
            coeff=FloatParameters(self._poly.coefficients, min=-20, max=20),
        )

    def set_parameters(self, params):
        self._params_to_apply = params

    def evaluate(self):
        error = 0.
        for i in range(100):
            t = i / 99
            error += math.pow(self._poly(t) - self.target_func(t), 2)
        return -math.sqrt(error) / 100


def sin_func(t: float):
    return math.sin(t * math.pi * 2.)


def cos_func(t: float):
    return math.cos(t * math.pi * 2.)


crazy_array = [3, 0, 1, 3, 0, 2, 1, 3]

def crazy_func(t: float):
    idx = int(t * len(crazy_array) + .5)
    idx = max(0, min(len(crazy_array) - 1, int(idx)))
    return crazy_array[idx]


if __name__ == "__main__":

    #target_func = sin_func
    target_func = cos_func
    #target_func = crazy_func

    max_mutation_amount = .5

    pool = Pool(max_population=30)
    for i in range(pool.max_population):
        pool.add_phenotype(PolyPhenotype6(target_func))

    num_steps = 10000
    with Timer(num_steps) as timer:
        try:
            for i in tqdm(range(num_steps)):
                pool.mutation_amount = max_mutation_amount * (1. - i / num_steps)
                #print(f"--- gen {i+1} / pool '{pool.pool_id}' / mut {round(pool.mutation_amount, 5)} ---")
                pool.step()
                print(f"--- gen {i+1} / pool '{pool.pool_id}' / mut {round(pool.mutation_amount, 5)} ---")
                pool.dump()
        except KeyboardInterrupt:
            pass

    #pool.evaluate()
    #pool.dump()
    print(f"\n best phenotype in {pool.generations}. generation:")
    print(pool.phenotypes[0].get_parameters())
    print(f"pool_id '{pool.pool_id}'")
    timer.print()

