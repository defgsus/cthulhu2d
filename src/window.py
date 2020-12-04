import pyglet

from .scene import Scene, MAPS

gl = pyglet.gl


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
        if symbol == ord('t'):
            self.scene.add_tree()
        if symbol == 65307:
            self.close()

        if symbol in self.SYMBOL_TO_PLAYER_KEY:
            self.scene.player.keys.set_key_down(self.SYMBOL_TO_PLAYER_KEY[symbol], True)

    def on_key_release(self, symbol, modifiers):
        if symbol in self.SYMBOL_TO_PLAYER_KEY:
            self.scene.player.keys.set_key_down(self.SYMBOL_TO_PLAYER_KEY[symbol], False)

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

