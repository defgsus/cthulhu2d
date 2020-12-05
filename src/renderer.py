import math

import pymunk
from pymunk import Vec2d

import pyglet
from pyglet import gl


class Renderer:

    def __init__(self, engine):
        self.engine = engine
        self._permanent_batches = {}
        self._batches = {}
        self._batches_disabled = set()
        self.translation = Vec2d()

    def get_permanent_batch(self, name):
        if name in self._batches_disabled:
            return None
        if name not in self._permanent_batches:
            self._permanent_batches[name] = pyglet.graphics.Batch()
        return self._permanent_batches[name]
    
    def get_batch(self, name):
        if name in self._batches_disabled:
            return None
        if name not in self._batches:
            self._batches[name] = pyglet.graphics.Batch()
        return self._batches[name]

    def is_batch_enabled(self, name):
        return name not in self._batches_disabled

    def set_batch_enabled(self, name, enabled=True):
        if enabled:
            self._batches_disabled.remove(name)
        else:
            self._batches_disabled.add(name)

    def render(self):
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPushMatrix()
        try:
            gl.glLoadIdentity()
            aspect = self.engine.window_size.x / self.engine.window_size.y
            gl.glOrtho(-10*aspect, 10*aspect, -1, 19, -1, 1)

            gl.glTranslatef(-self.translation.x, -self.translation.y, 0)

            self._render_batches()

        finally:
            gl.glPopMatrix()

    def _render_batches(self):
        for g in self.engine.iter_graphics():
            g.render_graphics()

        # print(self._batches, self._permanent_batches)

        for key in self._permanent_batches:
            self._permanent_batches[key].draw()

        for key in tuple(self._batches):
            self._batches[key].draw()
            del self._batches[key]

    def draw_lines(self, batch, vertices):
        vertices = tuple(vertices)
        num_vertices = len(vertices)
        indices = []
        for i in range(num_vertices):
            indices.append(i)
            indices.append((i + 1) % len(vertices))
        return self.draw_lines_indexed(batch, vertices, indices)

    def draw_lines_indexed(self, batch, vertices, indices):
        flat_vertices = []
        for pos in vertices:
            flat_vertices.append(pos.x)
            flat_vertices.append(pos.y)
        batch.add_indexed(
            len(vertices), gl.GL_LINES, None,
            indices,
            ("v2f", flat_vertices),
            )
