from __future__ import annotations


class Ball:
    def __init__(self, hoop: Hoop, center: tuple, radius: int):
        self.hoop = hoop
        self.center = tuple(center)
        self.radius = int(radius)

    def angle_in_hoop(self):
        return self.hoop.angle_in_hoop(self.center)
