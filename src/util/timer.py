import time


class Timer:
    def __init__(self, count=None):
        self.count = count
        self.start_time = None
        self.end_time = None
        self.length = None

    @property
    def rate(self):
        if not self.count or self.length is None:
            return None
        return self.count / self.length

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.length = self.end_time - self.start_time

    def print(self, desc=None, file=None):
        if desc:
            text = f"{desc} "
        else:
            text = ""
        if self.count:
            text += f"x{self.count} "
        text += f"took {self._round(self.length)} seconds"
        rate = self.rate
        if rate:
            text += f" = {self._round(rate)} per second"
        print(text, file=file)

    @staticmethod
    def _round(x):
        if abs(x) < 1:
            return round(x, 5)
        return round(x, 2)
