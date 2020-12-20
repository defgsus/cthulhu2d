import random
import datetime
import uuid
import time

from ..engine import Engine
from ..util import make_json_compatible


class Phenotype:

    def __init__(self):
        self.pool: Pool = None
        self.stats = PhenotypeStatistics()
        self.phenotype_id = None

    def __str__(self):
        para = self.get_parameters()
        name = para.to_name() if para else "-"
        hash = para.to_hash() if para else "-"
        return f"{self.__class__.__name__}/{hash}/{name}"

    def copy(self):
        raise NotImplementedError

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


class PhenotypeStatistics:

    def to_dict(self):
        return {
            key: getattr(self, key)
            for key in dir(self)
            if not key.startswith("_") and not callable(getattr(self, key))
        }

    def __str__(self):
        return "\n".join(
            f"{key} = {value}"
            for key, value in self.to_dict().items()
        )


class Pool:

    def __init__(
            self,
            max_population=10,
            num_keep=1,
            num_reproduce=0.3,
            num_reproduce_elastic=100,
            mutation_prob=0.3,
            mutation_amount=1.,
            export_elastic=True,
            seed=None
    ):
        self.pool_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.max_population = max_population
        self.num_keep = num_keep
        self.num_reproduce = num_reproduce
        self.num_reproduce_elastic = num_reproduce_elastic
        self.mutation_prob = mutation_prob
        self.mutation_amount = mutation_amount
        self.export_elastic = export_elastic
        self.phenotypes = []
        self.rnd = random.Random(seed)
        self.engine = Engine()
        self._pheno_fitness = dict()
        self._last_snapshot = None
        self._last_elastic_snapshot_time = time.time()
        self.generations = 0
        self.phenotype_counter = 0
        #self._randomize_all_request = False

    def add_phenotype(self, phenotype):
        self.phenotypes.append(phenotype)
        phenotype.pool = self
        phenotype.phenotype_id = f"{self.pool_id}-{self.phenotype_counter}"
        self.phenotype_counter += 1

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
                params = s["phenotype"].get_parameters()
                print(f"rank {i:3}, fitness {round(s['fitness'], 3):3}, params {params}")

    def step(self):
        if not self._pheno_fitness:
            self.evaluate()

        backup = self.phenotypes
        try:
            self.next_generation()
            self._pheno_fitness = None
        except KeyboardInterrupt:
            self.phenotypes = backup
            raise

        self.evaluate()
        self.generations += 1

    def _randomize_parameters(self, params):
        params.randomize(self.rnd, self.mutation_prob, self.mutation_amount)

    def next_generation(self):
        num_keep = self.num_keep
        if isinstance(num_keep, float):
            num_keep = int(len(self.phenotypes) * num_keep + 1)
        num_reproduce = self.num_reproduce
        if isinstance(num_reproduce, float):
            num_reproduce = int(len(self.phenotypes) * num_reproduce + 1)

        phenos = self.phenotypes
        self.phenotypes = []

        for p in phenos[:num_keep]:
            self.phenotypes.append(p.copy())
            self.phenotypes[-1].set_parameters(p.get_parameters())
            self.phenotypes[-1].phenotype_id = p.phenotype_id
        # self.phenotypes = [p.copy() for p in reproducible[:num_keep]]

        reproducible_params = [p.get_parameters() for p in phenos[:num_reproduce]]
        if self.num_reproduce_elastic:
            elastic_params = self.load_elastic_phenotype_params(
                phenos[0].__class__.__name__,
                self.num_reproduce_elastic,
            )
            for param_dict in elastic_params:
                params = phenos[0].get_parameters()
                params.from_dict(param_dict)
                reproducible_params.append(params)

        while len(self.phenotypes) <= self.max_population:
            source_params = self.rnd.choice(reproducible_params).copy()

            self._randomize_parameters(source_params)

            new_pheno = phenos[0].copy()
            new_pheno.set_parameters(source_params)
            self.add_phenotype(new_pheno)

    def record_snapshot(self):
        snapshot = []
        for pheno in self.phenotypes:
            snapshot.append({
                "fitness": self.fitness(pheno),
                "phenotype": pheno,
            })
        self._last_snapshot = snapshot
        cur_time = time.time()
        if self.export_elastic and cur_time - self._last_elastic_snapshot_time > 5.:
            self._export_snapshot_elastic(snapshot)
            self._last_elastic_snapshot_time = cur_time

    def _export_snapshot_elastic(self, snapshot):
        from .es import EsPhenotype
        EsPhenotype.init()
        for i, data in enumerate(snapshot):
            pheno = data["phenotype"]
            params = pheno.get_parameters()
            obj = EsPhenotype(
                pool_id=self.pool_id,
                pool_generation=self.generations,
                pool_size=len(snapshot),
                rank=i + 1,
                fitness=data["fitness"],
                phenotype=pheno.__class__.__name__,
                phenotype_id=pheno.phenotype_id,
                name=params.to_name(),
                param=make_json_compatible(params.to_dict()),
                param_hash=params.to_hash(),
                stats=make_json_compatible(pheno.stats.to_dict()),
            )
            obj.save()

    def _randomize_all(self, prob=None, amount=None):
        prob = self.mutation_prob if prob is None else prob
        amount = self.mutation_amount if amount is None else amount
        for pheno in self.phenotypes:
            params = pheno.get_parameters()
            params.randomize(self.rnd, prob, amount)

    def load_elastic_phenotype_params(self, phenotype, count):
        from .es import EsPhenotype
        s = EsPhenotype.search()
        s = s.query("match", phenotype=phenotype)

        s.aggs.bucket("param_hash", "terms", field="param_hash", size=count, order={"fitness": "desc"}) \
            .metric("fitness", "avg", field="fitness") \
            .metric("top", "top_hits", size=1)

        response = s.execute()
        params = [tag.top.hits.hits[0]._source.param.to_dict() for tag in response.aggs.param_hash.buckets]

        return params

