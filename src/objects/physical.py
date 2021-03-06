

class PhysicsInterface:

    """
    An interface to apply updates to physics
    """

    def __init__(self):
        self._base_update_called = False
        self._num_update_calls = 0

    def update(self, dt):
        self._base_update_called = True
        self._num_update_calls += 1

    def create_physics(self):
        pass

    def destroy_physics(self):
        pass
