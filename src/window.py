import time

from pymunk import Vec2d

import pyglet
from pyglet import gl

from .engine import Engine
from .maps import map_gen, bd_map

from .agents.player import Player


class MainWindow(pyglet.window.Window):

    SYMBOL_TO_PLAYER_KEY = {
        65361: "left",
        65362: "up",
        65363: "right",
        65364: "down",
        32: "pick",
        65293: "put",
        115: "shoot",
    }

    def __init__(self, size=None):
        if size:
            super().__init__(width=size[0], height=size[1], fullscreen=False)
        else:
            super().__init__(fullscreen=True)
        self.fps_display = pyglet.window.FPSDisplay(self)
        self.engine = Engine()

        self.engine.player = Player((0, 1))
        self.engine.add_container(self.engine.player)
        #map_gen.initialize_map_2(self.engine)
        bd_map.initialize_map(self.engine)

        self.do_render = True
        self.do_physics = True
        self.do_print_sensors = False
        self._last_render_time = time.time()

    def on_key_press(self, symbol, modifiers):
        print("KEY", symbol, modifiers)
        if symbol == ord('f'):
            self.set_fullscreen(not self.fullscreen)
        #if symbol == ord('1'):
        #    self.engine.add_more()
        if ord('1') <= symbol < (ord('1') + len(map_gen.MAPS)):
            pos = self.engine.player.position + (0, 20)
            map_gen.add_from_map(self.engine, map_gen.MAPS[symbol - ord('1')], pos=pos)
        if symbol == ord('x'):
            map_gen.density_parade(self.engine, self.engine.player.position)
        if symbol == ord('g'):
            self.do_render = not self.do_render
        if symbol == ord('p'):
            self.do_physics = not self.do_physics
        if symbol == ord('s'):
            self.do_print_sensors = not self.do_print_sensors
        if symbol == ord('d'):
            self.engine.container.dump_tree()
            self.engine.renderer.set_batch_enabled(
                "lines", not self.engine.renderer.is_batch_enabled("lines")
            )
        #if symbol == ord('t'):
        #    self.engine.add_tree()
        if symbol == 65307:
            self.close()

        if symbol in self.SYMBOL_TO_PLAYER_KEY:
            self.engine.player.keys.set_key_down(self.SYMBOL_TO_PLAYER_KEY[symbol], True)

    def on_key_release(self, symbol, modifiers):
        if symbol in self.SYMBOL_TO_PLAYER_KEY:
            self.engine.player.keys.set_key_down(self.SYMBOL_TO_PLAYER_KEY[symbol], False)

    def on_mouse_press(self, x, y, button, modifiers):
        map_pos = self.engine.renderer.pixel_to_map(Vec2d(x, y))
        body = self.engine.point_query_body(map_pos)
        if body:
            print()
            body.dump()
        #print(map_pos, body)

    def set_projection(self):
        aspect = self.width / self.height
        gl.glOrtho(-10*aspect, 10*aspect, -1, 19, -1, 1)

    def on_draw(self):
        render_time = time.time()
        dt = render_time - self._last_render_time
        self._last_render_time = render_time

        self.clear()
        if not self.do_render:
            return

        self.engine.window_size = (self.width, self.height)
        self.engine.render(dt)

        self.fps_display.draw()

    def update(self, dt):
        # print(dt)
        if self.do_physics:
            self.engine.update(dt)
            if self.do_print_sensors and hasattr(self.engine.player, "dump_sensors"):
                self.engine.player.dump_sensors(dt)


if __name__ == "__main__":
    window = MainWindow((640, 480))
    pyglet.clock.schedule_interval(window.update, 1 / 60.0)
    pyglet.app.run()

