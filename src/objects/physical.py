

class PhysicsInterface:

    """
    An interface to apply updates to physics
    """

    def __init__(self):
        self._base_update_called = False

    def update(self, dt):
        self._base_update_called = True

