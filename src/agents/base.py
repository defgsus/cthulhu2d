from typing import List

from pymunk import Vec2d

from ..objects.physical import PhysicsInterface
from ..objects.base import EngineObject
from ..objects.body import Body
from ..objects.constraints import Constraint
from ..objects.container import ObjectContainer


class AgentBase(ObjectContainer):

    def __init__(self, start_position=(0, 0), **parameters):
        super().__init__(**parameters)

        self._start_position = Vec2d(start_position)

    @property
    def start_position(self):
        return self._start_position

    @start_position.setter
    def start_position(self, v):
        self._start_position = Vec2d(v)

    def create_objects(self):
        pass
