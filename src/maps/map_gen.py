"""
Some testbed for map creation
"""

import math
import random

import numpy as np

from pymunk import Vec2d

from ..engine import Engine
from ..objects.primitives import Box
from ..objects.constraints import FixedJoint
from ..agents.tentacle import Tentacle
from ..objects.graphical import GraphicSettings
from ..image_gen import ImageGeneratorSettings


def initialize_map(engine: Engine):
    engine.player.start_position = (0, 5)
    engine.add_body(
        Box((0, -5), (1000, 5), density=0, graphic_settings=GraphicSettings(draw_sprite=True, image_name="box1"))
    )
    #snake(engine)
    engine.add_container(Tentacle((10, 0)))
    engine.add_container(Tentacle((20, 0), speed=2))



MAPS = [
    [
        [0, 0, 1, 1],
        [0, 0, 1, 1],
        [0, 0, 1, 0],
        [1, 1, 1, 0],
        [1, 0, 0, 0],
        [1, 0, 0, 0],
        [1, 1, 1, 1],
    ],
    [
        [0, 0, 1, 1, 0, 0],
        [0, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1],
        [0, 1, 1, 1, 1, 0],
        [0, 0, 1, 1, 0, 0],
        [0, 0, 1, 1, 0, 0],
        [0, 0, 1, 1, 0, 0],
        [0, 0, 1, 1, 0, 0],
    ],
    [
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 0, 1, 1],
        [1, 1, 0, 0, 0, 0, 1, 1],
        [1, 1, 0, 0, 0, 0, 1, 1],
        [1, 1, 0, 0, 0, 0, 1, 1],
        [1, 1, 0, 0, 0, 0, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
    ],
    [
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
    ]

]


def snake(engine: Engine):
    last_box = None
    for i in range(10):
        box = Box((5+math.sin(i/2), 5+i*1.1), (.5, .5), density=1)
        engine.add_body(box)

        if last_box:
            engine.add_constraint(
                FixedJoint(
                    last_box, box,
                    (0, last_box.extent[1]*.9), (0, -last_box.extent[1]*.9)
                )
            )

        last_box = box


def density_parade(engine: Engine, pos, num_items=30):
    for i in range(num_items):

        extent = (.2, .2)
        density = i + .1
        x = i * extent[0] * 3
        angle = .3
        angular_velocity = -200.

        graphic_settings = GraphicSettings(
            draw_lines=True, draw_sprite=True,
            image_name=ImageGeneratorSettings(
                color=density_color(density), shape="rect"
            ),
        )
        box = Box(
            Vec2d(x, 20) + pos, extent, angle=angle,
            density=density, graphic_settings=graphic_settings,
        )
        box.angular_velocity = angular_velocity
        engine.add_body(box)


def add_from_map(engine: Engine, MAP=None, pos=None, density=None):
    if pos is None:
        pos = Vec2d((0, 20))

    MAP = MAP or random.choice(MAPS)
    density = random.uniform(.5, 25) if density is None else density

    boxes = {}

    do_multi = False
    def _connect(a, b, anchor_a, anchor_b):
        engine.add_constraint(FixedJoint(a, b, anchor_a, anchor_b, breaking_impulse=500))

    extent = random.uniform(.1, 0.6)
    extent_smaller = 1.
    if random.randrange(5) == 0:
        extent_smaller = 1. - random.uniform(0., random.uniform(0., 1.))
    for y, row in enumerate(MAP):
        for x, v in enumerate(row):
            if v:
                local_density = random.uniform(0.1, density)
                graphic_settings = GraphicSettings(
                    draw_lines=True, draw_sprite=True,
                    image_name=ImageGeneratorSettings(
                        color=density_color(local_density), shape="rect"
                    ),
                )
                r = extent * extent_smaller
                box = Box(
                    (x * extent*2 + pos[0], (len(MAP) - y - 1) * extent*2 + pos[1]), (r, r),
                    density=local_density, graphic_settings=graphic_settings,
                )
                boxes[(x, y)] = box
                engine.add_body(box)

                if y > 0 and MAP[y-1][x]:
                    other = boxes[(x, y-1)]
                    if not do_multi:
                        _connect(box, other, (0, box.extent.y), (0, -other.extent.y))
                    else:
                        _connect(box, other, (-box.extent.x, box.extent.y), (-other.extent.x, -other.extent.y))
                        _connect(box, other, (+box.extent.x, box.extent.y), (+other.extent.x, -other.extent.y))

                if x > 0 and MAP[y][x-1]:
                    other = boxes[(x-1, y)]
                    if not do_multi:
                        _connect(box, other, (-box.extent.x, 0), (other.extent.x, 0))
                    else:
                        _connect(box, other, (-box.extent.x, -box.extent.y), (other.extent.x, -other.extent.y))
                        _connect(box, other, (-box.extent.x, +box.extent.y), (other.extent.x, +other.extent.y))



density_color_0 = np.array((.7, .7, .7), dtype=np.float)
density_color_1 = np.array((1, .3, .1), dtype=np.float)
def density_color(density):
    s = max(0, min(1, density / 25))
    c = density_color_0 + s * (density_color_1 - density_color_0)
    return np.round(c * 10) / 10
