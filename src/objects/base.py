
from ..parameterized import Parameterized


class EngineObject(Parameterized):

    engine_object_classes = dict()

    def __init_subclass__(cls, **kwargs):
        class_name = cls.__name__
        class_short_name = get_class_short_name(class_name)

        EngineObject.engine_object_classes[cls] = {
            "name": cls.__name__,
            "id": class_short_name,
            "counter": 0,
        }

    def __init__(self, user_data=None):
        from ..engine import Engine
        super().__init__()

        self._engine: Engine = None
        self._engine_callbacks = dict()
        self._parent_container = None
        self._user_data = user_data

        meta_info = self.engine_object_classes[self.__class__]
        self._id = f"{meta_info['id']}-{meta_info['counter']}"
        meta_info["counter"] += 1

    def to_dict(self):
        params = {
            **super().to_dict(),
            "id": self.id,
        }
        if self._user_data is not None:
            params["user_data"] = self._user_data
        return params

    @property
    def id(self):
        return self._id

    @property
    def engine(self):
        return self._engine

    @property
    def user_data(self):
        return self._user_data

    def has_user_data(self, key):
        """Check that user_data is a dict and that key is in there"""
        return isinstance(self._user_data, dict) and key in self._user_data

    def get_user_data(self, key, default=None):
        """Return key from user_data if it's a dict"""
        if not isinstance(self._user_data, dict):
            return default
        return self._user_data.get(key)

    def short_name(self):
        has_physics = bool(getattr(self, '_body', None))
        has_graphics = bool(getattr(self, '_graphics', None))
        s = f"{self.__class__.__name__}({self.id}"
        if has_physics or has_graphics:
            s += ", "
            if has_physics:
                s += "P"
            if has_graphics:
                s += "G"
        s += ")"
        return s

    def add_callback(self, name, cb):
        if name not in self._engine_callbacks:
            self._engine_callbacks[name] = []
        key = f"{name}-{hash(cb)}"
        self._engine_callbacks[name].append((cb, key))
        return key

    def remove_callback(self, name, cb_or_key):
        if name not in self._engine_callbacks:
            return

        for key, cb in self._engine_callbacks[name]:
            if cb[0] == cb_or_key or cb[1] == cb_or_key:
                self._engine_callbacks[name].remove(cb)
                return

    def fire_callback(self, name, *args, **kwargs):
        if name in self._engine_callbacks:
            for cb, key in self._engine_callbacks[name]:
                cb(*args, **kwargs)

    def on_engine_attached(self):
        pass

    def on_engine_detached(self):
        pass


def get_class_short_name(name):

    def _get_short_name(num_chars):
        n = ""
        num = 0
        for c in name:
            if c.isupper():
                n += c
                num = num_chars
            elif num:
                n += c
                num -= 1
        return n

    num_chars = 1
    short_name = _get_short_name(num_chars)
    while any(filter(lambda c: c["id"] == short_name, EngineObject.engine_object_classes.values())):
        num_chars += 1
        short_name = _get_short_name(num_chars)

    return short_name
