"""
Some testbed for map creation
"""

import math
import random

import numpy as np

import pymunk
from pymunk import Vec2d

from ..engine import Engine
from ..objects.primitives import Body, Box, Circle
from ..objects.constraints import FixedJoint, SpringJoint
from ..agents.tentacle import Tentacle
from ..objects.graphical import GraphicSettings
from ..objects.container import ObjectContainer
from ..objects.heightfield import Heightfield
from ..image_gen import ImageGeneratorSettings
from .rand import RandomXY


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


def initialize_map(engine: Engine):
    random_surroundings(engine, (-30, -20), (30, 20))
    engine.player.start_position = (0, 10)

    if 0:
        engine.add_body(
            Box((0, -30), (1000, 5), density=0, graphic_settings=GraphicSettings(draw_sprite=True, image_name="box1"))
        )
    else:
        engine.add_body(random_heightfield())


def initialize_map_2(engine: Engine):
    engine.player.start_position = (-3, 5)
    if 0:
        engine.add_body(
            Box((0, -5), (1000, 5), density=0, graphic_settings=GraphicSettings(draw_sprite=True, image_name="box1"))
        )
    else:
        engine.add_body(random_heightfield())

    top_box = engine.add_body(
        Box((15, 15), (1, .5), density=0)
    )
    stone = engine.add_body(
        Circle((10, 10), .5, density=10)
    )
    #snake(engine)
    rope(engine, top_box, stone)
    engine.add_container(Tentacle((10, 0)))
    engine.add_container(Tentacle((20, 0), speed=2))




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


def rope(container: ObjectContainer, body_a: Body, body_b: Body, num_segments=10):
    direction = (body_b.position - body_a.position).normalized()
    length = (body_b.position - body_a.position).get_length()
    bodies = [body_a]
    pos = Vec2d(body_a.position)
    for i in range(num_segments + 1):
        pos += direction * length / (num_segments + 2)
        if i < num_segments:
            bodies.append(container.add_body(
                Circle(
                    pos, .1, default_shape_filter=pymunk.ShapeFilter(mask=0), density=10,
                    graphic_settings=GraphicSettings(draw_lines=False)
                )
            ))
        else:
            bodies.append(body_b)

        if len(bodies) >= 2:
            container.add_constraint(
                #FixedJoint(bodies[-2], bodies[-1], (0, 0), (0, 0), breaking_impulse=0)
                SpringJoint(bodies[-2], bodies[-1], (0, 0), (0, 0), breaking_impulse=0)
            )


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


def random_surroundings(container, top_left, bottom_right, noise_range=(0, .5), scale=(1, 1), noise_scale=(.2, .2)):
    extent = Vec2d(scale) * .49
    rnd = RandomXY(1)
    for y in range(top_left[1], bottom_right[1]):
        for x in range(top_left[0], bottom_right[0]):
            n = rnd.fractal_noise(x * noise_scale[0], y * noise_scale[1])
            x = x * scale[0]
            y = y * scale[1]
            if noise_range[0] <= n <= noise_range[1]:
                density = 0
                if rnd.random(x, y, 23) < .4:
                    density = 10

                color = np.array((n, n, n), dtype=np.float)
                color = np.power(color, (1.2, 1.21, 1.22))
                if density:
                    color = np.power(color, (1, 1.5, 1))
                color = (color - noise_range[0]) / (noise_range[1] - noise_range[0])
                color = .8 - .6 * color
                color = np.round(color * 10) / 10
                sprite_settings = GraphicSettings(
                    draw_lines=True,
                    draw_sprite=True,
                    image_name=ImageGeneratorSettings(
                        shape="rect",
                        color=color,
                    )
                )
                body = Box((x, y), extent, density=density, graphic_settings=sprite_settings)

                container.add_body(body)


def uneven_floor_coordinates(
        center_x, y, width,
        spacing_min=.5, spacing_max=2,
        amount=.3,
        height=2.,
        rnd=None,
):
    assert spacing_min > 0
    assert spacing_max >= spacing_min
    assert height > amount

    rnd = rnd or random.Random()

    x_start, x_end = center_x - width // 2, center_x + width // 2
    x = x_start
    coordinates = []
    while x < x_end:
        displacement = rnd.uniform(0., amount)
        coordinates.append((x, y - displacement))
        x += rnd.uniform(spacing_min, spacing_max)

    coordinates += [
        (x_end, y),
        (x_end, y - height),
        (x_start, y - height),
    ]

    return coordinates


def random_heightfield(pos=(0, -2), extent=(60, 2), amount=0, num_samples=200, seed=23):
    rnd = RandomXY(seed)

    def _noise(t):
        return rnd.noise(t * 200, 0)

    return Heightfield(
        position=pos,
        extent=extent,
        height_func=_noise,
        amount=amount,
        num_samples=num_samples,
    )
