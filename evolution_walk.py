import math
import time

from tqdm import tqdm

from pymunk import Vec2d

from src.evo.polynomial import Polynomial
from src.evo.pool import Pool, Phenotype, PhenotypeStatistics
from src.evo.params import FloatParameters, ParametersGroup
from src.agents.player6 import AgentBase, Player6
from src.engine import Engine
from src.objects.primitives import Box
from src.util.timer import Timer
from src.util.textplot import print_curve
from src.maps.map_gen import random_heightfield


class Stats(PhenotypeStatistics):
    def __init__(self):
        self.num_frames = 0
        self.seconds = 0.
        self.num_frames_body_too_low = 0
        self.num_frames_body_too_askew = 0
        self.num_frames_feet_symmetric = 0
        self.num_frames_follow_keys = 0
        self.start_position = None
        self.last_position = None
        self.travelled_x = 0.
        self.travelled_correct_x = 0.
        self.travelled_wrong_x = 0.
        self.num_key_changes = 0
        self.max_foot_distance = 0.
        self.max_speed = 0.
        self._speed_sum = 0.

    @property
    def ratio_body_too_low(self):
        return self.num_frames_body_too_low / self.num_frames if self.num_frames else 0.

    @property
    def ratio_body_too_askew(self):
        return self.num_frames_body_too_askew / self.num_frames if self.num_frames else 0.

    @property
    def ratio_feet_symmetric(self):
        return self.num_frames_feet_symmetric / self.num_frames if self.num_frames else 0.

    @property
    def ratio_follow_keys(self):
        return self.num_frames_follow_keys / self.num_frames if self.num_frames else 0.

    @property
    def average_speed(self):
        return self._speed_sum / self.num_frames if self.num_frames else 0.

    @property
    def normalized_travelled_correct_x(self):
        return self.travelled_correct_x / self.seconds if self.seconds else 0.

    @property
    def normalized_travelled_wrong_x(self):
        return self.travelled_wrong_x / self.seconds if self.seconds else 0.


class WalkerPhenotype(Phenotype):

    def __init__(self, AgentClass, **init_kwargs):
        super().__init__(obj=None)
        self.AgentClass = AgentClass
        self.init_kwargs = init_kwargs
        self.stats = Stats()
        self._parameters_to_apply = None

    #def __str__(self):
    #    obj_id = self.obj.id if self.obj else "-"
    #    return f"{self.__class__.__name__}/{hash(self)}/{obj_id}"

    def copy(self):
        pheno = WalkerPhenotype(self.AgentClass, **self.init_kwargs)
        pheno.pool = self.pool
        pheno.set_parameters(self.get_parameters())
        return pheno

    def get_parameters(self):
        if not self.obj:
            return self._parameters_to_apply
        return self.obj.get_evo_parameters()

    def set_parameters(self, params):
        self._parameters_to_apply = params

    def _apply_parameters(self):
        self.obj.set_evo_parameters(self._parameters_to_apply)

    def start_trial(self):
        start_pos = (self.pool.rnd.uniform(-20, 20), 1)
        self.obj = self.AgentClass(**self.init_kwargs, start_position=start_pos)
        if self._parameters_to_apply:
            self._apply_parameters()
            self._parameters_to_apply = None
        # print("START", self.obj, self.obj.position)
        self.pool.engine.add_container(self.obj)
        self.stats = Stats()
        self.stats.start_position = self.obj.position

    def finish_trial(self):
        # print("STOP", self.obj, self.obj.position)
        self.pool.engine.remove_container(self.obj)

    def update_stats(self, dt):
        body, left_foot, right_foot = self.obj.bodies[:3]

        self.stats.num_frames += 1
        self.stats.seconds += dt
        self.stats.num_key_changes = self.obj.keys.changes("left") + self.obj.keys.changes("right")

        self.stats.max_foot_distance = max(
            self.stats.max_foot_distance,
            (left_foot.position - body.position).length,
            (right_foot.position - body.position).length,
        )

        if self.obj.keys.is_down("left"):
            dir = -1
        elif self.obj.keys.is_down("right"):
            dir = 1
        else:
            dir = 0
        # print(self.obj.keys.keys_down())

        if self.stats.last_position is not None:
            travelled_x = self.obj.position.x - self.stats.last_position.x

            speed = abs(travelled_x) / dt
            self.stats.max_speed = max(self.stats.max_speed, speed)
            self.stats._speed_sum += speed

            self.stats.travelled_x += abs(travelled_x)
            if self.obj.keys.is_down("left"):
                if travelled_x < 0:
                    self.stats.travelled_correct_x -= travelled_x
                else:
                    self.stats.travelled_wrong_x += travelled_x
                self.stats.num_frames_follow_keys += 1
            elif self.obj.keys.is_down("right"):
                if travelled_x > 0:
                    self.stats.travelled_correct_x += travelled_x
                else:
                    self.stats.travelled_wrong_x -= travelled_x
                self.stats.num_frames_follow_keys += 1
            #else:
            #    if abs(travelled_x) < dt * .1:

        self.stats.last_position = Vec2d(self.obj.position)

        if body.position.y < .5:
            self.stats.num_frames_body_too_low += 1

        if abs(body.angle) > math.radians(10):
            self.stats.num_frames_body_too_askew += 1

        s1 = left_foot.position.x < body.position.x
        s2 = right_foot.position.x < body.position.x
        if s1 ^ s2:
            self.stats.num_frames_feet_symmetric += 1

    def evaluate(self):
        penalty = 0

        if self.stats.max_foot_distance > .7:
            penalty += 10 * (self.stats.max_foot_distance - .7)

        if self.stats.ratio_body_too_low > .02:
            penalty += 100 * math.pow(self.stats.ratio_body_too_low, 2)

        if self.stats.ratio_body_too_askew > .1:
            penalty += 10 * math.pow(self.stats.ratio_body_too_askew - .1, 2)

        if self.stats.ratio_feet_symmetric < .7:
            penalty += 1 + 100 * (.7 - self.stats.ratio_feet_symmetric)

        penalty += 20. * pow(self.stats.normalized_travelled_wrong_x, 2)

        if self.stats.average_speed >= 4. or self.stats.max_speed > 5.:
            penalty += 1000.

        fitness = 10. * self.stats.normalized_travelled_correct_x

        fitness += self.stats.average_speed

        return fitness - penalty
        #return (self.stats.last_position - self.stats.start_position).x - penalty


class EnginePool(Pool):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = Engine()
        #self.engine.add_body(Box((0, -1), (100000, 1)))
        self.engine.add_body(random_heightfield())

    def print_num_bodies(self):
        print("Engine bodies", len(self.engine.container.bodies), "pymunk", len(self.engine.space.bodies))

    def run_trial(self):
        if self.generations == 0 and False:
            print("RANDOMIZING "*5)
            for p in self.phenotypes:
                p.obj.randomize()

        self.print_num_bodies()
        num_seconds = self.rnd.uniform(10, 15)
        dt = 1. / 60.
        seconds = 0.
        pheno_key_sequences = {
            pheno: self.get_key_sequence_fixed(num_seconds)
            for pheno in self.phenotypes
        }
        while seconds < num_seconds:
            self.engine.update(dt)

            for pheno in self.phenotypes:
                key_sequence = pheno_key_sequences[pheno]

                while key_sequence and seconds >= key_sequence[0][0]:
                    keys = key_sequence[0][1]
                    for key, down in keys.items():
                        pheno.obj.keys.set_key_down(key, down)
                    key_sequence.pop(0)

                pheno.update_stats(dt)

            seconds += dt

    def finish_trial(self):
        self.engine.update(1/60.)

    def record_snapshot(self):
        super().record_snapshot()
        print(self.phenotypes[0].stats)

    def get_key_sequence_fixed(self, seconds, num_keys=None):
        left, right = "left", "right"
        if self.rnd.randint(0, 1):
            left, right = right, left
            
        fixed_keys = [
            (.1, left),
            (.3, None),
            (.4, right),
            (.7, None),
            (.8, left),
            (.9, right),
        ]
        seq = []
        for second, key in fixed_keys:
            last_keys = seq[-1][1] if seq else {}

            new_keys = {
                key: False
                for key in last_keys
                if last_keys[key]
            }
            if key:
                new_keys.update({key: True})
            second += self.rnd.uniform(-.05, .05)
            seq.append((second * seconds, new_keys))
        return seq

    def get_key_sequence(self, seconds, num_keys, start_second=1.):
        exclusive_keys = ("left", "right")
        seq = [] #(0., {key: False for key in exclusive_keys})]
        second = start_second
        while second <= seconds:
            key = self.rnd.choice(exclusive_keys)
            last_keys = seq[-1][1] if seq else {}

            if any(last_keys.values()):
                if self.rnd.randint(0, num_keys) == 0:
                    key = None

            new_keys = {
                key: False
                for key in last_keys
                if last_keys[key]
            }
            if key:
                new_keys.update({key: True})
            seq.append((second, new_keys))

            dt = (seconds - start_second) / num_keys
            second += self.rnd.uniform(dt * .6, dt * 1.4)
        return seq


def main():
    # print(Stats()); exit()
    pool = EnginePool(
        max_population=30,
        mutation_prob=0.2,
    )
    max_mutation_amount = .5
    
    #for row in pool.get_key_sequence_fixed(10, 4):
    #    print(row)
    #exit()
    for i in range(pool.max_population):
        pool.add_phenotype(WalkerPhenotype(Player6))

    # pool.randomize_all(1, 1)

    num_steps = 1000
    with Timer(num_steps) as timer:
        try:
            for i in tqdm(range(num_steps)):
                pool.mutation_amount = max_mutation_amount * (1. - i / num_steps)
                pool.step()
                print(f"--- gen {i+1} / pool '{pool.pool_id}' / mut {round(pool.mutation_amount, 5)} ---")
                #pool.dump()
        except KeyboardInterrupt:
            # pool.evaluate()
            print()
    #pool.evaluate()
    pool.dump_snapshot()
    print()
    #pool.snapshot[0]["parameters"].save_json("best.json")
    #pool.phenotypes[0].obj.dump()
    print(f"\n best phenotype in {pool.generations}. generation:")
    print(pool.phenotypes[0].get_parameters())
    print(f"pool_id '{pool.pool_id}'")
    timer.print()


if __name__ == "__main__":
    main()
