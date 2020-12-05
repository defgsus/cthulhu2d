from typing import List

from ..engine_obj import EngineObject
from ..body import Body
from ..constraints import Constraint


class AgentBase(EngineObject):

    def __init__(self, start_position, **parameters):
        super().__init__(start_position=start_position, **parameters)
        self._bodies: List[Body] = []
        self._constraints: List[Constraint] = []

    @property
    def start_position(self):
        return self._parameters["start_position"]

    @property
    def bodies(self):
        return self._bodies

    def update(self, dt):
        pass

    def create_objects(self):
        pass

    def remove_objects(self):
        for body in self._bodies:
            self.engine.remove_body(body)

    def add_body(self, body):
        self._bodies.append(body)
        self.engine.add_body(body)
        return body

    def remove_body(self, body):
        self.engine.remove_body(body)
        self._bodies.remove(body)

    def add_constraint(self, constraint):
        self._constraints.append(constraint)
        self.engine.add_constraint(constraint)
        return constraint

    def remove_constraint(self, constraint):
        self.engine.remove_constraint(constraint)
        self._constraints.remove(constraint)
