

class Parameterized:

    def __init__(self, **parameters):
        self._parameters = parameters

    def get_parameter(self, *name):
        if len(name) < 1:
            return None
        elif len(name) < 2:
            return self._parameters.get(name)
        else:
            return tuple(self._parameters.get(n) for n in name)
