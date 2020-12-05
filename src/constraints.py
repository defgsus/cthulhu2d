import math

import pymunk
from pymunk import Vec2d

import pyglet
from pyglet import gl

from .engine_obj import EngineObject
from .graphical import Graphical


class Constraint(Graphical):

    def __init__(self, a, b, breaking_impulse=0, **parameters):
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

        if self.breaking_impulse and true_impulse > self.breaking_impulse:
            #print(f"constraint broken {true_impulse} > {self.breaking_impulse}: {self}", self._parameters)
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

    @property
    def distance(self):
        if not self._constraint:
            return 0.
        return self._constraint.distance

    @distance.setter
    def distance(self, v):
        if self._constraint:
            self._constraint.distance = v

    @property
    def original_distance(self):
        return self._parameters.get("original_distance", 0.)

    def create_physics(self):
        constraint = pymunk.PinJoint(
            self.a.body, self.b.body,
            anchor_a=self.anchor_a,
            anchor_b=self.anchor_b,
            #min=0, max=1 * .3,
        )

        self._constraint = constraint
        self.engine.space.add(constraint)
        self._parameters["original_distance"] = self._constraint.distance

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


class PivotAnchorJoint(Constraint):

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
        constraint = pymunk.PivotJoint(
            self.a.body, self.b.body,
            self.anchor_a,
            self.anchor_b,
        )
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
        batch.add(
            2, gl.GL_LINES, None,
            ("v2f", (p1.x, p1.y, p2.x, p2.y)),
        )


class SpringJoint(Constraint):

    def __init__(self, a, b, anchor_a, anchor_b, stiffness=1000, damping=10, rest_length=None, **parameters):
        if rest_length is None:
            world_pos_a = a.position + anchor_a
            world_pos_b = b.position + anchor_b
            rest_length = (world_pos_a - world_pos_b).get_length()

        super().__init__(
            a, b,
            anchor_a=Vec2d(anchor_a),
            anchor_b=Vec2d(anchor_b),
            rest_length=rest_length,
            original_rest_length=rest_length,
            stiffness=stiffness,
            damping=damping,
            **parameters,
        )

    @property
    def anchor_a(self):
        return self._parameters["anchor_a"]

    @property
    def anchor_b(self):
        return self._parameters["anchor_b"]

    @property
    def rest_length(self):
        return self._parameters["rest_length"]

    @property
    def original_rest_length(self):
        return self._parameters["original_rest_length"]

    @rest_length.setter
    def rest_length(self, v):
        self._parameters["rest_length"] = v
        if self._constraint:
            self._constraint.rest_length = v

    @property
    def stiffness(self):
        return self._parameters["stiffness"]

    @property
    def damping(self):
        return self._parameters["damping"]

    def create_physics(self):
        constraint = pymunk.DampedSpring(
            self.a.body, self.b.body,
            anchor_a=self.anchor_a,
            anchor_b=self.anchor_b,
            rest_length=self.rest_length,
            stiffness=self.stiffness,
            damping=self.damping,
        )
        constraint.error_bias = 0.000001

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


class RotaryLimitJoint(Constraint):

    def __init__(self, a, b, min, max, **parameters):
        super().__init__(
            a, b,
            min=min,
            max=max,
            **parameters,
        )

    @property
    def min(self):
        return self._parameters["min"]

    @property
    def max(self):
        return self._parameters["max"]

    def create_physics(self):
        constraint = pymunk.RotaryLimitJoint(
            self.a.body, self.b.body,
            min=self.min,
            max=self.max,
        )

        self._constraint = constraint
        self.engine.space.add(constraint)

    def create_graphics(self):
        pass

    def render_graphics(self):
        batch = self.engine.renderer.get_batch("lines")
        if not batch:
            return

        p1 = self.a.position
        p2 = self.b.position
        #f = (p2 - p1).normalized() * min(.3, 0.01 + self.impulse)
        #p1 -= f
        #p2 += f
        batch.add(
            2, gl.GL_LINES, None,
            ("v2f", (p1.x, p1.y, p2.x, p2.y)),
        )
