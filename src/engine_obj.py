
from .parameterized import Parameterized


class EngineObject(Parameterized):
    def __init__(self, **parameters):
        super().__init__(**parameters)
        self._engine = None

    @property
    def engine(self):
        return self._engine

    def on_engine_attached(self):
        pass

    def on_engine_detached(self):
        pass

