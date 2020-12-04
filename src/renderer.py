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
        self._translation = Vec2d()

    def get_permanent_batch(self, name):
        if name not in self._permanent_batches:
            self._permanent_batches[name] = pyglet.graphics.Batch()
        return self._permanent_batches[name]
    
    def get_batch(self, name):
        if name not in self._batches:
            self._batches[name] = pyglet.graphics.Batch()
        return self._batches[name]

    def render(self):
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPushMatrix()
        try:
            gl.glLoadIdentity()
            aspect = self.engine.window_size.x / self.engine.window_size.y
            gl.glOrtho(-10*aspect, 10*aspect, -1, 19, -1, 1)

            gl.glTranslatef(-self._translation.x, -self._translation.y, 0)

            self._render_batches()

        finally:
            gl.glPopMatrix()

    def _render_batches(self):
        for key in self._permanent_batches:
            self._permanent_batches[key].draw()

        for key in self._batches:
            self._batches[key].draw()
            del self._batches[key]
