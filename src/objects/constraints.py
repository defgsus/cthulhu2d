import pymunk
from pymunk import Vec2d

from .graphical import Graphical, GraphicSettings
from .physical import PhysicsInterface


class Constraint(PhysicsInterface, Graphical):

    def __init__(self, a, b, breaking_impulse=0, **parameters):
        if "graphic_settings" not in parameters:
            parameters["graphic_settings"] = GraphicSettings(
                draw_lines=True, draw_sprite=False,
                # line_batch_name="constraint-lines"
            )
        Graphical.__init__(self, **parameters)
        PhysicsInterface.__init__(self)

        self.a = a
        self.b = b
        self.breaking_impulse = breaking_impulse
        # the pymunk constraint
        self._constraint = None

    def to_dict(self):
        return {
            **super().to_dict(),
            "a": self.a.id,
            "b": self.b.id,
            "breaking_impulse": self.breaking_impulse,
        }

    @property
    def impulse(self):
        if not self._constraint:
            return 0.
        return self._constraint.impulse

    def remove(self):
        """Remove from parent/base container"""
        if self.engine:
            if self._parent_container:
                self._parent_container.remove_constraint(self)
            else:
                self.engine.remove_constraint(self)

    def destroy_physics(self):
        if self._constraint:
            self.engine.space.remove(self._constraint)
        self._constraint = None

    def update(self, dt):
        super().update(dt)
        true_impulse = self.impulse / dt

        if self.breaking_impulse and true_impulse > self.breaking_impulse:
            #print(f"constraint broken {true_impulse} > {self.breaking_impulse}: {self}")
            self.engine.remove_constraint(self)

    def iter_world_points(self):
        if hasattr(self, "anchor_a") and hasattr(self, "anchor_b"):
            yield self.a.position + self.anchor_a.rotated(self.a.angle)
            yield self.b.position + self.anchor_b.rotated(self.b.angle)


class FixedJoint(Constraint):

    def __init__(self, a, b, anchor_a, anchor_b, **parameters):
        super().__init__(a, b, **parameters)
        self.anchor_a = Vec2d(anchor_a)
        self.anchor_b = Vec2d(anchor_b)
        self.original_distance = None

    def to_dict(self):
        return {
            **super().to_dict(),
            "anchor_a": self.anchor_a,
            "anchor_b": self.anchor_b,
            "original_distance": self.original_distance,
        }

    @property
    def distance(self):
        if not self._constraint:
            return 0.
        return self._constraint.distance

    @distance.setter
    def distance(self, v):
        if self._constraint:
            self._constraint.distance = v

    def create_physics(self):
        constraint = pymunk.PinJoint(
            self.a.body, self.b.body,
            anchor_a=self.anchor_a,
            anchor_b=self.anchor_b,
        )

        self._constraint = constraint
        self.engine.space.add(constraint)
        self.original_distance = self._constraint.distance


class PivotAnchorJoint(Constraint):

    def __init__(self, a, b, anchor_a, anchor_b, **parameters):
        super().__init__(a, b, **parameters)
        self.anchor_a = Vec2d(anchor_a)
        self.anchor_b = Vec2d(anchor_b)

    def to_dict(self):
        return {
            **super().to_dict(),
            "anchor_a": self.anchor_a,
            "anchor_b": self.anchor_b,
        }

    def create_physics(self):
        constraint = pymunk.PivotJoint(
            self.a.body, self.b.body,
            self.anchor_a,
            self.anchor_b,
        )
        self._constraint = constraint
        self.engine.space.add(constraint)


class SpringJoint(Constraint):

    def __init__(self, a, b, anchor_a, anchor_b, stiffness=1000, damping=10, rest_length=None, **parameters):
        super().__init__(a, b, **parameters)
        self.anchor_a = Vec2d(anchor_a)
        self.anchor_b = Vec2d(anchor_b)
        if rest_length is None:
            world_pos_a = a.position + anchor_a
            world_pos_b = b.position + anchor_b
            rest_length = (world_pos_a - world_pos_b).get_length()
        self._rest_length = rest_length
        self.original_rest_length = rest_length
        self.stiffness = stiffness
        self.damping = damping

    def to_dict(self):
        return {
            **super().to_dict(),
            "anchor_a": self.anchor_a,
            "anchor_b": self.anchor_b,
            "stiffness": self.stiffness,
            "damping": self.damping,
            "rest_length": self.rest_length,
        }

    @property
    def rest_length(self):
        return self._rest_length

    @rest_length.setter
    def rest_length(self, v):
        self._rest_length = v
        if self._constraint:
            self._constraint.rest_length = v

    def create_physics(self):
        constraint = pymunk.DampedSpring(
            self.a.body, self.b.body,
            anchor_a=self.anchor_a,
            anchor_b=self.anchor_b,
            rest_length=self.rest_length,
            stiffness=self.stiffness,
            damping=self.damping,
        )

        self._constraint = constraint
        self.engine.space.add(constraint)


class RotarySpringJoint(Constraint):

    def __init__(self, a, b, anchor_a, anchor_b, rest_angle, stiffness=1000, damping=10, **parameters):
        super().__init__(a, b, **parameters)
        self.anchor_a = Vec2d(anchor_a)
        self.anchor_b = Vec2d(anchor_b)
        self._rest_angle = rest_angle
        self.original_rest_angle = rest_angle
        self.stiffness = stiffness
        self.damping = damping

    def to_dict(self):
        return {
            **super().to_dict(),
            "anchor_a": self.anchor_a,
            "anchor_b": self.anchor_b,
            "stiffness": self.stiffness,
            "damping": self.damping,
            "rest_angle": self.rest_angle,
        }

    @property
    def rest_angle(self):
        return self._rest_angle

    @rest_angle.setter
    def rest_angle(self, v):
        self._rest_angle = v
        if self._constraint:
            self._constraint.rest_angle = v

    def create_physics(self):
        constraint = pymunk.DampedRotarySpring(
            self.a.body, self.b.body,
            rest_angle=self.rest_angle,
            stiffness=self.stiffness,
            damping=self.damping,
        )

        self._constraint = constraint
        self.engine.space.add(constraint)


class RotaryLimitJoint(Constraint):

    def __init__(self, a, b, min, max, **parameters):
        super().__init__(a, b, **parameters)
        self._min = min
        self._max = max

    def to_dict(self):
        return {
            **super().to_dict(),
            "min": self._min,
            "max": self._max,
        }

    @property
    def min(self):
        if self._constraint:
            return self._constraint.min
        return self._min

    @min.setter
    def min(self, v):
        if self._constraint:
            self._constraint.min = v
        self._min = v

    @property
    def max(self):
        if self._constraint:
            return self._constraint.max
        return self._max

    @max.setter
    def max(self, v):
        if self._constraint:
            self._constraint.max = v
        self._max = v
    
    def create_physics(self):
        constraint = pymunk.RotaryLimitJoint(
            self.a.body, self.b.body,
            min=self.min,
            max=self.max,
        )

        self._constraint = constraint
        self.engine.space.add(constraint)
