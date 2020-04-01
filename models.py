import math
import numpy as np
import colorsys


def change_velocities(ball_1, ball_2):
    """Particles p1 and p2 have collided elastically: update their velocities."""

    m1, m2 = ball_1.size ** 2, ball_2.size ** 2
    M = m1 + m2
    r1, r2 = ball_1.pos, ball_2.pos
    d = (r1 - r2).mag ** 2
    v1, v2 = ball_1.vel, ball_2.vel
    u1 = v1 - 2 * m2 / M * np.dot((v1 - v2).pos, (r1 - r2).pos) / d * (r1 - r2)
    u2 = v2 - 2 * m1 / M * np.dot((v2 - v1).pos, (r2 - r1).pos) / d * (r2 - r1)
    ball_1.vel = u1
    ball_2.vel = u2


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        if not isinstance(scalar, (int, float)):
            raise ValueError("scalar must be a number")
        return Vector(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar):
        if not isinstance(scalar, (int, float)):
            raise ValueError("scalar must be a number")
        return Vector(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        if not isinstance(scalar, (int, float)):
            raise ValueError("scalar must be a number")
        return Vector(self.x / scalar, self.y / scalar)

    def __repr__(self):
        return f"Vector({self.x},{self.y})"

    def __eq__(self, other):
        return self.pos == other.pos

    @property
    def norm(self):
        if self.x == 0 and self.y == 0:
            return self
        return self / self.mag

    @property
    def mag(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    @property
    def point(self):
        return int(self.x), int(self.y)

    @property
    def pos(self):
        return self.x, self.y


class Ball:
    def __init__(
        self, start_pos, start_vel=None, start_acc=None, size=5
    ):
        self.pos = start_pos
        self.vel = start_vel
        self.acc = start_acc
        self.size = size

    @property
    def color(self):
        if self.vel and self.vel.mag > 0:
            norm = self.vel.norm
            h = math.acos(self.vel.x / self.vel.mag)
            if norm.y > 0:
                h = 2 * math.pi - h
            h = h / (2 * math.pi)
            s = self.size / 100
            v = 255 * min(1, self.vel.mag / 1000)
        else:
            h = 0
            s = 0
            v = 0
        return colorsys.hsv_to_rgb(h, s, v)

    @staticmethod
    def change_velocities(ball_1, ball_2):
        """Update the velocities for the perfectly elastic collision of ball_1 and ball_2"""

        if ball_1.pos == ball_2.pos:
            return
        m1, m2 = ball_1.size ** 2, ball_2.size ** 2
        M = m1 + m2
        r1, r2 = ball_1.pos, ball_2.pos
        d = (r1 - r2).mag ** 2
        v1, v2 = ball_1.vel, ball_2.vel
        u1 = v1 - 2 * m2 / M * np.dot((v1 - v2).pos, (r1 - r2).pos) / d * (r1 - r2)
        u2 = v2 - 2 * m1 / M * np.dot((v2 - v1).pos, (r2 - r1).pos) / d * (r2 - r1)
        ball_1.vel = u1
        ball_2.vel = u2

    @staticmethod
    def separate_balls(ball_1, ball_2):
        v = ball_1.pos - ball_2.pos
        amount_to_move = ball_1.size + ball_2.size - v.mag
        if amount_to_move > 0:
            move_v = v.norm * (amount_to_move / 2)
            ball_1.pos += move_v
            ball_2.pos -= move_v

    @property
    def point(self):
        return self.pos.point

    def update(self, frame_rate):
        if self.vel:
            self.pos += self.vel / frame_rate
            if self.acc:
                self.vel += self.acc

    def __repr__(self):
        return f"Ball(pos={self.pos}, vel={self.vel}, acc={self.acc})"
