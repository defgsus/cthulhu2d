import math

import pymunk
from pymunk import Vec2d

import pyglet
from pyglet import gl

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
        sprite = self.graphic_settings.create_sprite(self.engine)
        if sprite:
            sprite.scale = self.radius * 2. / sprite.width
            self._graphics.append(sprite)

    def update_graphics(self, dt):
        if self._graphics:
            sprite = self._graphics[0]
            sprite.position = self.position
            sprite.rotation = -self.angle * 180. / math.pi


class Box(Body):

    def __init__(self, position, extent, angle=0., **parameters):
        super().__init__(position=position, angle=angle, extent=Vec2d(extent), **parameters)

    @property
    def extent(self):
        return self._parameters["extent"]

    @property
    def bottom_left(self):
        return self.position - self.extent

    @property
    def bottom_right(self):
        return self.position + (self.extent.x, -self.extent.y)

    @property
    def top_left(self):
        return self.position + (-self.extent.x, self.extent.y)

    @property
    def top_right(self):
        return self.position + self.extent

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

    def create_graphics(self):
        if self.graphic_settings.draw_sprite:
            sprite = self.graphic_settings.create_sprite(self.engine)
            if sprite:
                sprite.scale = 1. / sprite.width
                sprite.scale_x *= self.extent[0] * 2
                sprite.scale_y *= self.extent[1] * 2
                self._graphics.append(sprite)

    def update_graphics(self, dt):
        if self.graphic_settings.draw_sprite and self._graphics:
            sprite = self._graphics[0]
            sprite.position = self.position
            sprite.rotation = -self.angle * 180. / math.pi

    def render_graphics(self):
        if self.graphic_settings.draw_lines:
            batch: pyglet.graphics.Batch = self.engine.renderer.get_batch("lines")
            if batch:
                self.engine.renderer.draw_lines(batch, self.iter_world_points())


class Trapezoid(Body):

    def __init__(self, position, width_top, width_bottom, height, angle=0., density=0.):
        super().__init__(
            position=position, angle=angle, density=density, 
            width_top=width_top,
            width_bottom=width_bottom,
            height=height,
        )

    @property
    def extent(self):
        return Vec2d(max(self.width_top, self.width_bottom), self.height) / 2

    @property
    def width_top(self):
        return self._parameters["width_top"]

    @property
    def width_bottom(self):
        return self._parameters["width_bottom"]

    @property
    def height(self):
        return self._parameters["height"]

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

    def create_graphics(self):
        if self.graphic_settings.draw_sprite:
            sprite = self.graphic_settings.create_sprite(self.engine)
            if sprite:
                sprite.scale = 1. / sprite.width
                sprite.scale_x *= self.extent[0] * 2
                sprite.scale_y *= self.extent[1] * 2
                self._graphics.append(sprite)

    def update_graphics(self, dt):
        if self.graphic_settings.draw_sprite and self._graphics:
            sprite = self._graphics[0]
            sprite.position = self.position
            sprite.rotation = -self.angle * 180. / math.pi

    def render_graphics(self):
        if self.graphic_settings.draw_lines:
            batch: pyglet.graphics.Batch = self.engine.renderer.get_batch("lines")
            if batch:
                self.engine.renderer.draw_lines(batch, self.iter_world_points())
