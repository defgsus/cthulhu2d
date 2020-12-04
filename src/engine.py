import math
from typing import List

import pymunk
from pymunk import Vec2d
import pyglet

from .images import Images
from .renderer import Renderer
from .body import Body
from .player import Player


class Engine:

    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = Vec2d(0., -10.)
        self.time = 0.
        self.images = Images()
        self.renderer = Renderer(self)
        self.bodies: List[Body] = []
        self._window_size = Vec2d((320, 200))
        self.player = Player((0, 0))
        self.add_body(self.player)

    @property
    def window_size(self):
        return self._window_size

    @window_size.setter
    def window_size(self, v):
        self._window_size = Vec2d(v)

    def update(self, dt, fixed_dt=None):
        for body in self.bodies:
            body.update(dt)

        self.space.step(fixed_dt or dt)

        self.time += dt

    def render(self, dt):
        for body in self.bodies:
            body.update_graphics(dt)
        self.renderer.render()

    def add_body(self, body):
        self.bodies.append(body)
        body.create_graphics(self)
        body.create_physics(self)

    def remove_body(self, body):
        self.bodies.remove(body)
        body.destroy_physics()
        body.destroy_graphics()

    def dump(self, file=None):
        for body in self.bodies:
            body.dump(file=None)