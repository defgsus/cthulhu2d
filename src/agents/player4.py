import math

import pymunk
from pymunk import Vec2d

from .base import AgentBase
from ..objects.primitives import Box, Circle, Ngon
from ..objects.graphical import GraphicSettings
from ..objects import constraints
from ..keyhandler import KeyHandler


class Player4(AgentBase):
    def __init__(self, start_position, **parameters):
        super().__init__(start_position=start_position, **parameters)

        self.keys = KeyHandler()
        self.pick_dir = Vec2d()
        self.shape_filter = pymunk.ShapeFilter(categories=0b1, mask=pymunk.ShapeFilter.ALL_MASKS ^ 0b1)
        self.sequence_index = 0.
        self.sequence_speed = 0.
        self.sequence_add = 0.

    @property
    def position(self):
        if self.bodies:
            return self.bodies[0].position
        return self.start_position

    def create_objects(self):
        self.reference_points = (
            Vec2d(-.4, -.1),
            # Vec2d(0, .4),
            Vec2d(.4, -.1),
        )
        body = self.add_body(Ngon(
            position=self.start_position, radius=.5, segments=5,
            density=10,
            default_shape_filter=self.shape_filter,
        ))
        for sign, offset in ((-1, 0.), (1, .51)):
            foot = self.add_body(Ngon(
                position=self.start_position + (sign*.3, -.38), radius=.2, segments=3, density=100,
                friction=5.,
                default_shape_filter=self.shape_filter,
            ))
            self.add_constraint(constraints.RotaryLimitJoint(
                body, foot, -.1, .1
            ))
            for i, ref_point in enumerate(self.reference_points):
                self.add_constraint(constraints.FixedJoint(
                    body, foot, ref_point, (0, 0), user_data={"ref_point": ref_point, "offset": offset},
                ))

    def get_walk_sequence(self, t):
        exag = self.keys.smooth_down("left") + self.keys.smooth_down("right")
        body = self.bodies[0]
        r = (t + .25) * math.pi * 2
        r += math.sin(r*2)
        circle = Vec2d(math.sin(r), math.cos(r))
        foot = circle * Vec2d(.4, .15) + (0, -.4)
        foot.x *= 1. + exag
        foot.rotate(body.angle)
        foot.y = max(foot.y, -.4)
        foot.rotate(-body.angle)
        return foot

    def run_walk_sequence(self, dt):
        for c in filter(lambda c: c.has_user_data("ref_point"), self.constraints):
            ref_point = c.user_data["ref_point"]
            seq_point = self.get_walk_sequence(self.sequence_index + c.user_data["offset"])
            c.distance = (seq_point - ref_point).get_length()

        if self.sequence_add > 0.:
            self.sequence_index += self.sequence_add * dt
            self.sequence_add -= dt

    def walk(self, dt, speed):
        self.sequence_speed = speed
        self.sequence_add = 1
        #self.sequence_index += dt * speed / 3

    def update(self, dt):
        super().update(dt)
        self.run_walk_sequence(dt)

        body = self.bodies[0]
        
        pick_dir = Vec2d(0, 0)
        if self.keys.is_pressed("left"):
            pick_dir.x = -1
            speed = 1 + 3 * self.keys.smooth_down("left") + 6 * self.keys.smooth_pressed("left")
            self.walk(dt, -speed)

        if self.keys.is_pressed("right"):
            pick_dir.x = 1
            speed = 1 + 3 * self.keys.smooth_down("right") + 6 * self.keys.smooth_pressed("right")
            self.walk(dt, speed)

        if self.keys.is_pressed("up"):
            pick_dir.y = 1
            body.velocity += (0, 10)

        if self.keys.is_pressed("down"):
            pick_dir.y = -1
            body.velocity += (0, -10)#-dt * 30)

        if self.keys.is_pressed("shoot"):
            self.shoot(self.pick_dir)

        if pick_dir.x or pick_dir.y:
            self.pick_dir = pick_dir.normalized()

        if self.pick_dir.x or self.pick_dir.y:
            if self.keys.is_pressed("pick"):
                self.pick(self.pick_dir)

            if self.keys.is_pressed("put"):
                self.put(self.pick_dir)

        self.keys.update(dt)

    def pick(self, dir):
        body = self.bodies[0]
        pick_pos = body.position + dir

        other_body = self.engine.point_query_nearest_body(pick_pos)
        if other_body and other_body.density:
            self.engine.remove_body(other_body)

    def put(self, dir):
        body = self.bodies[0]

        put_pos = body.position + dir
        self.engine.add_body(
            Box(put_pos, (.5, .5), density=10)
        )

    def shoot(self, dir):
        bullet = self.add_body(Ngon(
            self.position, radius=.1, segments=3,
            density=1200,
            default_shape_filter=self.shape_filter,
        ))
        bullet.angular_velocity = 100.
        bullet.velocity = dir * 100
