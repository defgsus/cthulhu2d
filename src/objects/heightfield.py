import math

import pymunk
from pymunk import Vec2d, autogeometry

import pyglet
from pyglet import gl

from .body import Body


class Heightfield(Body):

    def __init__(self, position, extent, height_func, num_samples=10, amount=.5, **parameters):
        super().__init__(position=position, **parameters)
        self.extent = Vec2d(extent)
        self.height_func = height_func
        self.num_samples = num_samples
        self.amount = amount
        self.coordinates = tuple()
        self._sample_height_func()

    def iter_points(self):
        yield from self.coordinates
        yield self.extent * (1, -1)
        yield self.extent * (-1, -1)

    def create_physics(self):
        body = self._create_body()
        shapes = []
        bottom = -self.extent.y
        for p1, p2 in zip(self.coordinates, self.coordinates[1:]):
            shape = pymunk.Poly(
                body, [(p1.x, bottom), p1, p2, (p2.x, bottom)]
            )
            shapes.append(self.add_shape(shape))

        self.engine.space.add(body, *shapes)

    def on_sprite_created(self, sprite):
        sprite.scale *= 1. / sprite.width
        sprite.scale_x *= self.extent[0] * 2
        sprite.scale_y *= self.extent[1] * 2

    def _sample_height_func(self):
        coords = []
        width, height = self.extent.x * 2, self.extent.y * 2
        for t in self._iter_t():
            value = self.height_func(t)
            value = self.amount * value + (1. - self.amount)
            pos = -self.extent + (t * width, value * height)
            coords.append(pos)
        self.coordinates = tuple(coords)

    def _iter_t(self):
        for i in range(self.num_samples):
            yield i / (self.num_samples - 1)
