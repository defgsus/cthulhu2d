import random

from ..engine import Engine


class Phenotype:

    def __init__(self, obj):
        self.obj = obj
        self.pool: Pool = None

    def __str__(self):
        para = self.get_parameters()
        name = para.to_name() if para else "-"
        return f"{self.__class__.__name__}/{name}"

    def get_parameters(self):
        raise NotImplementedError

    def set_parameters(self, parameters):
        raise NotImplementedError

    def start_trial(self):
        pass

    def finish_trial(self):
        pass

    def evaluate(self):
        raise NotImplementedError


class Pool:

    def __init__(self, max_population=10, mutation_prob=0.3, mutation_amount=1., seed=None):
        self.max_population = max_population
        self.mutation_prob = mutation_prob
        self.mutation_amount = mutation_amount
        self.phenotypes = []
        self.rnd = random.Random(seed)
        self.engine = Engine()
        self._pheno_fitness = dict()
        self._last_snapshot = None
        self.generations = 0
        #self._randomize_all_request = False

    def add_phenotype(self, phenotype):
        self.phenotypes.append(phenotype)
        phenotype.pool = self

    def fitness(self, pheno):
        return self._pheno_fitness.get(pheno)

    @property
    def snapshot(self):
        return self._last_snapshot

    def evaluate(self):
        for pheno in self.phenotypes:
            pheno.start_trial()

        self.run_trial()

        for pheno in self.phenotypes:
            pheno.finish_trial()

        self.finish_trial()

        self._pheno_fitness = dict()
        for pheno in self.phenotypes:
            self._pheno_fitness[pheno] = pheno.evaluate()

        self.phenotypes.sort(key=lambda p: -self._pheno_fitness[p])
        self.record_snapshot()

    def run_trial(self):
        pass

    def finish_trial(self):
        pass

    def dump(self):
        max_len = max(len(str(pheno)) for pheno in self.phenotypes)
        for pheno in self.phenotypes:
            fit = self.fitness(pheno)
            fit = round(fit, 3) if fit is not None else "-"
            print(f"{str(pheno):{max_len}} {fit}")

    def dump_snapshot(self):
        if self._last_snapshot:
            for i, s in enumerate(self._last_snapshot):
                print(f"rank {i:3}, fitness {round(s['fitness'], 3):3}, params {s['parameters']}")

    def step(self):
        if not self._pheno_fitness:
            self.evaluate()

        backup = self.phenotypes
        try:
            self.next_generation_replace()
        except KeyboardInterrupt:
            self.phenotypes = backup
            raise

        self.evaluate()
        self.generations += 1

    def _randomize_parameters(self, params):
        params.randomize(self.rnd, self.mutation_prob, self.mutation_amount)

    def next_generation(self):
        num_best = 5
        best = self.phenotypes[:num_best]

        for i in range(num_best, len(self.phenotypes)):
            source_pheno = self.rnd.choice(best)

            params = source_pheno.get_parameters()
            self._randomize_parameters(params)
            self.phenotypes[i].set_parameters(params)

    def next_generation_replace(self):
        num_reproduce = len(self.phenotypes)
        num_keep = min(5, len(self.phenotypes))

        reproducible = self.phenotypes[:num_reproduce]
        self.phenotypes = [p.copy() for p in reproducible[:num_keep]]

        while len(self.phenotypes) < self.max_population:
            source_pheno = self.rnd.choice(reproducible)
            params = source_pheno.get_parameters()

            new_pheno = source_pheno.copy()
            #if self.generations < 10:
            self._randomize_parameters(params)

            new_pheno.set_parameters(params)
            self.add_phenotype(new_pheno)

        #for p in self.phenotypes:
        #    print(p.get_parameters())

    def record_snapshot(self):
        snapshot = []
        for pheno in self.phenotypes:
            snapshot.append({
                "fitness": self.fitness(pheno),
                "parameters": pheno.get_parameters(),
            })
        self._last_snapshot = snapshot

    def _randomize_all(self, prob=None, amount=None):
        prob = self.mutation_prob if prob is None else prob
        amount = self.mutation_amount if amount is None else amount
        for pheno in self.phenotypes:
            params = pheno.get_parameters()
            params.randomize(self.rnd, prob, amount)
