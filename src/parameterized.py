

class Parameterized:

    def __init__(self):
        pass

    def to_dict(self):
        return dict()

    def __repr__(self):
        params = self.to_dict()
        params = ", ".join(
            f"{key}={repr(value)}"
            for key, value in params.items()
        )
        return f"{self.__class__.__name__}({params})"
