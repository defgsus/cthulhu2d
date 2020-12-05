import pyglet

from .engine_obj import EngineObject
from .parameterized import Parameterized
from .image_gen import ImageGeneratorSettings


class Graphical(EngineObject):

    def __init__(self, graphic_settings=None, **parameters):
        super().__init__(
            graphic_settings=graphic_settings or GraphicSettings(draw_lines=True),
            **parameters,
        )
        self._graphics = []

    @property
    def graphic_settings(self):
        return self._parameters["graphic_settings"]

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


class GraphicSettings(Parameterized):
    def __init__(
            self,
            draw_lines=False,
            draw_sprite=False,
            image_name=None,
            image_alignment="center",
            image_batch_name="sprites",
    ):
        super().__init__(
            draw_lines=draw_lines,
            draw_sprite=draw_sprite,
            image_name=image_name,
            image_alignment=image_alignment,
            image_batch_name=image_batch_name,
        )

    @property
    def draw_lines(self):
        return self._parameters["draw_lines"]

    @property
    def draw_sprite(self):
        return self._parameters["draw_sprite"]

    def get_image(self, engine):
        image_name, image_alignment = self.get_parameter("image_name", "image_alignment")
        if not image_name:
            return None

        if isinstance(image_name, ImageGeneratorSettings):
            image_name = image_name.to_uri()

        if image_alignment == "center":
            return engine.images.centered_image(image_name)

    def create_sprite(self, engine, batch_name=None):
        batch = engine.renderer.get_permanent_batch(batch_name or self.get_parameter("image_batch_name"))
        if not batch:
            return

        image = self.get_image(engine)
        if not image:
            return

        sprite = pyglet.sprite.Sprite(image, batch=batch, subpixel=True)
        return sprite
