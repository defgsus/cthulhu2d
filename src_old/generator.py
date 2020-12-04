import math

import pymunk
from pymunk import Vec2d

from .scene import Scene
from .objects import Box


class TreeGenerator:

    def __init__(self, scene: Scene):
        self.scene = scene

    def grow(self, start_pos, start_angle=0., start_scale=.5, mass=5):
        boxes = []
        constraints = []

        pos = Vec2d(start_pos)
        angle = start_angle
        scale = start_scale
        for i in range(25):
            box = Box(pos, (scale, scale), mass=mass, angle=angle)
            boxes.append(box)
            self.scene.add_box(box)

            if len(boxes) > 1:
                self._connect(constraints, boxes[-2], boxes[-1])

            angle += .3 * math.sin(i/3.)
            dir = Vec2d(0, 1).rotated(angle)
            pos += dir * scale * 2.1
            scale *= 0.91

        #for box in boxes:
        #    self.scene.add_box(box)
        self.scene.space.add(*constraints)

    def _connect(self, constraints, box1, box2):
        for index_a, index_b in ((0, 3), (1, 2)):
            anchor1 = self._get_box_anchor(box1, index_a)
            anchor2 = self._get_box_anchor(box2, index_b)
            constraint = pymunk.PinJoint(
                box1.body, box2.body,
                anchor_a=anchor1,
                anchor_b=anchor2,
            )
            constraint.breaking_impulse = 50000
            constraint.collide_bodies = False
            constraints.append(constraint)
            box1.constraints.append(constraint)
            box2.other_constraints.append(constraint)

    def _get_box_anchor(self, box, index):
        """tl, tr, br, bl"""
        if index == 0:
            pos = Vec2d(-box.extent[0], box.extent[1])
        elif index == 1:
            pos = Vec2d(box.extent[0], box.extent[1])
        elif index == 2:
            pos = Vec2d(box.extent[0], -box.extent[1])
        else:  # if index == 3:
            pos = Vec2d(-box.extent[0], -box.extent[1])

        #pos.rotate(box.angle)
        return pos
