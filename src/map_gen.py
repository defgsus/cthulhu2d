import math, random

from .engine import Engine
from .primitives import Box, Circle


def generate_map(engine: Engine):
    engine.add_body(
        Box((0, -5), (1000, 5), density=0)
    )
    for i in range(10):
        engine.add_body(
            Box((5+math.sin(i/2), 5+i*1.1), (.5, .5), density=1)
        )
    engine.player.position = (0, 5)
