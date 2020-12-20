"""
Some testbed for "boulder dash" style map creation
"""

import math
import random

import numpy as np

import pymunk
from pymunk import Vec2d

from ..engine import Engine
from ..objects.primitives import Body, Box, Circle, Ngon
from ..objects.constraints import FixedJoint, SpringJoint
from ..agents.tentacle import Tentacle
from ..objects.graphical import GraphicSettings
from ..objects.container import ObjectContainer
from ..image_gen import ImageGeneratorSettings
from .rand import RandomXY


MAP1 = """
# # # # # # # # # # # # # # # # # # # # # # # # # # #
# . . . d d d s . . . . . . . . . . . . . . . . . . #
# . d . . . . s . . . . . . . . . . . . . . . . . . #
# d d d . . . . s . . . . . . . . . . . . . . . . . #
# # # # # # # # . . . . . . . . . . . . . . . . . . #
# . . . . . . . . . . . . . . . . . . . . . . . . . #
# . . . . s s s s . . . . . . . . . . . . . . . . . #
# . . . . s d d s . . . . . . . . . . . . . . . . . #
# . . . . s s s s . . . . . . . . . . . . . . . . . #
# . . . . . . . . . . . . . . . . . . . . . . . . . #
#                                                   #
#                                                   #
#       P                                           #
# # # # # # # # # # # # # # # # # # # # # # # # # # #
"""


def char_to_object(char, x, y):
    if char == "#":
        return Box(
            (x+.5, y+.5), (.5, .5),
            density=0,
            graphic_settings=GraphicSettings(
                draw_sprite=True, 
                image_name=ImageGeneratorSettings(color=(.7, .7, .7))
            )
        )
    if char == ".":
        return Box(
            (x+.5, y+.5), (.5, .5),
            density=0,
            pickable=True,
            graphic_settings=GraphicSettings(
                draw_sprite=True,
                image_name=ImageGeneratorSettings(color=(.6, .3, .0))
            )
        )
    if char == "d":
        return Ngon(
            (x+.5, y+.5), radius=.5, segments=6,
            density=5,
            pickable=True,
            graphic_settings=GraphicSettings(
                #draw_sprite=True,
                #image_name=ImageGeneratorSettings(color=(.7, .7, .7))
            )
        )
    if char == "s":
        return Circle(
            (x+.5, y+.5), .5,
            density=20,
            graphic_settings=GraphicSettings(
                draw_sprite=True, draw_lines=False,
                image_name=ImageGeneratorSettings(shape="circle", color=(.6, .6, .6))
            )
        )
    raise NotImplementedError(f"No object defined for character '{char}'")

    
def initialize_map(engine: Engine, map_str=None):
    map_str = map_str or MAP1
    map_rows = [l.strip() for l in map_str.splitlines() if l.strip()]
    map_rows = [list(row[::2]) for row in map_rows]
    
    container = engine.add_container(ObjectContainer())
    
    for y, row in enumerate(map_rows):
        y = len(map_rows) - 1 - y
        for x, char in enumerate(row):
            if char and char != " ":
                if char == "P":
                    engine.player.start_position = (x+.5, y+.5)
                else:
                    obj = char_to_object(char, x, y)
                    container.add_body(obj)


