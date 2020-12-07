from typing import List

import pymunk
from pymunk import Vec2d

from .images import Images
from .renderer import Renderer
from .objects.body import Body
from .objects.constraints import Constraint
from .objects.graphical import Graphical
from .objects.physical import PhysicsInterface
from .objects.container import ObjectContainer
from .agents.base import AgentBase
from .agents.player import Player
from .log import LogMixin


class Engine(LogMixin):

    class TraceHit:
        def __init__(self, body, position, distance, gradient, num_steps):
            self.body = body
            self.position = position
            self.distance = distance
            self.gradient = gradient
            self.num_steps = num_steps

        def __str__(self):
            return "%s(%s)" % (
                self.__class__.__name__,
                ", ".join(
                    f"{key}={value}"
                    for key, value in (
                        ("body", self.body.short_name()),
                        ("position", self.position),
                        ("distance", self.distance),
                        ("gradient", self.gradient),
                        ("num_steps", self.num_steps),
                    )
                )
            )

    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = Vec2d(0., -10.)
        self.time = 0.
        self.images = Images()
        self.renderer = Renderer(self)
        self.container = ObjectContainer()
        self.container._engine = self
        self._empty_shape_filter = pymunk.ShapeFilter()
        self._window_size = Vec2d((320, 200))
        self.player = Player((0, 1))
        self.add_container(self.player)

    @property
    def window_size(self):
        return self._window_size

    @window_size.setter
    def window_size(self, v):
        self._window_size = Vec2d(v)

    def update(self, dt, fixed_dt=None):
        self.container.update(dt)

        pymunk_steps = 10
        pymunk_dt = (fixed_dt or dt) / pymunk_steps
        for i in range(pymunk_steps):
            self.space.step(pymunk_dt)

        self.time += dt

    def render(self, dt: float):
        self.renderer.translation += (self.player.position * (1, 0) - self.renderer.translation) * dt
        self.container.update_graphics(dt)
        self.renderer.render()

    def add_body(self, body: Body):
        return self.container.add_body(body)

    def remove_body(self, body: Body):
        self.container.remove_body(body)

    def add_constraint(self, constraint: Constraint):
        return self.container.add_constraint(constraint)

    def remove_constraint(self, constraint: Constraint):
        self.container.remove_constraint(constraint)

    def add_container(self, container: ObjectContainer):
        return self.container.add_container(container)

    def remove_container(self, container: ObjectContainer):
        self.container.remove_container(container)

    #def add_agent(self, agent: AgentBase):
    #    self.log(3, "add_agent", agent)
    #    agent._engine = self
    #    self.agents.append(agent)
    #    self._agents_to_create_objects.append(agent)

    #def remove_agent(self, agent: AgentBase):
    #    self.log(3, "remove_agent", agent)
    #    agent.remove_objects()
    #    self.agents.remove(agent)
    #    agent._engine = None
    #    self._agent_to_objects.pop(agent, None)

    def point_query_nearest_body(self, position, max_distance=0, shape_filter=None):
        hit = self.space.point_query_nearest(
            position, max_distance, shape_filter or self._empty_shape_filter
        )
        # print("Hit", position, hit)
        if not hit or not hit.shape:
            return None

        return self._pymunk_body_to_body(hit.shape.body)

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

        return self._pymunk_body_to_body(hit.shape.body)

    def trace(self, position, direction, max_steps=1000, min_distance=0.001, max_distance=1e6, shape_filter=None):
        """
        Raymarching through the pymunk physics space
        :param position: tuple, start of ray in world coordinates
        :param direction: tuple, direction as normalized vector
        :param max_steps: int, number of maximum steps to reach a surface
        :param min_distance: float, distance to surface to consider as hit
        :param max_distance: float, maximum distance to scan for objects
        :param shape_filter: pymunk.Shapefilter instance or None
        :return: Engine.TraceHit instance or None
        """
        shape_filter = shape_filter or self._empty_shape_filter
        position = Vec2d(position)
        direction = Vec2d(direction)
        for i in range(max_steps):
            hit = self.space.point_query_nearest(position, max_distance, shape_filter)
            if not hit:
                return None
            # print("H", hit)
            if hit.distance <= min_distance:
                return self.TraceHit(
                    body=self._pymunk_body_to_body(hit.shape.body),
                    position=position,
                    distance=hit.distance,
                    gradient=hit.gradient,
                    num_steps=i
                )

            position += direction * hit.distance

    def _pymunk_body_to_body(self, pymunk_body):
        body = self.container._pymunk_body_to_body(pymunk_body)
        if not body:
            raise AssertionError(f"pymunk body {pymunk_body} not in engine's mapping")
        return body

    def dump(self, file=None):
        self.container.dump_tree(file=file)
