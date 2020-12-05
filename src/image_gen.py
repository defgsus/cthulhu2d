import re
from urllib import parse as parse_url

import pyglet
import numpy as np

from .parameterized import Parameterized


class ImageGeneratorSettings(Parameterized):

    TUPLE_KEYS = ("size", "color")

    def __init__(
            self,
            shape="rect",
            size=(32, 32),
            color=(1, 1, 1, 1),
    ):
        super().__init__()
        self.shape = shape
        self.size = size
        self.color = color

    def to_dict(self):
        return {
            **super().to_dict(),
            "shape": self.shape,
            "size": self.size,
            "color": self.color,
        }

    def to_uri(self):
        query = dict()
        parameters = self.to_dict()
        for key in sorted(parameters):
            value = parameters[key]
            if key in self.TUPLE_KEYS:
                value = ",".join(str(v) for v in value)

            query[key] = str(value)

        return f"gen/?" + "&".join(f"{key}={value}" for key, value in query.items())

    @classmethod
    def from_uri(cls, uri):
        url = parse_url.urlsplit(uri)
        query = parse_url.parse_qs(url.query)
        settings = cls()
        for key, value in query.items():
            value = value[0]
            if key in cls.TUPLE_KEYS:
                value = tuple(value.split(","))
                if key == "size":
                    value = tuple(int(v) for v in value)
                else:
                    value = tuple(float(v) for v in value)

            setattr(settings, key, value)
        return settings


class ImageGenerator:
    """
    Generates images from uris

    gen/?size=32,32&shape=rect ...

    """

    def __init__(self):
        pass

    def create_from_uri(self, uri):
        settings = ImageGeneratorSettings.from_uri(uri)
        return self.create_from_settings(settings)

    def create_from_settings(self, settings: ImageGeneratorSettings):
        image = RGBAImage(settings.size)
        image.fill(settings.color)

        if settings.shape == "rect":
            image.add_mask(image.rect_bevel_mask())

        elif settings.shape == "circle":
            image.fill_alpha(image.circle_mask())

        return image.to_pyglet()


class RGBAImage:

    def __init__(self, size):
        self.size = size
        self.pixels = np.zeros((size[1], size[0], 4), dtype=np.float)
        self.fill_alpha(1)

    def to_pyglet(self):
        byte_array = self.pixels * 255
        byte_array = np.clip(byte_array, 0, 255)
        byte_array = np.array(byte_array, dtype=np.uint8)
        data = byte_array.flatten()
        data = bytes(data)
        return pyglet.image.ImageData(
            width=self.size[0],
            height=self.size[1],
            format="RGBA",
            data=data,
        )

    def fill(self, vec):
        self.pixels[:, :, :len(vec)] = vec

    def fill_alpha(self, a):
        self.pixels[:, :, -1:] = a

    def add_mask(self, mask):
        self.pixels += mask

    def circle_mask(self, center=None, radius=None):
        if radius is None:
            radius = .5
        if center is None:
            center = (.5, .5)

        max_size = max(*self.size)
        mask = np.ndarray((self.size[1], self.size[0], 1), dtype=np.float)
        for y in range(mask.shape[0]):
            yf = y / (mask.shape[0] - 1)
            for x in range(mask.shape[1]):
                xf = x / (mask.shape[1] - 1)
                dist = np.sqrt((xf - center[0])**2 + (yf - center[1])**2)
                step = max(0, min(1, (radius - dist) * max_size + 1))
                mask[y][x][0] = step

        return mask

    def rect_bevel_mask(self, padding=.2, amount=.1):
        mask = np.ndarray((self.size[1], self.size[0], 1), dtype=np.float)
        for y in range(mask.shape[0]):
            yf = y / (mask.shape[0] - 1)
            for x in range(mask.shape[1]):
                xf = x / (mask.shape[1] - 1)
                value = max(0., padding - xf) + \
                    max(0., padding - yf) + \
                    min(0., 1. - padding - xf) + \
                    min(0., 1. - padding - yf)
                mask[y][x][0] = value / padding * amount
        return mask

