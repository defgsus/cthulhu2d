

class KeyHandler:

    def __init__(self):
        self.keys = dict()

    def is_down(self, key):
        if key not in self.keys:
            return False
        return bool(self.keys[key]["down"])

    def is_pressed(self, key):
        if key not in self.keys:
            return False
        return bool(self.keys[key]["pressed"])

    def smooth_down(self, key):
        if key not in self.keys:
            return 0.
        return self.keys[key]["smooth_down"]

    def smooth_pressed(self, key):
        if key not in self.keys:
            return 0.
        return self.keys[key]["smooth_pressed"]

    def set_key_down(self, key, down: bool):
        if key not in self.keys:
            self.keys[key] = {
                "smooth_down": 0.,
                "smooth_pressed": 0.,
                "changes": 0,
            }
        if bool(self.keys[key].get("down")) != down:
            self.keys[key]["changes"] += 1
        self.keys[key].update({
            "down": 1 if down else 0,
            "pressed": down,
        })

    def update(self, dt):
        for key, dic in self.keys.items():
            dic["smooth_down"] += min(1, dt * 2) * (dic["down"] - dic["smooth_down"])
            if dic["smooth_down"] < 0.001:
                dic["smooth_down"] = 0.

            dic["smooth_pressed"] += min(1, dt * 2) * (dic["pressed"] - dic["smooth_pressed"])
            if dic["smooth_pressed"] < 0.001:
                dic["smooth_pressed"] = 0.

            dic["pressed"] = False

    def changes(self, key):
        return self.keys.get(key, {}).get("changes", 0)

    def keys_down(self):
        return tuple(key for key in self.keys if self.is_down(key))
