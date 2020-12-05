import math
from typing import List

import pymunk
from pymunk import Vec2d
import pyglet

from .images import Images
from .renderer import Renderer
from .body import Body
from .player import Player
from .constraints import Constraint


class Engine:

    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = Vec2d(0., -10.)
        self.time = 0.
        self.images = Images()
        self.renderer = Renderer(self)
        self.bodies: List[Body] = []
        self._pymunk_body_to_body = {}
        self._empty_shape_filter = pymunk.ShapeFilter()
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

        pymunk_steps = 10
        pymunk_dt = (fixed_dt or dt) / pymunk_steps
        for i in range(pymunk_steps):
            self.space.step(pymunk_dt)

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
        self._pymunk_body_to_body[body._body] = body
        body.on_engine_attached()

    def remove_body(self, body: Body):
        for constraint in body._constraints:
            self.remove_constraint(constraint)
        self.bodies.remove(body)
        self._pymunk_body_to_body.pop(body._body, None)
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
        if constraint not in self.constraints:
            return
        for obj in (constraint.a, constraint.b):
            if constraint in obj._constraints:
                obj._constraints.remove(constraint)
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

    def point_query_nearest_body(self, position, max_distance=0, shape_filter=None):
        hit = self.space.point_query_nearest(
            position, max_distance, shape_filter or self._empty_shape_filter
        )
        print("Hit", position, hit)
        if not hit or not hit.shape:
            return None

        pymunk_body = hit.shape.body
        if pymunk_body not in self._pymunk_body_to_body:
            raise AssertionError(f"pymunk body {pymunk_body} not in engine's mapping")

        return self._pymunk_body_to_body[pymunk_body]

    def dump(self, file=None):
        for body in self.bodies:
            body.dump(file=file)
