import pymunk
from pymunk import Vec2d

from .base import AgentBase
from ..objects.primitives import Box, Circle, Ngon
from ..objects.graphical import GraphicSettings
from ..objects import constraints
from ..keyhandler import KeyHandler


class Player3(AgentBase):
    def __init__(self, start_position, **parameters):
        super().__init__(start_position=start_position, **parameters)

        self.keys = KeyHandler()
        self.pick_dir = Vec2d()
        self.shape_filter = pymunk.ShapeFilter(categories=0b1, mask=pymunk.ShapeFilter.ALL_MASKS ^ 0b1)
        self.sequences = []

    @property
    def position(self):
        if self.bodies:
            return self.bodies[0].position
        return self.start_position

    def create_objects(self):
        """
        ..###..
        ..###..
        ..###..
        ..#.#..
        ..#.#..
        .##.##.
        """
        density = 50
        body = self.add_body(Box(
            position=self.start_position, extent=(.3, .3), density=density,
            default_shape_filter=self.shape_filter,
        ))
        def _create_leg(s):
            leg_1 = self.add_body(Box(
                position=self.start_position + (s*.2, -.45), extent=(.1, .15), density=density,
                default_shape_filter=self.shape_filter,
            ))
            leg_2 = self.add_body(Box(
                position=self.start_position + (s*.2, -.75), extent=(.1, .15), density=density,
                default_shape_filter=self.shape_filter,
            ))
            foot = self.add_body(Box(
                position=self.start_position + (s*.3, -.95), extent=(.2, .05), density=density,
                default_shape_filter=self.shape_filter,
            ))
            self.add_constraint(constraints.FixedJoint(body, leg_1, (s*.2, -.3), (0, .15)))
            self.add_constraint(constraints.FixedJoint(leg_1, leg_2, (0, -.15), (0, .15)))
            self.add_constraint(constraints.FixedJoint(leg_2, foot, (0, -.15), (-s*0.1, .05)))
            self.add_constraint(constraints.RotaryLimitJoint(body, leg_1, 0., 0., user_data={"rot_leg_1": s}))
            self.add_constraint(constraints.RotaryLimitJoint(leg_1, leg_2, 0., 0., user_data={"rot_leg_2": s}))
            self.add_constraint(constraints.RotaryLimitJoint(leg_2, foot, 0., 0., user_data={"rot_foot": s}))
        _create_leg(-1)
        _create_leg(1)

    def jump(self, dt):
        self.add_sequence({
            "rot_leg_1": [0, 1.4],
            "rot_leg_2": [0, -2],
            "rot_foot": [0, .4],
        }, amount=3)

    def add_sequence(self, data, length=0.2, amount=1):
        max_len = 0
        for seq in data.values():
            max_len = max(max_len, len(seq))
        if max_len:
            self.sequences.append({
                "length": length,
                "time": 0.,
                "amount": amount,
                "seqs": data,
            })

    def run_sequences(self, dt):
        seqs_to_remove = []
        for s in self.sequences:
            time, length, amount = s["time"], s["length"], s["amount"]
            if time >= length:
                seqs_to_remove.append(s)
                continue

            time_factor = time / length
            for key, seq in s["seqs"].items():
                x = time_factor * len(seq)
                ix = int(x)
                fx = x - ix
                v0 = seq[ix]
                v1 = seq[ix+1] if ix+1 < len(seq) else 0.
                v = v0 * (1. - fx) + fx * v1
                v *= amount

                for c in filter(lambda c: c.has_user_data(key), self.constraints):
                    c.min = v * c.get_user_data(key)
                    c.max = v * c.get_user_data(key)

            s["time"] += dt

        for s in seqs_to_remove:
            self.sequences.remove(s)

    def update(self, dt):
        super().update(dt)

        self.run_sequences(dt)

        body = self.bodies[0]
        
        side_speed = 5
        angular_speed = 10
        max_angular_speed = 20
        pick_dir = Vec2d(0, 0)
        if self.keys.is_down("left"):
            pick_dir.x = -1
            speed = 1 + 3 * self.keys.smooth_down("left") + 6 * self.keys.smooth_pressed("left")
            body.velocity += (-dt * side_speed * speed, 0)
            #if body.angular_velocity < max_angular_speed:
            #    body.angular_velocity += dt * angular_speed * speed

        if self.keys.is_down("right"):
            pick_dir.x = 1
            speed = 1 + 3 * self.keys.smooth_down("right") + 6 * self.keys.smooth_pressed("right")
            body.velocity -= (-dt * side_speed * speed, 0)
            #if body.angular_velocity > -max_angular_speed:
            #    body.angular_velocity -= dt * angular_speed * speed

        if self.keys.is_pressed("up"):
            pick_dir.y = 1
            #body.velocity += (0, 10)
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
