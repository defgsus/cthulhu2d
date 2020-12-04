
import math
import random
from typing import List

import pyglet

import pymunk
from pymunk import Vec2d

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
        self.mass = mass
        self.radius = radius
        self.pos = Vec2d(pos)
        self.body = None
        self.shape = None
        self.scene: Scene = None
        self.keys_down = set()
        self.is_jump = False
        self.is_pick = False
        self.is_put = False
        self.pick_dir = (1, 0)

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
        if "left" in self.keys_down:
            pick_dir.x = -1
            self.body.velocity += (-dt * side_speed, 0)
            if self.body.angular_velocity < max_angular_speed:
                self.body.angular_velocity += dt * angular_speed
        if "right" in self.keys_down:
            pick_dir.x = 1
            self.body.velocity -= (-dt * side_speed, 0)
            if self.body.angular_velocity > -max_angular_speed:
                self.body.angular_velocity -= dt * angular_speed

        if "up" in self.keys_down:
            pick_dir.y = 1
            if not self.is_jump:
                self.is_jump = True
                self.body.velocity += (0, 10)
        else:
            self.is_jump = False

        if "down" in self.keys_down:
            pick_dir.y = -1
            self.body.velocity += (0, -10)#-dt * 30)

        if pick_dir.x or pick_dir.y:
            self.pick_dir = pick_dir.normalized()

        if "pick" in self.keys_down:
            if not self.is_pick and (self.pick_dir.x or self.pick_dir.y):
                self.pick(self.pick_dir)
        else:
            self.is_pick = False

        if "put" in self.keys_down:
            if not self.is_put and (self.pick_dir.x or self.pick_dir.y):
                self.put(self.pick_dir)
        else:
            self.is_put = False

    def pick(self, dir):
        self.is_pick = True
        pick_pos = self.body.position + dir
        hit = self.scene.space.point_query_nearest(pick_pos, 0, pymunk.ShapeFilter())
        if hit and hit.shape:
            shape = hit.shape
            box = self.scene.body_to_box.get(shape.body)
            if box and box.mass:
                self.scene.remove_box(box)

    def put(self, dir):
        self.is_put = True
        put_pos = self.body.position + dir
        self.scene.add_box(
            Box(put_pos, (.5, .5), mass=10)
        )


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
        for name in ("box1.png", "box2.png"):
            image = pyglet.image.load(name)
            image.anchor_x = image.width // 2
            image.anchor_y = image.height // 2
            self.box_images.append(image)
        self.box_batch = pyglet.graphics.Batch()
        self.boxes: List[Box] = []
        self.body_to_box = dict()
        self.debug_render = False
        self.player_image = pyglet.image.load("player1.png")
        self.player_image.anchor_x = self.player_image.width // 2
        self.player_image.anchor_y = self.player_image.height // 2
        self.player = None
        self.add_player((-10, 2))
        self.map_offset = Vec2d()

    def add_player(self, pos):
        self.player = Player(pos)
        self.player.scene = self
        self.player.create_pymunk()
        self.player.create_pyglet(self.player_image, self.box_batch)
        self.space.add(self.player.body, self.player.shape)

    def add_box(self, box: Box, image=None):
        if image is None:
            image = random.choice(self.box_images)
        self.boxes.append(box)
        box.create_pymunk()
        box.create_pyglet(image, self.box_batch)
        self.space.add(box.body, box.shape)
        self.body_to_box[box.body] = box

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
        self.add_map(MAPS[1], pos=(0, 0), mass=100)
        self.add_map(MAPS[3], pos=(-20, 0), mass=10)

    def add_more(self):
        self.add_box(
            Box(self.player.pos + (random.uniform(-3, 3), 10), (.5, .5), mass=1)
        )

    def add_map(self, MAP=None, pos=None, mass=None):
        if pos is None:
            pos = Vec2d(self.player.pos) + (0, random.uniform(10, 20))

        mass = mass or random.choice((2, 10))

        MAP = MAP or random.choice(MAPS)
        image = self.box_images[min(len(self.box_images)-1, int(mass / 5))]

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
            
        for y, row in enumerate(MAP):
            for x, v in enumerate(row):
                if v:
                    box = Box((x + pos[0], len(MAP) - y - .5 + pos[1]), (.5, .5), mass=mass)
                    boxes[(x, y)] = box
                    self.add_box(box, image=image)

                    if y > 0 and MAP[y-1][x]:
                        other = boxes[(x, y-1)]
                        if not do_multi:
                            _connect(box, other, (0, box.extent[1]), (0, -box.extent[1]))
                        else:
                            _connect(box, other, (-box.extent[0], box.extent[1]), (-box.extent[0], -box.extent[1]))
                            _connect(box, other, (+box.extent[0], box.extent[1]), (+box.extent[0], -box.extent[1]))

                    if x > 0 and MAP[y][x-1]:
                        other = boxes[(x-1, y)]
                        if not do_multi:
                            _connect(box, other, (-box.extent[0], 0), (box.extent[0], 0))
                        else:
                            _connect(box, other, (-box.extent[0], -box.extent[1]), (box.extent[0], -box.extent[1]))
                            _connect(box, other, (-box.extent[0], +box.extent[1]), (box.extent[0], +box.extent[1]))

    def render(self):
        for box in self.boxes:
            box.get_transform()
        self.player.get_transform()
        self.box_batch.draw()

        if self.debug_render:
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

    def update(self, dt):
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


class MainWindow(pyglet.window.Window):

    SYMBOL_TO_PLAYER_KEY = {
        65361: "left",
        65362: "up",
        65363: "right",
        65364: "down",
        32: "pick",
        65293: "put",
    }

    def __init__(self, size):
        #super().__init__(width=size[0], height=size[1], fullscreen=False)
        super().__init__(fullscreen=True)
        self.fps_display = pyglet.window.FPSDisplay(self)
        self.scene = Scene()
        self.scene.add_some_objects()
        self.do_render = True
        self.do_physics = True
        self.label = pyglet.text.Label('Label',
                                       font_name='Times New Roman',
                                       font_size=36,
                                       x=self.width//2, y=self.height//2,
                                       anchor_x='center', anchor_y='center')

    def on_key_press(self, symbol, modifiers):
        print("KEY", symbol, modifiers)
        if symbol == ord('f'):
            self.set_fullscreen(not self.fullscreen)
        if symbol == ord('1'):
            self.scene.add_more()
        if ord('2') <= symbol <= (ord('1') + len(MAPS)):
            self.scene.add_map(MAPS[symbol - ord('2')])
        if symbol == ord('g'):
            self.do_render = not self.do_render
        if symbol == ord('p'):
            self.do_physics = not self.do_physics
        if symbol == ord('d'):
            self.scene.debug_render = not self.scene.debug_render
        if symbol == 65307:
            self.close()

        if symbol in self.SYMBOL_TO_PLAYER_KEY:
            self.scene.player.keys_down.add(self.SYMBOL_TO_PLAYER_KEY[symbol])

    def on_key_release(self, symbol, modifiers):
        if symbol in self.SYMBOL_TO_PLAYER_KEY:
            self.scene.player.keys_down.remove(self.SYMBOL_TO_PLAYER_KEY[symbol])

    def set_projection(self):
        aspect = self.width / self.height
        gl.glOrtho(-10*aspect, 10*aspect, -1, 19, -1, 1)

    def on_draw(self):
        self.clear()
        if not self.do_render:
            return

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPushMatrix()
        try:
            gl.glLoadIdentity()
            self.set_projection()
            gl.glTranslatef(-self.scene.map_offset.x, -self.scene.map_offset.y, 0)

            # does not work..
            # gl.glColor3f(0, 0, 1)
            # gl.glClear(gl.GL_COLOR_BUFFER_BIT)# | gl.GL_DEPTH_BUFFER_BIT)

            #pyglet.graphics.draw(3, gl.GL_TRIANGLES, (
            #    "v2f", (-.5, -.5,   .5, -.5,   .5, .5)
            #))

            self.scene.render()

        finally:
            gl.glPopMatrix()

        #self.label.draw()

        self.fps_display.draw()

    def update(self, dt):
        # print(dt)
        if self.do_physics:
            self.scene.update(dt)


if __name__ == "__main__":
    window = MainWindow((640, 480))
    pyglet.clock.schedule_interval(window.update, 1 / 60.0)
    pyglet.app.run()

