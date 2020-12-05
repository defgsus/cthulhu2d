import math
from typing import List

import pymunk
from pymunk import Vec2d
import pyglet

from .graphical import Graphical


class Body(Graphical):

    def __init__(self, position, angle=0, density=0, **parameters):
        from .constraints import Constraint

        super().__init__(
            start_position=Vec2d(position),
            start_angle=angle,
            density=density,
            **parameters,
        )
        self._body: pymunk.Body = None
        self._shapes: List[pymunk.Shape] = []
        self._constraints: List[Constraint] = []

    @property
    def position(self):
        if self._body:
            return self._body.position
        return self._parameters["start_position"]

    @position.setter
    def position(self, v):
        v = Vec2d(v)
        if self._body:
            self._body.position = v
        self._parameters["start_position"] = v

    @property
    def angle(self):
        if self._body:
            return self._body.angle
        return self._parameters["start_angle"]

    @property
    def density(self):
        return self._parameters["density"]

    @property
    def body(self):
        if self._body is None:
            raise ValueError(f"Request of non-existent body. Use {self.__class__.__name__}.create_graphics() first")
        return self._body

    def create_physics(self):
        pass

    def destroy_physics(self):
        for shape in self._shapes:
            self.engine.space.remove(shape)

        self._shapes = []
        if self._body:
            self.engine.space.remove(self._body)

        self._body = None

    def update(self, dt):
        pass

    def add_shape(self, shape: pymunk.Shape):
        """
        Add a pymunk Shape object.
        To be called within create_physics()
        """
        shape.density = self.density
        shape.friction = 1.
        self._shapes.append(shape)

    def _create_body(self):
        if not self.density:
            self._body = pymunk.Body(body_type=pymunk.Body.STATIC)
        else:
            self._body = pymunk.Body()
        self._body.position = self._parameters["start_position"]
        return self._body

    def iter_points(self):
        raise StopIteration

    def iter_world_points(self):
        for p in self.iter_points():
            yield self.position + p.rotated(self.angle)

    def dump(self, file=None):
        print(f"{self.__class__.__name__}: pos={self.position}, ang={self.angle}", file=file)
