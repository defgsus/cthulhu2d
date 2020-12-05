
from .parameterized import Parameterized


class EngineObject(Parameterized):

    engine_object_classes = dict()

    def __init__(self, **nothing_yet):
        super().__init__()
        from .engine import Engine
        self._engine: Engine = None
        meta_info = self.engine_object_classes[self.__class__]
        self._id = f"{meta_info['id']}-{meta_info['counter']}"
        meta_info["counter"] += 1

    def __init_subclass__(cls, **kwargs):
        class_name = cls.__name__
        class_short_name = "".join(filter(lambda c: c.isupper(), class_name))
        while any(filter(lambda c: c["id"] == class_short_name, EngineObject.engine_object_classes.values())):
            class_short_name += "1"

        EngineObject.engine_object_classes[cls] = {
            "name": cls.__name__,
            "id": class_short_name,
            "counter": 0,
        }

    def to_dict(self):
        return {
            **super().to_dict(),
            "id": self.id,
        }

    @property
    def id(self):
        return self._id

    @property
    def engine(self):
        return self._engine

    def on_engine_attached(self):
        pass

    def on_engine_detached(self):
        pass
