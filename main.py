import pyglet

from src.window import MainWindow


if __name__ == "__main__":
    window = MainWindow((640, 480))
    pyglet.clock.schedule_interval(window.update, 1 / 60.0)
    pyglet.app.run()

