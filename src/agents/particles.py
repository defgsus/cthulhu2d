import pymunk
from pymunk import Vec2d

from .base import AgentBase
from ..objects.primitives import Box, Circle, Ngon
from ..objects.graphical import GraphicSettings
from ..keyhandler import KeyHandler


class Particles(AgentBase):
    def __init__(self, **parameters):
        super().__init__(start_position=(0, 0), **parameters)

    def create_objects(self):
        pass

    def add_particle(
            self,
            position,
            velocity,
            radius,
            lifetime=3.,
            shape_filter=None,
    ):
        body = self.add_body(
            Ngon(position, radius, 5, density=.1, default_shape_filter=shape_filter)
        )
        body.velocity = velocity
        body.lifetime = 0.
        body.max_lifetime = lifetime

    def update(self, dt):
        super().update(dt)
        for body in self.bodies:
            body.lifetime += dt
            if body.lifetime >= body.max_lifetime:
                self.remove_body(body)
