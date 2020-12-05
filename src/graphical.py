from .engine_obj import EngineObject


class Graphical(EngineObject):

    def __init__(self, **parameters):
        super().__init__(**parameters)
        self._graphics = []

    def create_graphics(self):
        pass

    def destroy_graphics(self):
        for g in self._graphics:
            g.delete()
        self._graphics = []

    def update_graphics(self, dt):
        pass

    def render_graphics(self):
        pass
