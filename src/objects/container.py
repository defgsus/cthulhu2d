from typing import List

from .base import EngineObject
from .physical import PhysicsInterface
from .graphical import Graphical
from .body import Body
from .constraints import Constraint
from ..log import LogMixin


class ObjectContainer(PhysicsInterface, Graphical, LogMixin):

    """
    Container for EngineObjects.
    Engine itself holds a base container where everything is managed
    """

    def __init__(self, **parameters):
        Graphical.__init__(self, **parameters)
        PhysicsInterface.__init__(self)

        self.bodies: List[Body] = []
        self.constraints: List[Constraint] = []
        self.containers: List[ObjectContainer] = []
        self._pymunk_body_to_body_dict = {}
        self._physics_to_create = []
        self._physics_to_destroy = []
        self._graphics_to_create = []
        self._graphics_to_destroy = []
        self._bodies_to_remove = []
        self._constraints_to_remove = []
        self._containers_to_remove = []
        self._containers_to_create_objects = []

    def update(self, dt):
        super().update(dt)

        for i in range(2):
            self._remove_bodies()
            self._remove_constraints()
            self._destroy_physics()
            self._create_physics()
            self._create_container_objects()

        for obj in self.iter_physics():
            obj._base_update_called = False
            obj.update(dt)
            if not obj._base_update_called:
                raise RuntimeError(
                    f"super update() method has not been called in {obj}"
                )

    def create_graphics(self):
        for c in self.containers:
            c.create_graphics()

    def destroy_graphics(self):
        for c in self.containers:
            c.destroy_graphics()

    def update_graphics(self, dt):
        self._destroy_graphics()
        self._create_graphics()

        for g in self.iter_graphics():
            g.update_graphics(dt)

    def render_graphics(self):
        for g in self.iter_graphics():
            g.render_graphics()

    def add_body(self, body):
        self.log(3, "add_body", body)
        body._parent_container = self
        body._engine = self.engine
        self.bodies.append(body)
        # self._add_to_agent(agent, "body", body)
        self._physics_to_create.append(body)
        self._graphics_to_create.append(body)
        body.on_engine_attached()
        return body

    def add_constraint(self, constraint):
        self.log(3, "add_constraint", constraint)
        constraint._parent_container = self
        constraint._engine = self.engine
        self.constraints.append(constraint)
        # self._add_to_agent(agent, "constraint", constraint)
        self._physics_to_create.append(constraint)
        self._graphics_to_create.append(constraint)
        constraint.on_engine_attached()
        for body in (constraint.a, constraint.b):
            body._constraints.append(constraint)
        for body in (constraint.a, constraint.b):
            body.on_constraint_added(constraint)
        return constraint

    def add_container(self, container):
        self.log(3, "add_container", container)
        container._parent_container = self
        container._engine = self.engine
        self.containers.append(container)
        if hasattr(container, "create_objects"):
            self._containers_to_create_objects.append(container)
        return container

    def remove_body(self, body):
        self.log(3, "remove_body", body)
        if not self._remove_body_recursive(body):
            raise ValueError(f"remove_body on {self.short_name()} not successful with {body}")

    def remove_constraint(self, constraint):
        self.log(3, "remove_constraint", constraint)
        if not self._remove_constraint_recursive(constraint):
            raise ValueError(f"remove_constraint on {self.short_name()} not successful with {constraint}\nXX {self.constraints}")

    def remove_container(self, container):
        self.log(3, "remove_container", container)
        if not self._remove_container_recursive(container):
            raise ValueError(f"remove_container on {self.short_name()} not successful with {container}")

    def _remove_body_recursive(self, body):
        if body in self.bodies:
            self._bodies_to_remove.append(body)
            return True
        else:
            for c in self.containers:
                if c._remove_body_recursive(body):
                    return True
        return False

    def _remove_constraint_recursive(self, constraint):
        if constraint in self.constraints:
            self._constraints_to_remove.append(constraint)
            return True
        else:
            for c in self.containers:
                if c._remove_constraint_recursive(constraint):
                    return True
        return False
    
    def _remove_container_recursive(self, container):
        if container in self.containers:
            self._containers_to_remove.append(container)
            return True
        else:
            for c in self.containers:
                if c._remove_container_recursive(container):
                    return True
        return False

    def iter_objects(self):
        """Yields all contained EngineObject instances"""
        for o in self.bodies:
            yield o
        for o in self.constraints:
            yield o
        for o in self.containers:
            yield o

    def iter_graphics(self):
        for o in self.iter_objects():
            if isinstance(o, Graphical):
                yield o

    def iter_physics(self):
        for o in self.iter_objects():
            if isinstance(o, PhysicsInterface):
                yield o

    def _pymunk_body_to_body(self, pymunk_body):
        if pymunk_body in self._pymunk_body_to_body_dict:
            return self._pymunk_body_to_body_dict[pymunk_body]

        for sub in self.containers:
            body = sub._pymunk_body_to_body(pymunk_body)
            if body:
                return body

    def _create_physics(self):
        while self._physics_to_create:
            obj = self._physics_to_create.pop(0)
            self.log(4, "create_physics:", obj)
            obj.create_physics()
            if isinstance(obj, Body):
                self._pymunk_body_to_body_dict[obj._body] = obj
                obj._start_angular_velocity_applied = False

    def _destroy_physics(self):
        while self._physics_to_destroy:
            obj = self._physics_to_destroy.pop(0)
            self.log(4, "destroy_physics:", obj)
            obj.destroy_physics()
            obj.on_engine_detached()
            obj._engine = None

    def _create_graphics(self):
        while self._graphics_to_create:
            obj = self._graphics_to_create.pop(0)
            self.log(4, "create_graphics:", obj)
            obj.create_graphics()

    def _destroy_graphics(self):
        while self._graphics_to_destroy:
            obj = self._graphics_to_destroy.pop(0)
            self.log(4, "destroy_graphics:", obj)
            obj.destroy_graphics()

    def _remove_bodies(self):
        while self._bodies_to_remove:
            body = self._bodies_to_remove.pop(0)

            body.fire_callback("remove_body", body)

            for constraint in body._constraints:
                constraint.remove()

            self.bodies.remove(body)
            self._pymunk_body_to_body_dict.pop(body._body, None)

            self._physics_to_destroy.append(body)
            self._graphics_to_destroy.append(body)

    def _remove_constraints(self):
        while self._constraints_to_remove:
            constraint = self._constraints_to_remove.pop(0)

            constraint.fire_callback("remove_constraint", constraint)

            for body in (constraint.a, constraint.b):
                if constraint in body._constraints:
                    body._constraints.remove(constraint)
            for body in (constraint.a, constraint.b):
                body.on_remove_constraint(constraint)
            self.constraints.remove(constraint)

            self._physics_to_destroy.append(constraint)
            self._graphics_to_destroy.append(constraint)

    def _create_container_objects(self):
        while self._containers_to_create_objects:
            container = self._containers_to_create_objects.pop(0)
            container.create_objects()

    def dump_tree(self, indent="", file=None):
        print(f"{indent}{self.short_name()}")
        for c in self.iter_objects():
            if isinstance(c, ObjectContainer):
                c.dump_tree(indent=indent + "  ", file=file)
            else:
                print(f"  {indent}{c.short_name()}")
