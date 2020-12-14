import math

import pymunk
from pymunk import Vec2d

from .base import AgentBase
from ..objects.primitives import Box, Circle, Ngon
from ..objects.graphical import GraphicSettings
from ..objects import constraints
from ..keyhandler import KeyHandler
from ..evo.polynomial import Polynomial, PolynomialPeriod
from ..evo.params import FloatParameter, FloatParameters, ParametersGroup


class Player6(AgentBase):
    """Try to walk with evolutionary help"""
    def __init__(self, start_position, **parameters):
        super().__init__(start_position=start_position, **parameters)

        self.keys = KeyHandler()
        self.pick_dir = Vec2d()
        self.shape_filter = pymunk.ShapeFilter(categories=0b1, mask=pymunk.ShapeFilter.ALL_MASKS ^ 0b1)
        self.sequence_index = 0.
        self.jump_amount = 0.
        self.walk_sign = 1
        self.walking = False
        self.walk_speed_factor = .3
        self.polynomials = {
            "walk_x": PolynomialPeriod(
                seq=[0.1] * 5, amplitude=1., offset=0.,
                #seq=[0.08882834734403289, 1.0437225138008464, 0.1372975990571167, -1.1517058245854663, -1.3299943580854514], amplitude=0.5,
                #seq=[0.8213138250878218, 0.3169560467905213, 0.5394817031352098, -2.4297660696376178, -1.01426872271315], amplitude=.5,
                #seq=[0.848275819837695, 0.4225692758627822, 0.24071284860993988, -2.5062551638643997, -1.1058408159740925], amplitude=.5,
                #seq=[0.43443431597450755, 0.1, 0.6543409985769876, -1.3512604515288842, -1.0949536260473556], amplitude=1.,
                #seq=[0.7357286237574165, 0.8010924421839678, 2.003760840571829, 1.7379895383942698, 1.1614764404707159], amplitude=.1,
                #seq=[-1.2674264815002598, 1.3659628202326013, -0.6229660620629052, 0.2536657026249989, 2.202557766145348], amplitude=.5,
                #seq=[2.1870903370096197, -5.473204286047804, 5.604686414981392, 0.2443093967190033, 1.3374612075860475], amplitude=.5, offset=-1.,
            ),
            "walk_y": PolynomialPeriod(
                seq=[0.1] * 5, amplitude=.1, offset=-.4,
                #seq=[1.395439362585945, -1.7524559075070907, -1.27006177299697, 1.690270215932573, -0.9444440925711943], amplitude=.035,
                #seq=[-0.7556301652401446, 2.017016348622996, -0.8110032220306115, 0.14614223527738057, -2.1957851977203733], amplitude=.33,
                #seq=[-0.6699859363825067, 2.3693394418097204, -0.5513749784557014, 0.3170747097423691, -2.208134873159431], amplitude=.245,
                #seq=[0.14765961278931786, 1.442002873452267, 0.14889152564506092, 0.256085880845646, -1.6046491682048876], amplitude=.5,
                #seq=[-1.2274086889828242, 2.0857493488809267, 0.41104812733868057, 2.1882295616841416, 0.407664323133222], amplitude=.01,
                #seq=[1.2841619127292327, 2.1770939164052607, 2.981937467567752, 4.349743705283853, 0.045200595667766574], amplitude=.5,
                #seq=[-2.1382519479458937, 6.074638270631739, 9.695219330161098, 5.425918729808018, 4.340229696932189], amplitude=0.01, offset=-.2628,
            ),
        }
        self.load_evo_parameters("best.json")

    def load_evo_parameters(self, filename):
        params = self.get_evo_parameters()
        params.load_json(filename)
        self.set_evo_parameters(params)

    def randomize(self):
        import random
        for p in self.polynomials.values():
            for i in range(len(p.parameters)):
                p.parameters[i] = random.uniform(-.5, .5)
            p.amplitude = random.uniform(.1, .5)

    def get_evo_parameters(self):
        return ParametersGroup(
            **{
                f"poly_{key}": ParametersGroup(
                    poly=FloatParameters(poly.parameters),
                    amp=FloatParameter(poly.amplitude, min=0.01, max=1.),
                    #offset=FloatParameter(poly.offset, min=-1, max=1),
                )
                for key, poly in self.polynomials.items()
            },
            walk_speed=FloatParameter(self.walk_speed_factor, min=0., max=2.),
        )

    def set_evo_parameters(self, parameters):
        for key, params in parameters.parameters.items():
            if key.startswith("poly_"):
                poly = self.polynomials[key[5:]]
                poly.parameters = params.poly.values
                poly.amplitude = params.amp.value
                #poly.offset = params.offset.value
        self.walk_speed_factor = parameters.walk_speed.value

    @property
    def position(self):
        if self.bodies:
            return self.bodies[0].position
        return self.start_position

    def get_sensors(self, dt):
        body, foot_l, foot_r = self.bodies[0], self.bodies[1], self.bodies[2]
        center_of_gravity = body._body.center_of_gravity + body.position
        def _get_body_sensors(body, name):
            cog_diff = (body.position - center_of_gravity)
            return {
                f"{name}_pos_x": body.position.x,
                f"{name}_pos_y": body.position.y,
                f"{name}_velocity_x": body.velocity.x,
                f"{name}_velocity_y": body.velocity.y,
                f"{name}_angle": body.angle,
                f"{name}_kinetic_energy": body.kinetic_energy,
                f"{name}_cog_distance_x": cog_diff.x,
                f"{name}_cog_distance_y": cog_diff.y,
                #f"{name}_pos": body.position,
            }
        sensors = dict()
        sensors.update(_get_body_sensors(body, "body"))
        sensors.update(_get_body_sensors(foot_l, "foot_l"))
        sensors.update(_get_body_sensors(foot_r, "foot_r"))
        return sensors

    def create_objects(self):
        self.reference_points = (
            Vec2d(-.4, .1),
            # Vec2d(0, .4),
            Vec2d(.4, .1),
        )
        body = self.add_body(Ngon(
            position=self.start_position, radius=.5, segments=5,
            density=10,
            default_shape_filter=self.shape_filter,
        ))
        for sign, offset in ((-1, 0.), (1, .51)):
            foot = self.add_body(Ngon(
                position=self.start_position + (sign*.3, -.38), radius=.2, segments=3, density=10,
                friction=5.,
                default_shape_filter=self.shape_filter,
            ))
            self.add_constraint(constraints.RotaryLimitJoint(
                body, foot, 0., 0., user_data={"foot_rot": sign}
            ))
            for i, ref_point in enumerate(self.reference_points):
                self.add_constraint(constraints.FixedJoint(
                    body, foot, ref_point, (0, 0), user_data={"ref_point": ref_point, "offset": offset},
                ))
            #self.engine.space.add_collision_handler()

    def get_walk_sequence(self, t):
        return Vec2d(
            self.polynomials["walk_x"](t),
            self.polynomials["walk_y"](t),
        )

    def run_walk_sequence(self, dt):
        for c in filter(lambda c: c.has_user_data("ref_point"), self.constraints):
            ref_point = c.user_data["ref_point"]
            seq_point = self.get_walk_sequence(self.sequence_index + c.user_data["offset"])
            c.distance = (seq_point - ref_point).get_length()

        self.jump_amount *= max(0, 1. - dt * 20)

        # always finish current step
        if not self.walking:
            next_index = math.ceil(self.sequence_index*2) if self.walk_sign > 0 else math.floor(self.sequence_index*2)
            next_index_diff = (next_index - self.sequence_index*2) * self.walk_speed_factor
            if abs(next_index_diff) > 0.004:
                self.sequence_index += min(1, dt * 10) * next_index_diff

    def run_balance(self, dt):
        desired_angle = 0.#.4 * (-self.keys.is_down("right") + self.keys.is_down("left"))
        body = self.bodies[0]
        current_angle = body.angle
        amount = min(1, dt * 100.)# * abs(current_angle))
        body.angular_velocity += amount * (desired_angle - current_angle)

        for c in filter(lambda c: c.has_user_data("foot_rot"), self.constraints):
            c.min = c.max = -body.angle

    def walk(self, dt, speed):
        self.sequence_index += dt * speed * self.walk_speed_factor
        self.walk_sign = -1 if speed < 0 else 1
        self.walking = True

    def jump(self, dt):
        #self.jump_amount = 1.
        self.bodies[0].velocity += (0, 10)
        
    def dump_body(self, name, body):
        values = {
            key: _round(getattr(body._body, key))
            for key in ("kinetic_energy", "torque", "moment", "velocity")
        }
        values.update({
            "surface_velocity": body._shapes[0].surface_velocity
        })
        print(name, values)

    def dump_sensors(self, dt):
        sensors = self.get_sensors(dt)
        max_len = max(len(key) for key in sensors)
        print("-" * 40)
        for key, value in sensors.items():
            print(f"{key:{max_len}}: {_round(value)}")

    def update(self, dt):
        super().update(dt)
        if not self.bodies:
            return
        self.run_balance(dt)
        self.run_walk_sequence(dt)

        #self.dump_body("body ", self.bodies[0])
        #self.dump_body("left ", self.bodies[1])
        #self.dump_body("right", self.bodies[2])
        #self.dump_sensors(dt)

        body = self.bodies[0]
        
        pick_dir = Vec2d(0, 0)
        self.walking = False
        if self.keys.is_down("left"):
            pick_dir.x = -1
            speed = 1 + 3 * self.keys.smooth_down("left") + 6 * self.keys.smooth_pressed("left")
            self.walk(dt, -speed)

        if self.keys.is_down("right"):
            pick_dir.x = 1
            speed = 1 + 3 * self.keys.smooth_down("right") + 6 * self.keys.smooth_pressed("right")
            self.walk(dt, speed)

        if self.keys.is_pressed("up"):
            pick_dir.y = 1
            self.jump(dt)

        if self.keys.is_pressed("down"):
            pick_dir.y = -1
            body.velocity += (0, -10)#-dt * 30)

        if self.keys.is_pressed("shoot"):
            self.shoot(self.pick_dir)

        if pick_dir.x or pick_dir.y:
            self.pick_dir = pick_dir.normalized()

        if self.pick_dir.x or self.pick_dir.y:
            if self.keys.is_pressed("pick"):
                self.pick(self.pick_dir)

            if self.keys.is_pressed("put"):
                self.put(self.pick_dir)

        self.keys.update(dt)

    def pick(self, dir):
        body = self.bodies[0]
        pick_pos = body.position + dir

        other_body = self.engine.point_query_nearest_body(pick_pos)
        if other_body and other_body.density:
            self.engine.remove_body(other_body)

    def put(self, dir):
        body = self.bodies[0]

        put_pos = body.position + dir
        self.engine.add_body(
            Box(put_pos, (.5, .5), density=10)
        )

    def shoot(self, dir):
        bullet = self.add_body(Ngon(
            self.position, radius=.1, segments=3,
            density=1200,
            default_shape_filter=self.shape_filter,
        ))
        bullet.angular_velocity = 100.
        bullet.velocity = dir * 100


def _round(x, digits=2):
    if isinstance(x, (Vec2d, tuple)):
        return tuple(round(v, digits) for v in x)
    try:
        return round(x, digits)
    except (TypeError, ValueError):
        return x
