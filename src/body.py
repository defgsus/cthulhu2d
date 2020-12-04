import math
from typing import List

import pymunk
from pymunk import Vec2d
import pyglet


class Body:

    def __init__(self, position, angle=0, density=0, **parameters):
        self._parameters = {
            "start_position": Vec2d(position),
            "start_angle": angle,
            "density": density,
            **parameters,
        }
        self._body: pymunk.Body = None
        self._shapes: List[pymunk.Shape] = []
        self._graphics = []

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

    def get_parameter(self, name):
        return self._parameters.get(name)

    def create_physics(self, engine):
        pass

    def destroy_physics(self, engine):
        for shape in self._shapes:
            engine.space.remove(shape)
            del shape
        self._shapes = []
        if self._body:
            engine.space.remove(self._body)
        del self._body
        self._body = None

    def create_graphics(self, engine):
        pass

    def destroy_graphics(self, engine):
        for g in self._graphics:
            g.delete()
            del g
        self._graphics = []

    def update(self, dt):
        pass

    def update_graphics(self, dt):
        pass

    def _create_body(self):
        if not self.density:
            self._body = pymunk.Body(body_type=pymunk.Body.STATIC)
        else:
            self._body = pymunk.Body()
        self._body.position = self._parameters["start_position"]
        return self._body

    def dump(self, file=None):
        print(f"{self.__class__.__name__}: pos={self.position}, ang={self.angle}")
