import math

import pymunk
from pymunk import Vec2d

import pyglet
from pyglet import gl

from .engine_obj import EngineObject
from .graphical import Graphical


class Constraint(Graphical):

    def __init__(self, a, b, breaking_impulse=200, **parameters):
        # TODO: how to parmeterize a and b objects?
        super().__init__(
            breaking_impulse=breaking_impulse,
            **parameters
        )
        self.a = a
        self.b = b
        # the pymunk constraint
        self._constraint = None
        # give bodies access to their constraints
        self.a._constraints.append(self)
        self.b._constraints.append(self)

    @property
    def breaking_impulse(self):
        return self._parameters["breaking_impulse"]

    @property
    def impulse(self):
        if not self._constraint:
            return 0.
        return self._constraint.impulse

    def create_physics(self):
        raise NotImplementedError
    
    def destroy_physics(self):
        if self._constraint:
            self.engine.space.remove(self._constraint)
        self._constraint = None

    def update(self, dt):
        true_impulse = self.impulse / dt

        if true_impulse > self.breaking_impulse:
            self.engine.remove_constraint(self)


class FixedJoint(Constraint):

    def __init__(self, a, b, anchor_a, anchor_b, **parameters):
        super().__init__(
            a, b,
            anchor_a=Vec2d(anchor_a),
            anchor_b=Vec2d(anchor_b),
            **parameters,
        )

    @property
    def anchor_a(self):
        return self._parameters["anchor_a"]

    @property
    def anchor_b(self):
        return self._parameters["anchor_b"]

    def create_physics(self):
        constraint = pymunk.PinJoint(
            self.a.body, self.b.body,
            anchor_a=Vec2d(self.get_parameter("anchor_a")),
            anchor_b=Vec2d(self.get_parameter("anchor_b")),
            #min=0, max=1 * .3,
        )
        constraint.error_bias = 0.000001
        #constraint.max_bias = 100.
        constraint.breaking_impulse = self.get_parameter("breaking_impulse")

        self._constraint = constraint
        self.engine.space.add(constraint)

    def create_graphics(self):
        pass

    def render_graphics(self):
        batch = self.engine.renderer.get_batch("lines")
        if not batch:
            return

        p1 = self.a.position + self.anchor_a.rotated(self.a.angle)
        p2 = self.b.position + self.anchor_b.rotated(self.b.angle)
        #f = (p2 - p1).normalized() * min(.3, 0.01 + self.impulse)
        #p1 -= f
        #p2 += f
        batch.add(
            2, gl.GL_LINES, None,
            ("v2f", (p1.x, p1.y, p2.x, p2.y)),
        )
