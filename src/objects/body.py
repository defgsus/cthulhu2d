from typing import List

import pymunk
from pymunk import Vec2d

from .graphical import Graphical
from .physical import PhysicsInterface


class Body(PhysicsInterface, Graphical):

    def __init__(self, position, angle=0, density=0, velocity=(0, 0), friction=1., default_shape_filter=None, **parameters):
        from .constraints import Constraint
        Graphical.__init__(self, **parameters)
        PhysicsInterface.__init__(self)

        self.start_position = Vec2d(position)
        self.start_angle = angle
        self.start_angular_velocity = 0.
        self.density = density
        self._friction = friction
        self._start_angular_velocity_applied = False
        self._default_shape_filter = default_shape_filter
        self._start_velocity = Vec2d(velocity)

        self._body: pymunk.Body = None
        self._shapes: List[pymunk.Shape] = []
        self._constraints: List[Constraint] = []

    def to_dict(self):
        return {
            **super().to_dict(),
            "start_position": self.start_position,
            "start_angle": self.start_angle,
            "start_angular_velocity": self.start_angular_velocity,
            "density": self.density,
            #"default_shape_filter": self._default_shape_filter,
        }

    @property
    def position(self):
        if self._body:
            return self._body.position
        return self.start_position

    @position.setter
    def position(self, v):
        v = Vec2d(v)
        if self._body:
            self._body.position = v
        self.start_position = v

    @property
    def velocity(self):
        if self._body:
            return self._body.velocity
        return self._start_velocity

    @velocity.setter
    def velocity(self, v):
        if self._body:
            self._body.velocity = v
        self._start_velocity = v

    @property
    def angular_velocity(self):
        if self._body:
            return self._body.angular_velocity
        return self.start_angular_velocity

    @angular_velocity.setter
    def angular_velocity(self, v):
        if self._body:
            self._body.angular_velocity = v
        self.start_angular_velocity = v

    @property
    def angle(self):
        if self._body:
            return self._body.angle
        return self.start_angle

    @angle.setter
    def angle(self, v):
        if self._body:
            self._body.angle = v
        self.start_angle = v

    @property
    def friction(self):
        return self._friction

    @friction.setter
    def friction(self, v):
        self.friction = v
        for s in self._shapes:
            s.friction = v

    @property
    def kinetic_energy(self):
        if self._body:
            return self._body.kinetic_energy
        return 0.

    @property
    def body(self):
        if self._body is None:
            raise ValueError(f"Request of non-existent body. Use {self.__class__.__name__}.create_graphics() first")
        return self._body

    def remove(self):
        """Remove from parent/base container"""
        if self.engine:
            if self._parent_container:
                self._parent_container.remove_body(self)
            else:
                self.engine.remove_body(self)

    def on_constraint_added(self, constraint):
        pass

    def on_remove_constraint(self, constraint):
        pass

    def destroy_physics(self):
        for shape in self._shapes:
            self.engine.space.remove(shape)
        self._shapes = []

        if self._body:
            self.engine.space.remove(self._body)
        self._body = None

    def update(self, dt):
        super().update(dt)
        if self._body and not self._start_angular_velocity_applied:
            self._body.angular_velocity = self.start_angular_velocity
            self._body.velocity = self._start_velocity
            self._start_angular_velocity_applied = True

    def add_shape(self, shape: pymunk.Shape):
        """
        Add a pymunk Shape object.
        To be called within create_physics()
        """
        shape._parent_body = self
        shape.density = self.density
        shape.friction = self._friction
        # shape.elasticity = .5
        if self._default_shape_filter:
            shape.filter = self._default_shape_filter
        self._shapes.append(shape)

    def _create_body(self):
        if not self.density:
            self._body = pymunk.Body(body_type=pymunk.Body.STATIC)
        else:
            self._body = pymunk.Body()
        self._body.position = self.start_position
        self._body.angle = self.start_angle
        return self._body

    def iter_points(self):
        raise StopIteration

    def iter_world_points(self):
        for p in self.iter_points():
            yield self.position + p.rotated(self.angle)

    def dump(self, file=None):
        print(self.__class__.__name__, file=file)
        params = self.to_dict()
        for key in sorted(params):
            value = params[key]
            print(f"{key:30}: {repr(value)}", file=file)
        if self._constraints:
            print("constraints:", file=file)
            for c in self._constraints:
                print(" ", c, file=file)
        else:
            print("no constraints", file=file)

        #print(f"{self.__class__.__name__}: pos={self.position}, ang={self.angle}", file=file)

