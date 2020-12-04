import os

import pyglet


class Images:

    def __init__(self, base_path=None):
        if base_path is None:
            base_path = os.path.abspath(os.path.dirname(__file__))
        self.base_path = base_path
        self._centered_images = {}

    def centered_image(self, name):
        if name not in self._centered_images:
            image = self._load_image(name)
            image.anchor_x = image.width // 2
            image.anchor_y = image.height // 2
            self._centered_images[name] = image
        return self._centered_images[name]

    def _load_image(self, name):
        return pyglet.image.load(os.path.join(f"{name}.png"))

