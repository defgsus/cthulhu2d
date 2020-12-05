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

    def render_graphics(self):
        batch: pyglet.graphics.Batch = self.engine.renderer.get_batch("lines")
        if not batch:
            return

        vertices = []
        for corner in self.iter_points():
            pos = self.position + corner.rotated(self.angle)
            vertices.append(pos.x)
            vertices.append(pos.y)
        batch.add_indexed(
            len(vertices) // 2, gl.GL_LINES, None,
            [0, 1, 1, 2, 2, 3, 3, 0],
            ("v2f", vertices),
        )
