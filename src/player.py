import pymunk
from pymunk import Vec2d

from .primitives import Circle
from .keyhandler import KeyHandler


class Player(Circle):
    def __init__(self, position):
        super().__init__(position=position, radius=.4, density=1)
        self.keys = KeyHandler()
        self.pick_dir = Vec2d()

    def update(self, dt):
        side_speed = 5
        angular_speed = 10
        max_angular_speed = 20
        pick_dir = Vec2d(0, 0)
        if self.keys.is_down("left"):
            pick_dir.x = -1
            speed = 1 + 3 * self.keys.smooth_down("left") + 6 * self.keys.smooth_pressed("left")
            self._body.velocity += (-dt * side_speed * speed, 0)
            if self._body.angular_velocity < max_angular_speed:
                self._body.angular_velocity += dt * angular_speed * speed

        if self.keys.is_down("right"):
            pick_dir.x = 1
            speed = 1 + 3 * self.keys.smooth_down("right") + 6 * self.keys.smooth_pressed("right")
            self._body.velocity -= (-dt * side_speed * speed, 0)
            if self._body.angular_velocity > -max_angular_speed:
                self._body.angular_velocity -= dt * angular_speed * speed

        if self.keys.is_pressed("up"):
            pick_dir.y = 1
            self._body.velocity += (0, 10)

        if self.keys.is_pressed("down"):
            pick_dir.y = -1
            self._body.velocity += (0, -10)#-dt * 30)

        if pick_dir.x or pick_dir.y:
            self.pick_dir = pick_dir.normalized()

        if self.pick_dir.x or self.pick_dir.y:
            if self.keys.is_pressed("pick"):
                self.pick(self.pick_dir)

            if self.keys.is_pressed("put"):
                self.put(self.pick_dir)

        self.keys.update(dt)

    def pick(self, dir):
        pick_pos = self._body.position + dir

        body = self.engine.point_query_nearest_body(pick_pos)
        if body and body.density:
            self.engine.remove_body(body)

    def put(self, dir):
        from .primitives import Box
        put_pos = self.body.position + dir
        self.engine.add_body(
            Box(put_pos, (.5, .5), density=10)
        )

