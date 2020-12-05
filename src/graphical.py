import math
import pyglet

from .engine_obj import EngineObject
from .parameterized import Parameterized
from .image_gen import ImageGeneratorSettings


class Graphical(EngineObject):

    def __init__(self, graphic_settings=None, **parameters):
        super().__init__(**parameters)
        self.graphic_settings = graphic_settings or GraphicSettings(draw_lines=True)
        self._graphics = []

    def create_graphics(self):
        """Default implementation create a sprite if configured in graphics_settings"""
        if self.graphic_settings.draw_sprite:
            sprite = self.graphic_settings.create_sprite(self.engine)
            if sprite:
                self.on_sprite_created(sprite)
                self._graphics.append(sprite)

    def destroy_graphics(self):
        for g in self._graphics:
            g.delete()
        self._graphics = []

    def update_graphics(self, dt):
        """
        Default implementation updates the sprites with position and angle, if present
        """
        if hasattr(self, "position"):
            if self.graphic_settings.draw_sprite and self._graphics:
                sprite = self._graphics[0]
                sprite.position = self.position
                if hasattr(self, "angle"):
                    sprite.rotation = -self.angle * 180. / math.pi

    def render_graphics(self):
        """Default function renders lines along iter_world_points(), if present"""
        from .constraints import Constraint
        if hasattr(self, "iter_world_points"):
            if self.graphic_settings.draw_lines:
                batch: pyglet.graphics.Batch = self.engine.renderer.get_batch(self.graphic_settings.line_batch_name)
                if batch:
                    #if isinstance(self, Constraint):
                    #    print("RENDCON", list(self.iter_world_points()))
                    self.engine.renderer.draw_lines(batch, self.iter_world_points())

    def on_sprite_created(self, sprite):
        """Called by default implementation of create_graphics() if 'draw_sprite' is enabled in graphics_settings"""
        pass


class GraphicSettings(Parameterized):
    def __init__(
            self,
            draw_lines=True,
            draw_sprite=False,
            image_name=None,
            image_alignment="center",
            image_batch_name="sprites",
            line_batch_name="lines",
    ):
        super().__init__()
        self.draw_lines = draw_lines
        self.draw_sprite = draw_sprite
        self.image_name = image_name
        self.image_alignment = image_alignment
        self.image_batch_name = image_batch_name
        self.line_batch_name = line_batch_name

    def get_image(self, engine):
        if not self.image_name:
            return None

        if isinstance(self.image_name, ImageGeneratorSettings):
            image_name = self.image_name.to_uri()
        else:
            image_name = self.image_name

        if self.image_alignment == "center":
            return engine.images.centered_image(image_name)

    def create_sprite(self, engine, batch_name=None):
        batch = engine.renderer.get_permanent_batch(batch_name or self.image_batch_name)
        if not batch:
            return

        image = self.get_image(engine)
        if not image:
            return

        sprite = pyglet.sprite.Sprite(image, batch=batch, subpixel=True)
        return sprite
