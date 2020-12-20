import json
import datetime

from pymunk import Vec2d


def make_json_compatible(data):
    return json.loads(json.dumps(data, cls=JsonEncoder))


class JsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Vec2d):
            return [o.x, o.y]
        if isinstance(o, datetime.datetime):
            return o.isoformat()

        try:
            return super().default(o)
        except (TypeError, ValueError):
            return str(o)

