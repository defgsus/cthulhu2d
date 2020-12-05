
from .parameterized import Parameterized


class EngineObject(Parameterized):

    def __init__(self, **nothing_yet):
        super().__init__()
        from .engine import Engine
        self._engine: Engine = None

    @property
    def engine(self):
        return self._engine

    def on_engine_attached(self):
        pass

    def on_engine_detached(self):
        pass
