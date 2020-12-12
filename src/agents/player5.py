import math

import pymunk
from pymunk import Vec2d

from .base import AgentBase
from ..objects.primitives import Box, Circle, Ngon
from ..objects.graphical import GraphicSettings
from ..objects import constraints
from ..keyhandler import KeyHandler


class Player5(AgentBase):
    def __init__(self, start_position, **parameters):
        super().__init__(start_position=start_position, **parameters)

        self.keys = KeyHandler()
        self.pick_dir = Vec2d()
        self.shape_filter = pymunk.ShapeFilter(categories=0b1, mask=pymunk.ShapeFilter.ALL_MASKS ^ 0b1)
        self.sequence_index = 0.
        self.jump_amount = 0.
        self.walk_sign = 1
        self.walking = False

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
                body, foot, 0., 0., user_data={"foot_rot": sign}
            ))
            for i, ref_point in enumerate(self.reference_points):
                self.add_constraint(constraints.FixedJoint(
                    body, foot, ref_point, (0, 0), user_data={"ref_point": ref_point, "offset": offset},
                ))
            #self.engine.space.add_collision_handler()

    def get_walk_sequence(self, t):
        exag = self.keys.smooth_down("left") + self.keys.smooth_down("right")
        body = self.bodies[0]
        t += .25
        #t *= 2.
        #t = t % 1.
        #t = pow(t, .5)
        #t /= 2
        r = (t) * math.pi * 2
        #r += math.sin(r*2)
        circle = Vec2d(math.sin(r), math.cos(r))
        foot = circle * Vec2d(.5, .15) + (0, -.4 - 2.*self.jump_amount)
        foot.x *= .7 + .4*exag
        #foot.rotate(-body.angle)
        #foot.y = max(foot.y, -.4)
        #foot.rotate(-body.angle)
        return foot

    def run_walk_sequence(self, dt):
        for c in filter(lambda c: c.has_user_data("ref_point"), self.constraints):
            ref_point = c.user_data["ref_point"]
            seq_point = self.get_walk_sequence(self.sequence_index + c.user_data["offset"])
            c.distance = (seq_point - ref_point).get_length()

        self.jump_amount *= max(0, 1. - dt * 20)

        # always finish current step
        if not self.walking:
            next_index = math.ceil(self.sequence_index*2) if self.walk_sign > 0 else math.floor(self.sequence_index*2)
            next_index_diff = (next_index - self.sequence_index*2)/2
            if abs(next_index_diff) > 0.004:
                self.sequence_index += min(1, dt * 10) * next_index_diff

    def run_balance(self, dt):
        desired_angle = 0.#.4 * (-self.keys.is_down("right") + self.keys.is_down("left"))
        body = self.bodies[0]
        current_angle = body.angle
        amount = min(1, dt * 100. * abs(current_angle))
        body.angular_velocity += amount * (desired_angle - current_angle)

        for c in filter(lambda c: c.has_user_data("foot_rot"), self.constraints):
            c.min = c.max = -body.angle

    def walk(self, dt, speed):
        self.sequence_index += dt * speed / 3
        self.walk_sign = -1 if speed < 0 else 1
        self.walking = True

    def jump(self, dt):
        self.jump_amount = 1.

    def dump_body(self, name, body):
        values = {
            key: _round(getattr(body._body, key))
            for key in ("kinetic_energy", "torque", "moment", "velocity")
        }
        values.update({
            "surface_velocity": body._shapes[0].surface_velocity
        })
        print(name, values)

    def update(self, dt):
        super().update(dt)
        self.run_balance(dt)
        self.run_walk_sequence(dt)

        #self.dump_body("left ", self.bodies[1])
        #self.dump_body("right", self.bodies[2])

        body = self.bodies[0]
        
        pick_dir = Vec2d(0, 0)
        self.walking = False
        if self.keys.is_down("left"):
            pick_dir.x = -1
            speed = 1 + 3 * self.keys.smooth_down("left") + 6 * self.keys.smooth_pressed("left")
            self.walk(dt, -speed)

        if self.keys.is_down("right"):
            pick_dir.x = 1
            speed = 1 + 3 * self.keys.smooth_down("right") + 6 * self.keys.smooth_pressed("right")
            self.walk(dt, speed)

        if self.keys.is_pressed("up"):
            pick_dir.y = 1
            self.jump(dt)

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


def _round(x, digits=2):
    if isinstance(x, (Vec2d, tuple)):
        return tuple(round(v, digits) for v in x)
    try:
        return round(x, digits)
    except (TypeError, ValueError):
        return x
