import math
from typing import List

import pymunk
from pymunk import Vec2d
import pyglet

from .images import Images
from .renderer import Renderer
from .body import Body
from .player import Player
from .constraints import Constraint, JointBase


class Engine:

    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = Vec2d(0., -10.)
        self.time = 0.
        self.images = Images()
        self.renderer = Renderer(self)
        self.bodies: List[Body] = []
        self.constraints: List[Constraint] = []
        self._window_size = Vec2d((320, 200))
        self.player = Player((0, 0))
        self.add_body(self.player)

    @property
    def window_size(self):
        return self._window_size

    @window_size.setter
    def window_size(self, v):
        self._window_size = Vec2d(v)

    def update(self, dt, fixed_dt=None):
        for body in self.bodies:
            body.update(dt)
        for constraint in self.constraints:
            constraint.update(dt)

        self.space.step(fixed_dt or dt)

        self.time += dt

    def render(self, dt: float):
        for g in self.iter_graphics():
            g.update_graphics(dt)
        self.renderer.render()

    def add_body(self, body: Body):
        body._engine = self
        self.bodies.append(body)
        body.create_graphics()
        body.create_physics()
        body.on_engine_attached()

    def remove_body(self, body: Body):
        self.bodies.remove(body)
        body.destroy_physics()
        body.destroy_graphics()
        body.on_engine_detached()
        body._engine = None

    def add_constraint(self, constraint: Constraint):
        constraint._engine = self
        self.constraints.append(constraint)
        constraint.create_physics()
        constraint.create_graphics()
        constraint.on_engine_attached()

    def remove_constraint(self, constraint: Constraint):
        self.constraints.remove(constraint)
        constraint.destroy_graphics()
        constraint.destroy_physics()
        constraint.on_engine_detached()
        constraint._engine = None

    def iter_graphics(self):
        for g in self.bodies:
            yield g
        for g in self.constraints:
            yield g

    def dump(self, file=None):
        for body in self.bodies:
            body.dump(file=file)
