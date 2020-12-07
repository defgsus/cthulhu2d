from typing import List

import pymunk
from pymunk import Vec2d

from .images import Images
from .renderer import Renderer
from .objects.body import Body
from .objects.player import Player
from .objects.constraints import Constraint
from .objects.graphical import Graphical
from .objects.physical import PhysicsInterface
from .agents.base import AgentBase
from .log import LogMixin


class Engine(LogMixin):

    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = Vec2d(0., -10.)
        self.time = 0.
        self.images = Images()
        self.renderer = Renderer(self)
        self.bodies: List[Body] = []
        self.agents: List[AgentBase] = []
        self._pymunk_body_to_body = {}
        self._empty_shape_filter = pymunk.ShapeFilter()
        self._physics_to_create = []
        self._physics_to_destroy = []
        self._graphics_to_create = []
        self._graphics_to_destroy = []
        self._bodies_to_remove = []
        self._constraints_to_remove = []
        self._agents_to_create_objects = []
        self.constraints: List[Constraint] = []
        self._agent_to_objects = {}
        self._window_size = Vec2d((320, 200))
        self.player = Player((0, 0))
        self.add_body(self.player)

    @property
    def window_size(self):
        return self._window_size

    @window_size.setter
    def window_size(self, v):
        self._window_size = Vec2d(v)

    def update(self, dt, fixed_dt=None):
        for i in range(2):
            self._remove_bodies()
            self._remove_constraints()
            self._destroy_physics()
            self._create_physics()
            self._create_agent_objects()

        for o in self.iter_physics():
            o._base_update_called = False
            o.update(dt)
            if not o._base_update_called:
                raise RuntimeError(
                    f"super update() method has not been called: {o}"
                )

            o.update(dt)

        pymunk_steps = 10
        pymunk_dt = (fixed_dt or dt) / pymunk_steps
        for i in range(pymunk_steps):
            self.space.step(pymunk_dt)

        self.time += dt

    def render(self, dt: float):
        self._create_graphics()
        self._destroy_graphics()

        self.renderer.translation += (self.player.position * (1, 0) - self.renderer.translation) * dt
        for g in self.iter_graphics():
            g.update_graphics(dt)
        self.renderer.render()

    def add_body(self, body: Body, agent: AgentBase = None):
        self.log(3, "add_body", body, agent)
        body._engine = self
        self.bodies.append(body)
        self._add_to_agent(agent, "body", body)
        self._physics_to_create.append(body)
        self._graphics_to_create.append(body)
        body.on_engine_attached()

    def remove_body(self, body: Body):
        self.log(3, "remove_body", body)
        self._bodies_to_remove.append(body)

    def add_constraint(self, constraint: Constraint, agent: AgentBase = None):
        self.log(3, "add_constraint", constraint)
        constraint._engine = self
        self.constraints.append(constraint)
        self._add_to_agent(agent, "constraint", constraint)
        self._physics_to_create.append(constraint)
        self._graphics_to_create.append(constraint)
        constraint.on_engine_attached()
        for body in (constraint.a, constraint.b):
            body._constraints.append(constraint)
        for body in (constraint.a, constraint.b):
            body.on_constraint_added(constraint)

    def remove_constraint(self, constraint: Constraint):
        self.log(3, "remove_constraint", constraint)
        self._constraints_to_remove.append(constraint)

    def add_agent(self, agent: AgentBase):
        self.log(3, "add_agent", agent)
        agent._engine = self
        self.agents.append(agent)
        self._agents_to_create_objects.append(agent)

    def remove_agent(self, agent: AgentBase):
        self.log(3, "remove_agent", agent)
        agent.remove_objects()
        self.agents.remove(agent)
        agent._engine = None
        self._agent_to_objects.pop(agent, None)

    def iter_objects(self):
        """Yields all EngineObject instances"""
        for o in self.bodies:
            yield o
        for o in self.constraints:
            yield o
        for o in self.agents:
            yield o

    def iter_graphics(self):
        for o in self.iter_objects():
            if isinstance(o, Graphical):
                yield o

    def iter_physics(self):
        for o in self.iter_objects():
            if isinstance(o, PhysicsInterface):
                yield o

    def point_query_nearest_body(self, position, max_distance=0, shape_filter=None):
        hit = self.space.point_query_nearest(
            position, max_distance, shape_filter or self._empty_shape_filter
        )
        # print("Hit", position, hit)
        if not hit or not hit.shape:
            return None

        pymunk_body = hit.shape.body
        if pymunk_body not in self._pymunk_body_to_body:
            raise AssertionError(f"pymunk body {pymunk_body} not in engine's mapping")

        return self._pymunk_body_to_body[pymunk_body]

    def point_query_body(self, position, max_distance=0, shape_filter=None):
        hit = self.space.point_query(
            position, max_distance, shape_filter or self._empty_shape_filter
        )
        # print("Hit", position, hit)
        if not hit:
            return None
        hit = hit[0]
        if not hit.shape:
            return None

        pymunk_body = hit.shape.body
        if pymunk_body not in self._pymunk_body_to_body:
            raise AssertionError(f"pymunk body {pymunk_body} not in engine's mapping")

        return self._pymunk_body_to_body[pymunk_body]

    def dump(self, file=None):
        for body in self.bodies:
            body.dump(file=file)

    def _create_physics(self):
        while self._physics_to_create:
            obj = self._physics_to_create.pop(0)
            obj.create_physics()
            if isinstance(obj, Body):
                self._pymunk_body_to_body[obj._body] = obj
                obj._start_angular_velocity_applied = False

    def _destroy_physics(self):
        while self._physics_to_destroy:
            obj = self._physics_to_destroy.pop(0)
            obj.destroy_physics()
            obj.on_engine_detached()
            obj._engine = None

    def _create_graphics(self):
        while self._graphics_to_create:
            obj = self._graphics_to_create.pop(0)
            obj.create_graphics()

    def _destroy_graphics(self):
        while self._graphics_to_destroy:
            obj = self._graphics_to_destroy.pop(0)
            obj.destroy_graphics()

    def _remove_bodies(self):
        while self._bodies_to_remove:
            body = self._bodies_to_remove.pop(0)

            body.fire_callback("remove_body", body)
            self._remove_from_agent("body", body)

            for constraint in body._constraints:
                self.remove_constraint(constraint)
            self.bodies.remove(body)

            self._pymunk_body_to_body.pop(body._body, None)
            self._physics_to_destroy.append(body)
            self._graphics_to_destroy.append(body)

    def _remove_constraints(self):
        while self._constraints_to_remove:
            constraint = self._constraints_to_remove.pop(0)

            constraint.fire_callback("remove_constraint", constraint)
            self._remove_from_agent("constraint", constraint)

            for body in (constraint.a, constraint.b):
                if constraint in body._constraints:
                    body._constraints.remove(constraint)
            for body in (constraint.a, constraint.b):
                body.on_remove_constraint(constraint)
            self.constraints.remove(constraint)

            self._physics_to_destroy.append(constraint)
            self._graphics_to_destroy.append(constraint)

    def _create_agent_objects(self):
        while self._agents_to_create_objects:
            agent = self._agents_to_create_objects.pop(0)
            agent.create_objects()

    def _add_to_agent(self, agent: AgentBase, key, obj):
        if not agent:
            return
        if agent not in self._agent_to_objects:
            self._agent_to_objects[agent] = {}
        if key not in self._agent_to_objects[agent]:
            self._agent_to_objects[agent][key] = []
        self._agent_to_objects[agent][key].append(obj)

    def _remove_from_agent(self, key, obj):
        for agent, objects_per_key in self._agent_to_objects.items():
            if key in objects_per_key:
                objects = objects_per_key[key]
                if obj in objects:
                    if key == "body":
                        agent._bodies.remove(obj)
                    elif key == "constraint":
                        agent._constraints.remove(obj)

                    objects.remove(obj)
