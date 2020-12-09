import pymunk
from pymunk import Vec2d

from .base import AgentBase
from ..objects.primitives import Circle, Ngon
from ..objects.graphical import GraphicSettings
from ..objects import constraints
from ..keyhandler import KeyHandler


class Player2(AgentBase):
    def __init__(self, start_position, **parameters):
        super().__init__(start_position=start_position, **parameters)

        self.keys = KeyHandler()
        self.pick_dir = Vec2d()

    @property
    def position(self):
        if self.bodies:
            return self.bodies[0].position
        return self.start_position

    def create_objects(self):
        shape_filter = pymunk.ShapeFilter(categories=0b1, mask=pymunk.ShapeFilter.ALL_MASKS ^ 0b1)
        body = self.add_body(Ngon(
            position=self.start_position, radius=.4, segments=5,
            density=10,
            graphic_settings=GraphicSettings(
                draw_lines=True, #draw_sprite=True,
                image_name="player1",
            ),
            default_shape_filter=shape_filter
        ))
        if 0:
            hand = self.add_body(Ngon(
                position=self.start_position + (-.4, .1),
                radius=.2,
                segments=3,
                density=10,
                default_shape_filter=shape_filter,
            ))
            self.add_constraint(constraints.RotarySpringJoint(
                body, hand, (0, 0), (0, 0), rest_angle=0,
            ))

        for i in range(2):
            i = i * 2 - 1
            foot = self.add_body(Ngon(
                position=self.start_position + (i * .23, -.21),
                radius=.2,
                segments=3,
                density=50,
                default_shape_filter=shape_filter,
            ))
            self.add_constraint(constraints.FixedJoint(
                body, foot,
                (0, 0), (0, 0),
                user_data={"leg": i}
            ))
        self.add_constraint(constraints.FixedJoint(
            self.bodies[-2], self.bodies[-1],
            (0, 0), (0, 0),
            user_data={"leg": 0}
        ))

    def jump(self, dt):
        #self.bodies[0].velocity += (0, 10)
        for leg in filter(lambda c: c.has_user_data("leg"), self.constraints):
            if leg.get_user_data("leg"):
                leg.distance = leg.original_distance * 8.
            else:
                leg.distance = leg.original_distance * .3

    def duck(self, dt):
        for leg in filter(lambda c: c.has_user_data("leg"), self.constraints):
            leg.distance = leg.original_distance * .1

    def relax_legs(self, dt):
        for c in filter(lambda c: c.has_user_data("leg"), self.constraints):
            c.distance += (c.original_distance - c.distance) * min(1, dt * 20)

    def move_x(self, speed):
        #for c in filter(lambda c: c.has_user_data("leg") , self.constraints):
        #    #if c.get_user_data("leg") < 0 and speed < 0 or c.get_user_data("leg") > 0 and speed > 0:
        #    c.distance = c.original_distance * (1 + c.user_data["leg"] * speed * 10)
        #return
        side_speed = 5
        angular_speed = 10
        max_angular_speed = 20
        for foot in (self.bodies[-2], self.bodies[-1]):

            foot.velocity += (side_speed * speed, 0)
            if foot.angular_velocity < max_angular_speed:
                foot.angular_velocity += angular_speed * speed

    def update(self, dt):
        super().update(dt)
        self.relax_legs(dt)
        body = self.bodies[0]
        
        pick_dir = Vec2d(0, 0)
        if self.keys.is_down("left"):
            pick_dir.x = -1
            speed = 1 + 3 * self.keys.smooth_down("left") + 6 * self.keys.smooth_pressed("left")
            self.move_x(-dt * speed)

        if self.keys.is_down("right"):
            pick_dir.x = 1
            speed = 1 + 3 * self.keys.smooth_down("right") + 6 * self.keys.smooth_pressed("right")
            self.move_x(dt * speed)

        if self.keys.is_pressed("up"):
            pick_dir.y = 1
            self.jump(dt)

        if self.keys.is_pressed("down"):
            pick_dir.y = -1
            self.duck(dt)
            #body.velocity += (0, -10)#-dt * 30)

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
        from ..objects.primitives import Box
        body = self.bodies[0]

        put_pos = body.position + dir
        self.engine.add_body(
            Box(put_pos, (.5, .5), density=10)
        )

