import math
import random

import pymunk
from pymunk import Vec2d

from .engine import Engine
from .primitives import Box, Circle
from .constraints import FixedJoint


def initialize_map(engine: Engine):
    engine.player.position = (0, 5)
    engine.add_body(
        Box((0, -5), (1000, 5), density=0)
    )
    snake(engine)


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


def add_from_map(engine: Engine, MAP=None, pos=None, density=None):
    if pos is None:
        pos = Vec2d((0, 20))

    MAP = MAP or random.choice(MAPS)
    density = random.uniform(.5, 25) if density is None else density

    boxes = {}

    do_multi = False
    def _connect(a, b, anchor_a, anchor_b):
        engine.add_constraint(FixedJoint(a, b, anchor_a, anchor_b))

    extent = random.uniform(.1, .5)
    for y, row in enumerate(MAP):
        for x, v in enumerate(row):
            if v:
                r = extent * .9#random.uniform(.2, 1)
                box = Box((x * extent*2 + pos[0], (len(MAP) - y - 1) * extent*2 + pos[1]), (r, r), density=density)
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
