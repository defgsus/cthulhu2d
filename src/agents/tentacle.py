import math

from pymunk import Vec2d

from ..objects.primitives import Box, Trapezoid
from ..objects.constraints import FixedJoint, PivotAnchorJoint
from .base import AgentBase


class Tentacle(AgentBase):
    
    def __init__(self, start_position, num_segments=15, speed=1, amount=1, **parameters):
        super().__init__(start_position=start_position, **parameters)
        self.num_segments = num_segments
        self.speed = speed
        self.amount = amount

    def update(self, dt):
        super().update(dt)
        time = self.engine.time * self.speed
        amount = min(1, time / 3.) * self.amount
        motor_joints = filter(lambda c: c.user_data and c.user_data.get("motor_sign"), self.constraints)
        for joint in motor_joints:
            sign, i = joint.user_data["motor_sign"], joint.user_data["index"]
            change = math.pow(.5*(1. + sign * math.sin(time)), 3.)
            joint.distance = change * joint.original_distance * 3 * amount

    def create_objects(self):
        #hit = self.engine.space.point_query_nearest(
        #    self.start_position - (0, .1), max_distance=0, shape_filter=pymunk.ShapeFilter()
        #)

        angle = 0
        density = 1
        scale = 1
        scale_factor = 0.9
        extent = Vec2d(.5, .5)
        start_pos = Vec2d(self.start_position) + (0, extent.y)
        pos = Vec2d(start_pos)
        last_body = None

        ground_query_pos = self.start_position - (0, extent.y+.1)
        ground_body = self.engine.point_query_nearest_body(ground_query_pos)

        for i in range(self.num_segments):
            #body = self.add_body(Box(pos, extent * scale, angle=angle, density=density))
            body = self.add_body(Trapezoid(
                pos,
                width_bottom=extent.x * scale * 2,
                width_top=extent.x * scale * scale_factor * 2,
                height=extent.y * scale * 2,
                angle=angle, density=density
            ))

            if last_body:
                self._tentacle_connect(last_body, body, 0, 0, user_data={"motor_sign": -1, "index": i}),
                self._tentacle_connect(last_body, body, 1, 0, user_data={"motor_sign": 1, "index": i}),

            last_body = body
            #angle += .3 * math.sin(i/3.)
            pos += Vec2d(0, 1).rotated(angle) * scale * 1.02
            scale *= scale_factor

        if ground_body and self.bodies:
            for ofs in (Vec2d(-.2, 0), Vec2d(.2, 0)):
                self.add_constraint(
                    FixedJoint(
                        ground_body, self.bodies[0],
                        ground_query_pos - ground_body.position + ofs,
                        Vec2d(0, -self.bodies[0].extent.y) + ofs,
                        breaking_impulse=0,
                    )
                )

    def _tentacle_connect(self, box_a, box_b, corner, bot, user_data=None):
        if corner == 0:
            anchor_a = box_a.top_left_extent
            anchor_b = box_b.bottom_left_extent
        else:
            anchor_a = box_a.top_right_extent
            anchor_b = box_b.bottom_right_extent

        bot_x = box_a.extent.x * bot * .3
        return self.add_constraint(
            FixedJoint(box_a, box_b, anchor_a + (bot_x, 0), anchor_b, breaking_impulse=0, user_data=user_data)
            #SpringJoint(
            #    box_a, box_b, anchor_a + (bot_x, 0), anchor_b,
            #    breaking_impulse=1000,
            #    stiffness=100,#min(10000, 5000 + box_a.extent.x * 30000),
            #    damping=100,
            #)
        )

