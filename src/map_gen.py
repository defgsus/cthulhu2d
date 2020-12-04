import math, random

from .engine import Engine
from .primitives import Box, Circle
from .constraints import FixedJoint


def generate_map(engine: Engine):
    engine.player.position = (0, 5)
    engine.add_body(
        Box((0, -5), (1000, 5), density=0)
    )

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
