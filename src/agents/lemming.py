import pymunk
from pymunk import Vec2d

from .base import AgentBase
from ..objects.primitives import Box, Circle, Ngon
from ..objects.graphical import GraphicSettings
from ..keyhandler import KeyHandler


class Lemming(AgentBase):
    def __init__(self, start_position, direction=-1, radius=.4, **parameters):
        super().__init__(start_position=start_position, **parameters)
        self.radius = radius
        self.direction = direction
        self.direction_progress = 0.

    @property
    def position(self):
        if self.bodies:
            return self.bodies[0].position
        return self.start_position

    @property
    def body(self):
        return self.bodies[0] if self.bodies else None

    def create_objects(self):
        body = Ngon(
            position=self.start_position, radius=self.radius, segments=7,
            density=20,
            graphic_settings=GraphicSettings(
                draw_lines=True,
                #draw_sprite=True, image_name="player1",
            ),
        )
        self.add_body(body)

    def apply_move(self, sign, dt):
        side_speed = 5
        angular_speed = 10
        max_angular_speed = 20

        body = self.body
        body.velocity += (sign * dt * side_speed, 0)
        if body.angular_velocity < max_angular_speed:
            body.angular_velocity += -sign * dt * angular_speed

    def update(self, dt):
        super().update(dt)

        dir_progress = max(0., self.body.velocity.x * self.direction)
        self.direction_progress += (dir_progress - self.direction_progress) * min(1., dt * 3.)
        if self.direction_progress < 1.:
            self.direction = -self.direction
            self.direction_progress = 100.
        #print(self.direction_progress)

        if self.body:
            self.apply_move(self.direction, dt)
