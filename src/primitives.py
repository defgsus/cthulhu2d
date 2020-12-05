import math

import pymunk
from pymunk import Vec2d
import pyglet

from .body import Body


class Circle(Body):

    def __init__(self, position, radius, density=0):
        super().__init__(position=position, density=density, radius=radius)

    @property
    def radius(self):
        return self._parameters["radius"]

    def create_physics(self):
        shape = pymunk.Circle(self._create_body(), radius=self.radius)
        self.add_shape(shape)

        self.engine.space.add(self._body, shape)

    def create_graphics(self):
        batch = self.engine.renderer.get_permanent_batch("sprites")
        if not batch:
            return

        image = self.engine.images.centered_image("player1")
        sprite = pyglet.sprite.Sprite(image, batch=batch, subpixel=True)
        sprite.scale = self.radius * 2. / sprite.width
        self._graphics.append(sprite)

    def update_graphics(self, dt):
        if self._graphics:
            sprite = self._graphics[0]
            sprite.position = self.position
            sprite.rotation = -self.angle * 180. / math.pi


class Box(Body):

    def __init__(self, position, extent, angle=0., density=0.):
        super().__init__(position=position, angle=angle, density=density, extent=Vec2d(extent))

    @property
    def extent(self):
        return self._parameters["extent"]

    def create_physics(self):
        shape = pymunk.Poly.create_box(self._create_body(), self.extent * 2)
        self.add_shape(shape)

        self.engine.space.add(self._body, shape)

    def create_graphics(self):
        batch = self.engine.renderer.get_permanent_batch("sprites")
        if not batch:
            return

        image = self.engine.images.centered_image("box1")
        sprite = pyglet.sprite.Sprite(image, batch=batch, subpixel=True)
        sprite.scale = 1. / sprite.width
        sprite.scale_x *= self.extent[0] * 2
        sprite.scale_y *= self.extent[1] * 2
        self._graphics.append(sprite)

    def update_graphics(self, dt):
        if self._graphics:
            sprite = self._graphics[0]
            sprite.position = self.position
            sprite.rotation = -self.angle * 180. / math.pi
