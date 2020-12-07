import math
from typing import List

import pymunk
from pymunk import Vec2d
import pyglet

from .graphical import Graphical


class Body(Graphical):

    def __init__(self, position, angle=0, density=0, **parameters):
        from .constraints import Constraint
        super().__init__(**parameters)

        self.start_position = Vec2d(position)
        self.start_angle = angle
        self.start_angular_velocity = 0.
        self.density = density
        self._start_angular_velocity_applied = False

        self._body: pymunk.Body = None
        self._shapes: List[pymunk.Shape] = []
        self._constraints: List[Constraint] = []

    def to_dict(self):
        return {
            **super().to_dict(),
            "start_position": self.start_position,
            "start_angle": self.start_angle,
            "start_angular_velocity": self.start_angular_velocity,
            "density": self.density,
        }

    @property
    def position(self):
        if self._body:
            return self._body.position
        return self.start_position

    @position.setter
    def position(self, v):
        v = Vec2d(v)
        if self._body:
            self._body.position = v
        self.start_position = v

    @property
    def angular_velocity(self):
        if self._body:
            return self._body.angular_velocity
        return self.start_angular_velocity

    @angular_velocity.setter
    def angular_velocity(self, v):
        if self._body:
            self._body.angular_velocity = v
        self.start_angular_velocity = v

    @property
    def angle(self):
        if self._body:
            return self._body.angle
        return self.start_angle

    @property
    def body(self):
        if self._body is None:
            raise ValueError(f"Request of non-existent body. Use {self.__class__.__name__}.create_graphics() first")
        return self._body

    def on_constraint_added(self, constraint):
        pass

    def on_remove_constraint(self, constraint):
        pass

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
        if self._body and not self._start_angular_velocity_applied:
            self._body.angular_velocity = self.start_angular_velocity
            self._start_angular_velocity_applied = True

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
        self._body.position = self.start_position
        self._body.angle = self.start_angle
        return self._body

    def iter_points(self):
        raise StopIteration

    def iter_world_points(self):
        for p in self.iter_points():
            yield self.position + p.rotated(self.angle)

    def dump(self, file=None):
        print(self.__class__.__name__, file=file)
        params = self.to_dict()
        for key in sorted(params):
            value = params[key]
            print(f"{key:30}: {repr(value)}", file=file)
        if self._constraints:
            print("constraints:", file=file)
            for c in self._constraints:
                print(" ", c, file=file)
        else:
            print("no constraints", file=file)

        #print(f"{self.__class__.__name__}: pos={self.position}, ang={self.angle}", file=file)

