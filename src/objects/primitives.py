import math

import pymunk
from pymunk import Vec2d

import pyglet
from pyglet import gl

from .body import Body


class Circle(Body):

    def __init__(self, position, radius, **parameters):
        super().__init__(position=position, **parameters)
        self.radius = radius

    def iter_points(self):
        steps = 6
        for i in range(steps):
            t = i / steps * math.pi * 2
            yield Vec2d((math.sin(t), math.cos(t))) * self.radius

    def create_physics(self):
        shape = pymunk.Circle(self._create_body(), radius=self.radius)
        self.add_shape(shape)

        self.engine.space.add(self._body, shape)

    def on_sprite_created(self, sprite):
        sprite.scale *= self.radius * 2. / sprite.width


class Ngon(Body):

    def __init__(self, position, radius, segments, **parameters):
        super().__init__(position=position, **parameters)
        assert segments > 0, f"Can not use segment < 1 in {self}"
        self.radius = radius
        self.segments = segments

    def iter_points(self):
        for i in range(self.segments):
            t = i / self.segments * math.pi * 2
            yield Vec2d((math.sin(t), math.cos(t))) * self.radius

    def create_physics(self):
        shape = pymunk.Poly(self._create_body(), list(self.iter_points()))
        self.add_shape(shape)

        self.engine.space.add(self._body, shape)

    def on_sprite_created(self, sprite):
        sprite.scale *= self.radius * 2. / sprite.width


class Box(Body):

    def __init__(self, position, extent, angle=0., **parameters):
        super().__init__(position=position, angle=angle, **parameters)
        self.extent = Vec2d(extent)

    @property
    def bottom_left_extent(self):
        return -self.extent

    @property
    def bottom_right_extent(self):
        return Vec2d(self.extent.x, -self.extent.y)

    @property
    def top_left_extent(self):
        return Vec2d(-self.extent.x, self.extent.y)

    @property
    def top_right_extent(self):
        return self.extent

    def iter_points(self):
        yield self.top_left_extent
        yield self.top_right_extent
        yield self.bottom_right_extent
        yield self.bottom_left_extent

    def create_physics(self):
        shape = pymunk.Poly.create_box(self._create_body(), self.extent * 2)
        self.add_shape(shape)

        self.engine.space.add(self._body, shape)

    def on_sprite_created(self, sprite):
        sprite.scale *= 1. / sprite.width
        sprite.scale_x *= self.extent[0] * 2
        sprite.scale_y *= self.extent[1] * 2


class Trapezoid(Body):

    def __init__(self, position, width_top, width_bottom, height, angle=0., density=0.):
        super().__init__(
            position=position, angle=angle, density=density,
        )
        self.width_top = width_top
        self.width_bottom = width_bottom
        self.height = height

    @property
    def extent(self):
        return Vec2d(max(self.width_top, self.width_bottom), self.height) / 2

    @property
    def bottom_left_extent(self):
        return Vec2d(-self.width_bottom, -self.height) / 2

    @property
    def bottom_right_extent(self):
        return Vec2d(self.width_bottom, -self.height) / 2

    @property
    def top_left_extent(self):
        return Vec2d(-self.width_top, self.height) / 2

    @property
    def top_right_extent(self):
        return Vec2d(self.width_top, self.height) / 2

    def iter_points(self):
        yield self.top_left_extent
        yield self.top_right_extent
        yield self.bottom_right_extent
        yield self.bottom_left_extent

    def create_physics(self):
        shape = pymunk.Poly(self._create_body(), list(self.iter_points()))
        self.add_shape(shape)

        self.engine.space.add(self._body, shape)

    def on_sprite_created(self, sprite):
        sprite.scale *= 1. / sprite.width
        sprite.scale_x *= self.extent[0] * 2
        sprite.scale_y *= self.extent[1] * 2
