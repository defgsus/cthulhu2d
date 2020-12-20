import pymunk
from pymunk import Vec2d

from .base import AgentBase
from ..objects.primitives import Box, Circle, Ngon
from ..objects.graphical import GraphicSettings
from ..keyhandler import KeyHandler
from ..util import dump_object


class Player(AgentBase):
    def __init__(self, start_position, **parameters):
        super().__init__(start_position=start_position, **parameters)

        self.keys = KeyHandler()
        self.pick_dir = Vec2d()
        self.shape_filter = pymunk.ShapeFilter(categories=0b1, mask=pymunk.ShapeFilter.ALL_MASKS ^ 0b1)
        self.radius = .4
        self.picked_bodies = []

    @property
    def position(self):
        if self.bodies:
            return self.bodies[0].position
        return self.start_position

    def create_objects(self):
        body = Ngon(
            position=self.start_position, radius=self.radius, segments=5,
            density=50,
            graphic_settings=GraphicSettings(
                draw_lines=True, #draw_sprite=True,
                image_name="player1",
            ),
            default_shape_filter=self.shape_filter,
        )
        self.add_body(body)

    def update(self, dt):
        super().update(dt)
        
        body = self.bodies[0]
        # print(self.has_foot_contact())

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

    def has_foot_contact(self):
        for offset in (
                (0, 0), (-self.radius, 0), (self.radius, 0)
        ):
            ground = self.engine.trace(
                self.position + offset, direction=(0, -1),
                max_steps=20, min_distance=.02, max_distance=1., shape_filter=self.shape_filter
            )
            #if ground:
            #    print((self.position - ground.position).length)
            if ground and (self.position - ground.position).length <= self.radius * 1.2:
                return True
        return False

    def jump(self, dt):
        body = self.bodies[0]
        if self.has_foot_contact(): #body.kinetic_energy < 100:
            body.velocity += (0, 10)

    def pick(self, dir):
        body = self.bodies[0]
        pick_pos = body.position + dir

        other_body = self.engine.point_query_nearest_body(pick_pos)
        if other_body and other_body.pickable:
            self.engine.remove_body(other_body)
            self.picked_bodies.append(other_body)

    def put(self, dir):
        body = self.bodies[0]
        put_pos = body.position + dir

        if self.picked_bodies:
            body = self.picked_bodies.pop(-1)
            body.position = put_pos
            if not body.density:
                body.density = 1.
            self.engine.add_body(body)

    def shoot(self, dir):
        bullet = self.add_body(Ngon(
            self.position, radius=.1, segments=3,
            density=1200,
            default_shape_filter=self.shape_filter,
        ))
        bullet.angular_velocity = 100.
        bullet.velocity = dir * 100

    def on_collision(self, a, b, arbiter: pymunk.Arbiter):
        body = b if a in self.bodies else a
        body_type = body.get_user_data("type")

        #if body_type == "stone":
        if arbiter.total_impulse.y > 20.:
            mass = body.mass
            if mass:
                self.engine.add_particles(
                    self.position + (0, self.radius*.7),
                    num=max(10, int(arbiter.total_impulse.length / 4.)),
                    shape_filter=self.shape_filter
                )

            print(f"COLLISION {a} <-> {b}")
            dump_object(arbiter)
            #print("mass", body.mass)

        #if body_type == "sand":
        #    self.engine.remove_body(body)

        return True
        for key in dir(arbiter):
            if not key.startswith("_"):
                print(f"{key:20} = {getattr(arbiter, key)}")
        return True