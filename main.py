import argparse

import pyglet

from src.window import MainWindow


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-fs", "--fullscreen", type=bool, nargs="?", default=False, const=True,
        help="Start in fullscreen mode"
    )

    return parser.parse_args()


if __name__ == "__main__":
    options = parse_arguments()
    size = None if options.fullscreen else (640, 480)

    window = MainWindow(size=size)
    pyglet.clock.schedule_interval(window.update, 1 / 60.0)
    pyglet.app.run()

