from typing import List

from pymunk import Vec2d

from ..objects.physical import PhysicsInterface
from ..objects.base import EngineObject
from ..objects.body import Body
from ..objects.constraints import Constraint


class AgentBase(PhysicsInterface, EngineObject):

    def __init__(self, start_position, **parameters):
        EngineObject.__init__(self, **parameters)
        PhysicsInterface.__init__(self)

        self.start_position = Vec2d(start_position)
        self._bodies: List[Body] = []
        self._constraints: List[Constraint] = []

    @property
    def bodies(self):
        return self._bodies

    @property
    def constraints(self):
        return self._constraints

    def update(self, dt):
        super().update(dt)

    def create_objects(self):
        pass

    def remove_objects(self):
        for body in self._bodies:
            self.engine.remove_body(body)

    def add_body(self, body):
        self._bodies.append(body)
        self.engine.add_body(body, agent=self)
        return body

    def remove_body(self, body):
        self.engine.remove_body(body)
        self._bodies.remove(body)

    def add_constraint(self, constraint):
        self._constraints.append(constraint)
        self.engine.add_constraint(constraint, agent=self)
        return constraint

    def remove_constraint(self, constraint):
        self.engine.remove_constraint(constraint)
        self._constraints.remove(constraint)
