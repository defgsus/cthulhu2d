import os
import json
import warnings

PROJECT_DIR = os.path.abspath(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
)


phrases = []
for consonant in ("k", "v", "w", "b", "t", "s", "r", "f"):
    for vocal in ("a", "e", "i", "o", "u"):
        phrases.append(consonant + vocal)


class ParametersBase:

    def copy(self):
        raise NotImplementedError

    def randomize(self, rnd, prob, amount):
        raise NotImplementedError

    def to_dict(self):
        raise NotImplementedError

    def to_bytes(self):
        raise NotImplementedError

    def from_dict(self, data):
        raise NotImplementedError

    @classmethod
    def float_to_bytes(cls, f):
        s = str(round(f, 3)).encode("ascii")
        return s

    def to_name(self):
        seq = self.to_bytes()
        s = 0
        name = []
        break_point = 301
        for c in seq:
            if s >= break_point:
                name.append(phrases[(s // 5) % len(phrases)])
                if len(name) % (3 + (s // 11) % 3) == 0:
                    name.append(" ")
                    if name.count(" ") > 2:
                        break
                s -= break_point
            s += c
        return "".join(name).strip()


class FloatParameters(ParametersBase):

    def __init__(self, seq, min=None, max=None):
        self.values = list(seq)
        self.min = min
        self.max = max

    def __repr__(self):
        return repr(self.values)

    def copy(self):
        return self.__class__(self.values, min=self.min, max=self.max)

    def to_dict(self):
        return {"values": self.values, "min": self.min, "max": self.max}

    def to_bytes(self):
        return b"".join(self.float_to_bytes(f) for f in self.values)

    def from_dict(self, data):
        self.values = data["values"]
        self.min = data["min"]
        self.max = data["max"]

    def randomize(self, rnd, prob, amount):
        for i, v in enumerate(self.values):
            if rnd.uniform(0, 1) < prob:
                v = v + rnd.uniform(-amount, amount)
                if self.min is not None:
                    v = max(v, self.min)
                if self.max is not None:
                    v = min(v, self.max)
                self.values[i] = v


class FloatParameter(ParametersBase):

    def __init__(self, value, min=None, max=None):
        self.value = value
        self.min = min
        self.max = max

    def __repr__(self):
        return repr(self.value)

    def copy(self):
        return self.__class__(self.value, min=self.min, max=self.max)

    def to_dict(self):
        return {"value": self.value, "min": self.min, "max": self.max}

    def from_dict(self, data):
        self.value = data["value"]
        self.min = data["min"]
        self.max = data["max"]

    def to_bytes(self):
        return self.float_to_bytes(self.value)

    def randomize(self, rnd, prob, amount):
        if rnd.uniform(0, 1) < prob:
            v = self.value + rnd.uniform(-amount, amount)
            if self.min is not None:
                v = max(v, self.min)
            if self.max is not None:
                v = min(v, self.max)
            self.value = v


class ParametersGroup(ParametersBase):

    DATA_DIR = os.path.join(PROJECT_DIR, "pools")

    def __init__(self, **parameters):
        self.parameters = parameters

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.parameters)}"

    def copy(self):
        self.__class__(**{
            key: params.copy()
            for key, params in self.parameters.items()
        })

    def randomize(self, rnd, prob, amount):
        for params in self.parameters.values():
            params.randomize(rnd, prob, amount)

    def __getattr__(self, item):
        if item in self.parameters:
            return self.parameters[item]
        return super().__getattribute__(item)

    def to_dict(self):
        return {
            key: params.to_dict()
            for key, params in self.parameters.items()
        }

    def from_dict(self, data):
        for key in self.parameters:
            if key in data:
                self.parameters[key].from_dict(data[key])
            else:
                warnings.warn(f"Missing parameter '{key}'")

    def to_bytes(self):
        return b"".join(
            self.parameters[key].to_bytes()
            for key in sorted(self.parameters)
        )

    def save_json(self, filename):
        if not os.path.exists(self.DATA_DIR):
            os.makedirs(self.DATA_DIR)
        with open(os.path.join(self.DATA_DIR, filename), "w") as fp:
            json.dump(self.to_dict(), fp, indent=2)

    def load_json(self, filename):
        with open(os.path.join(self.DATA_DIR, filename)) as fp:
            data = json.load(fp)
        self.from_dict(data)
