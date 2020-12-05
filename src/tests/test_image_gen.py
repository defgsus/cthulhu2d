import unittest

from src.image_gen import ImageGenerator, RGBAImage


class TestImageGen(unittest.TestCase):

    def xx_test_rgba_image(self):
        im = RGBAImage((4, 4))
        self.assertEqual((4, 4, 4), im.pixels.shape)
        im.fill((1, 2, 3))
        im.fill_alpha(im.circle_mask())
        print(im.pixels)

        print(im.to_pyglet())

    def test_uri(self):
        gen = ImageGenerator()
        image = gen.create_from_uri("/gen/?size=23,42&shape=rect")
        print(image)


if __name__ == '__main__':
    unittest.main()
