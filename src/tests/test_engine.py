import math
import unittest

from ..engine import Engine
from ..objects.container import ObjectContainer
from ..objects.primitives import Box, Circle
from ..objects.graphical import GraphicSettings


class TestEngine(unittest.TestCase):

    def assertTrace(self, hit, body=None, position=None):
        if not hit:
            raise AssertionError("Expected hit, got None")

        if body is not None:
            if body != hit.body:
                raise AssertionError(
                    f"Expected hit {body.short_name()}, got hit {hit.body.short_name()}\nin {hit}"
                )

        if position is not None:
            self.assertAlmostEqual(
                position[0], hit.position[0], places=2,
                msg=f"Expected hit position {position}, got {hit.position}\nin {hit}"
            )

    def test_trace(self):
        engine = Engine()
        obj_1 = engine.add_body(Circle((0, 0), 1))
        obj_2 = engine.add_body(Circle((10, 0), 5))
        engine.update(1/60)

        self.assertTrace(engine.trace((-10, 0), (1, 0)), body=obj_1)
        self.assertTrace(engine.trace((-10, 0.9), (1, 0)), body=obj_1)
        self.assertTrace(engine.trace((-10, 2), (1, 0)), body=obj_2)
        self.assertIsNone(engine.trace((-10, 10), (1, 0)))

    def test_trace_box(self):
        engine = Engine()
        obj_1 = engine.add_body(Box((0, 0), (1, 1)))
        obj_2 = engine.add_body(Box((0, 10), (1, 1), angle=math.radians(45)))
        engine.update(1/60)

        self.assertTrace(engine.trace((-10, 0), (1, 0)), body=obj_1, position=(-1, .98))
        self.assertTrace(engine.trace((-10, 10.707), (1, 0)), body=obj_2, position=(-.707, 10.707))


if __name__ == '__main__':
    unittest.main()
