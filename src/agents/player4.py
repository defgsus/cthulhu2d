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

    @property
    def position(self):
        if self.bodies:
            return self.bodies[0].position
        return self.start_position

    def create_objects(self):
        steps = 100
        self.walk_sequence = tuple(
            Vec2d(math.sin(i/steps*math.pi*2), math.cos(i/steps*math.pi*2)) * Vec2d(.5, .5) + (0, -.4)
            for i in range(steps)
        )
        self.reference_points = (
            Vec2d(-.4, .1),
            #Vec2d(0, .4),
            Vec2d(.4, .1),
        )
        self.reference_distance_sequences = tuple(
            tuple(
                (seq_point - ref_point).get_length()
                for seq_point in self.walk_sequence
            )
            for ref_point in self.reference_points
        )
        body = self.add_body(Circle(
            position=self.start_position, radius=.5, #segments=5,
            density=10,
            default_shape_filter=self.shape_filter,
        ))
        for sign, offset in ((-1, 0.), (1, .5)):
            foot = self.add_body(Ngon(position=self.start_position + (sign*.3, -.38), radius=.2, segments=3, density=100))
            for i, ref_point in enumerate(self.reference_points):
                self.add_constraint(constraints.SpringJoint(
                    body, foot, ref_point, (0, 0), user_data={"ref_point": i, "offset": offset},
                    stiffness=10000
                ))

    def run_walk_sequence(self, dt):
        for c in filter(lambda c: c.has_user_data("ref_point"), self.constraints):
            ref_distance_sequence = self.reference_distance_sequences[c.user_data["ref_point"]]
            seq_index = int((self.sequence_index + c.user_data["offset"]) * len(self.walk_sequence)) % len(self.walk_sequence)
            c.rest_length = ref_distance_sequence[seq_index]

        self.sequence_index += dt

    def update(self, dt):
        super().update(dt)
        self.run_walk_sequence(dt)

        body = self.bodies[0]
        
        side_speed = 5
        angular_speed = 10
        max_angular_speed = 20
        pick_dir = Vec2d(0, 0)
        if self.keys.is_down("left"):
            pick_dir.x = -1
            speed = 1 + 3 * self.keys.smooth_down("left") + 6 * self.keys.smooth_pressed("left")
            body.velocity += (-dt * side_speed * speed, 0)
            if body.angular_velocity < max_angular_speed:
                body.angular_velocity += dt * angular_speed * speed

        if self.keys.is_down("right"):
            pick_dir.x = 1
            speed = 1 + 3 * self.keys.smooth_down("right") + 6 * self.keys.smooth_pressed("right")
            body.velocity -= (-dt * side_speed * speed, 0)
            if body.angular_velocity > -max_angular_speed:
                body.angular_velocity -= dt * angular_speed * speed

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
