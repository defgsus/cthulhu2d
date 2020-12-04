
import math
import random
from typing import List

import pyglet

import pymunk
from pymunk import Vec2d

from .objects import Box, Player

gl = pyglet.gl



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

class Scene:

    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = Vec2d(0.0, -10.0)
        self.box_images = []
        for name in ("box0.png", "box1.png", "box2.png", "box3.png"):
            image = pyglet.image.load(name)
            image.anchor_x = image.width // 2
            image.anchor_y = image.height // 2
            self.box_images.append(image)
        self.box_batch = pyglet.graphics.Batch()
        self.boxes: List[Box] = []
        self.body_to_box = dict()
        self.debug_render = True
        self.player_image = pyglet.image.load("player1.png")
        self.player_image.anchor_x = self.player_image.width // 2
        self.player_image.anchor_y = self.player_image.height // 2
        self.player = None
        self.add_player((-10, 2))
        self.map_offset = Vec2d()
        self.physics_pause = False

    def add_player(self, pos):
        self.player = Player(pos)
        self.player.scene = self
        self.player.create_pymunk()
        self.player.create_pyglet(self.player_image, self.box_batch)
        self.space.add(self.player.body, self.player.shape)

    def add_box(self, box: Box, image=None):
        if image is None:
            image = self.box_images[max(0, min(len(self.box_images)-1, int(box.mass / 20 * len(self.box_images))))]
        self.boxes.append(box)
        box.create_pymunk()
        box.create_pyglet(image, self.box_batch)
        self.space.add(box.body, box.shape)
        self.body_to_box[box.body] = box

    def add_tree(self, pos=None):
        from .generator import TreeGenerator
        self.physics_pause = True
        if pos is None:
            pos = (random.uniform(-5, 5) + self.player.pos.x, 0.5)

        gen = TreeGenerator(self)
        gen.grow(start_pos=pos)
        self.physics_pause = False

    def remove_box(self, box: Box):
        for c in box.constraints + box.other_constraints:
            if c in self.space.constraints:
                self.space.remove(c)
        self.space.remove(box.shape, box.body)
        self.body_to_box.pop(box.body, None)
        self.boxes = list(filter(lambda b: b != box, self.boxes))
        box.sprite.delete()
        box.sprite = None

    def add_some_objects(self):
        self.add_box(Box((0, -.25), (200, .25), mass=0))
        #self.objects.append(Box((0, 10), (.5, .5)))
        self.add_map(MAPS[1], pos=(0, 0), mass=20)
        self.add_map(MAPS[3], pos=(-20, 0), mass=10)

    def add_more(self):
        self.add_box(
            Box(self.player.pos + (random.uniform(-3, 3), 10), (.5, .5), mass=1)
        )

    def add_map(self, MAP=None, pos=None, mass=None):
        if pos is None:
            pos = Vec2d(self.player.pos) + (0, random.uniform(10, 20))

        mass = mass or random.uniform(.5, 25)

        MAP = MAP or random.choice(MAPS)
        image = None#self.box_images[min(len(self.box_images)-1, int(mass / 5))]

        boxes = {}

        do_multi = False
        def _connect(a, b, anchor_a, anchor_b):
            constraint = pymunk.PinJoint(
                a.body, b.body,
                anchor_a=Vec2d(anchor_a) * .95,
                anchor_b=Vec2d(anchor_b) * .95,
                #min=0, max=1 * .3,
            )
            constraint.error_bias = 0.000001
            #constraint.max_bias = 100.
            constraint.breaking_impulse = random.uniform(40, 100) * mass * 5
            a.constraints.append(constraint)
            b.other_constraints.append(constraint)
            self.space.add(constraint)

        extent = random.uniform(.1, .5)
        for y, row in enumerate(MAP):
            for x, v in enumerate(row):
                if v:
                    r = extent * .9#random.uniform(.2, 1)
                    box = Box((x * extent*2 + pos[0], (len(MAP) - y - 1) * extent*2 + pos[1]), (r, r), mass=mass)
                    boxes[(x, y)] = box
                    self.add_box(box, image=image)

                    if y > 0 and MAP[y-1][x]:
                        other = boxes[(x, y-1)]
                        if not do_multi:
                            _connect(box, other, (0, box.extent[1]), (0, -other.extent[1]))
                        else:
                            _connect(box, other, (-box.extent[0], box.extent[1]), (-other.extent[0], -other.extent[1]))
                            _connect(box, other, (+box.extent[0], box.extent[1]), (+other.extent[0], -other.extent[1]))

                    if x > 0 and MAP[y][x-1]:
                        other = boxes[(x-1, y)]
                        if not do_multi:
                            _connect(box, other, (-box.extent[0], 0), (other.extent[0], 0))
                        else:
                            _connect(box, other, (-box.extent[0], -box.extent[1]), (other.extent[0], -other.extent[1]))
                            _connect(box, other, (-box.extent[0], +box.extent[1]), (other.extent[0], +other.extent[1]))

    def render(self):
        for box in self.boxes:
            box.get_transform()
        self.player.get_transform()
        self.box_batch.draw()

        if self.debug_render:
            self.render_boxes_lines()
            self.render_constraints()

    def render_constraints(self):
        batch = pyglet.graphics.Batch()
        for c in self.space.constraints:
            p1 = c.a.position + c.anchor_a.rotated(c.a.angle)
            p2 = c.b.position + c.anchor_b.rotated(c.b.angle)
            f = 0#(p2 - p1).normalized() * min(.3, 0.01 + c.impulse)
            p1 -= f
            p2 += f
            batch.add(
                2, gl.GL_LINES, None,
                ("v2f", (p1.x, p1.y, p2.x, p2.y)),
            )
        batch.draw()

    def render_boxes_lines(self):
        batch = pyglet.graphics.Batch()
        for box in self.boxes:
            self.render_box_line(batch, box)
        batch.draw()

    def render_box_line(self, batch, box):
        vertices = []
        for corner in (
                (-1, 1), (1, 1),
                (1, 1), (1, -1),
                (1, -1), (-1, -1),
                (-1, -1), (-1, 1),
        ):
            pos = box.pos + (box.extent * corner).rotated(box.angle)
            #if len(vertices) > 1:
            #    vertices += vertices[-2:]
            vertices.append(pos.x)
            vertices.append(pos.y)
        batch.add(
            len(vertices) // 2, gl.GL_LINES, None,
            ("v2f", vertices),
        )

    def update(self, dt):
        if self.physics_pause:
            return

        fixed_dt = 1. / 60.
        self.player.update(dt)
        self.map_offset += dt * (self.player.pos - Vec2d(1, 3) - self.map_offset) * (1, 0)
        for i in range(10):
            self.space.step(fixed_dt / 10.)
        for c in self.space.constraints:
            if c.impulse / fixed_dt > c.breaking_impulse:
                box = self.body_to_box[c.a]
                for c2 in box.constraints:
                    if c2 in self.space.constraints:
                        self.space.remove(c2)
                box.constraints.clear()

