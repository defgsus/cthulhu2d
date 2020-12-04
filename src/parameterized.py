

class Parameterized:

    def __init__(self, **parameters):
        self._parameters = parameters

    def get_parameter(self, name):
        return self._parameters.get(name)
