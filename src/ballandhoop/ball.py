from __future__ import annotations


class Ball:
    """
    This class is a data structure for the ball element

    :var hoop: the hoop this ball belongs to
    :var center: the tuple of coordinates from the center of the ball
    :var radius: the radius of the ball
    """
    def __init__(self, hoop: Hoop, center: tuple, radius: int):
        self.hoop = hoop

        self.center = tuple(center)
        self.radius = int(radius)

    def angle(self):
        """
        Calculates the angle the ball has inside the hoop

        :return: the angle in float, calculated by his parent hoop :py:meth:`.Hoop.angle_in_hoop()`
        """
        return self.hoop.angle_in_hoop(self.center)
