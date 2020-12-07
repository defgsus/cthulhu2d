import unittest

from ..engine import Engine
from ..objects.container import ObjectContainer
from ..objects.primitives import Box
from ..objects.graphical import GraphicSettings

sprite_settings = GraphicSettings(draw_sprite=True, image_name="gen/")


class TestContainer(unittest.TestCase):

    def assertHasPhysicsBody(self, *objects, assert_true=True):
        for obj in objects:
            condition = bool(getattr(obj, "_body", None))
            if (condition and not assert_true) or (not condition and assert_true):
                raise AssertionError(
                    f"Expected physics body == {assert_true} for {obj}"
                )

    def assertHasGraphics(self, *objects, assert_true=True):
        for obj in objects:
            condition = bool(getattr(obj, "_graphics", None))
            if (condition and not assert_true) or (not condition and assert_true):
                raise AssertionError(
                    f"Expected graphics == {assert_true} for {obj}"
                )

    def test_nested_container(self):
        engine = Engine()
        box = engine.add_body(Box((0, 0), (1, 1), graphic_settings=sprite_settings))

        sub_cont = engine.add_container(ObjectContainer())
        sub_box = sub_cont.add_body(Box((10, 0), (1, 1), graphic_settings=sprite_settings))

        sub_sub_cont = sub_cont.add_container(ObjectContainer())
        sub_sub_box = sub_sub_cont.add_body(Box((20, 0), (1, 1), graphic_settings=sprite_settings))
        sub_sub_box_2 = sub_sub_cont.add_body(Box((22, 0), (1, 1), graphic_settings=sprite_settings))

        self.assertHasPhysicsBody(box, sub_box, sub_sub_box, sub_sub_box_2, assert_true=False)
        self.assertHasGraphics(box, sub_box, sub_sub_box, sub_sub_box_2, assert_true=False)

        engine.update(1/60)
        engine.render(1/60)
        engine.dump()

        self.assertHasPhysicsBody(box, sub_box, sub_sub_box, sub_sub_box_2)
        self.assertHasGraphics(box, sub_box, sub_sub_box, sub_sub_box_2)


if __name__ == '__main__':
    unittest.main()
