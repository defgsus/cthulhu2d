
import math
import random
from typing import List

import pyglet

import pymunk
from pymunk import Vec2d

from .keyhandler import KeyHandler

gl = pyglet.gl


class Box:

    def __init__(self, pos, extent, angle=0, mass=0):
        self.pos = Vec2d(pos)
        self.extent = Vec2d(extent)
        self.angle = angle
        self.mass = mass
        self.body = None
        self.shape = None
        self.sprite = None
        self.constraints = []
        self.other_constraints = []

    def create_pymunk(self):
        if not self.mass:
            self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        else:
            self.body = pymunk.Body()

        self.shape = pymunk.Poly.create_box(self.body, self.extent * 2)
        self.shape.mass = self.mass
        self.shape.friction = 1.0
        self.shape.elasticity = 0.

        self.body.position = Vec2d(self.pos)
        if self.mass:
            self.body.angle = self.angle

    def create_pyglet(self, box_image, box_batch):
        sprite = pyglet.sprite.Sprite(box_image, batch=box_batch, subpixel=True)
        sprite.scale = 1. / sprite.width
        sprite.scale_x *= self.extent[0] * 2
        sprite.scale_y *= self.extent[1] * 2
        self.sprite = sprite

    def get_transform(self):
        #print(body.position, body.position.angle)
        self.pos = (self.body.position.x, self.body.position.y)
        self.angle = self.body.angle
        if self.sprite:
            self.sprite.x, self.sprite.y = self.pos
            self.sprite.rotation = -self.angle * 180 / math.pi


class Player:

    def __init__(self, pos, radius=.4, mass=50):
        from .scene import Scene
        self.mass = mass
        self.radius = radius
        self.pos = Vec2d(pos)
        self.body = None
        self.shape = None
        self.sprite = None
        self.scene: Scene = None
        self.keys = KeyHandler()
        self.pick_dir = Vec2d(0, 0)

    def create_pymunk(self):
        self.body = pymunk.Body()

        if 1:
            self.shape = pymunk.Circle(self.body, self.radius)
        else:
            r = self.radius
            self.shape = pymunk.Poly(self.body, [(-r, -r), (r, -r), (0, r)])
        self.shape.mass = self.mass
        self.shape.friction = .4
        self.shape.elasticity = 0

        self.body.position = Vec2d(self.pos)

    def create_pyglet(self, image, batch):
        sprite = pyglet.sprite.Sprite(image, batch=batch, subpixel=True)
        sprite.scale = 1. / sprite.width
        sprite.scale_x *= self.radius * 2
        sprite.scale_y *= self.radius * 2
        self.sprite = sprite

    def get_transform(self):
        #print(body.position, body.position.angle)
        self.pos = self.body.position
        self.angle = self.body.angle

        self.sprite.x, self.sprite.y = self.pos
        self.sprite.rotation = -self.angle * 180 / math.pi

    def update(self, dt):
        side_speed = 5
        angular_speed = 10
        max_angular_speed = 20
        pick_dir = Vec2d(0, 0)
        if self.keys.is_down("left"):
            pick_dir.x = -1
            speed = 1 + 3 * self.keys.smooth_down("left") + 6 * self.keys.smooth_pressed("left")
            self.body.velocity += (-dt * side_speed * speed, 0)
            if self.body.angular_velocity < max_angular_speed:
                self.body.angular_velocity += dt * angular_speed * speed

        if self.keys.is_down("right"):
            pick_dir.x = 1
            speed = 1 + 3 * self.keys.smooth_down("right") + 6 * self.keys.smooth_pressed("right")
            self.body.velocity -= (-dt * side_speed * speed, 0)
            if self.body.angular_velocity > -max_angular_speed:
                self.body.angular_velocity -= dt * angular_speed * speed

        if self.keys.is_pressed("up"):
            pick_dir.y = 1
            self.body.velocity += (0, 10)

        if self.keys.is_pressed("down"):
            pick_dir.y = -1
            self.body.velocity += (0, -10)#-dt * 30)

        if pick_dir.x or pick_dir.y:
            self.pick_dir = pick_dir.normalized()

        if self.pick_dir.x or self.pick_dir.y:
            if self.keys.is_pressed("pick"):
                self.pick(self.pick_dir)

            if self.keys.is_pressed("put"):
                self.put(self.pick_dir)

        self.keys.update(dt)

    def pick(self, dir):
        pick_pos = self.body.position + dir
        hit = self.scene.space.point_query_nearest(pick_pos, 0, pymunk.ShapeFilter())
        if hit and hit.shape:
            shape = hit.shape
            box = self.scene.body_to_box.get(shape.body)
            if box and box.mass:
                self.scene.remove_box(box)

    def put(self, dir):
        put_pos = self.body.position + dir
        self.scene.add_box(
            Box(put_pos, (.5, .5), mass=10)
        )
