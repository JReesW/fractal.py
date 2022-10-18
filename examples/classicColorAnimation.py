from fractal import FractalAnimation
from math import sin, pi


phi = (1 + 5 ** 0.5) / 2


def shade(val, depth):
    return max(0, val - depth)


class CustomFractal(FractalAnimation):
    def __init__(self):
        super().__init__()

    def func(self, z: complex, state: dict) -> complex:
        return z ** 3 - 1

    def update(self, frame: int) -> dict:
        return {
            'f': 127 * (sin(frame / (self.FRAMES // 2 / pi)) + 1),
            'g': 127 * (sin((frame - (self.FRAMES // 3)) / ((self.FRAMES // 2) / pi)) + 1),
            'h': 127 * (sin((frame + (self.FRAMES // 3)) / ((self.FRAMES // 2) / pi)) + 1),
        }

    def get_color(self, root: int, depth: int, state: dict) -> (int, int, int):
        if root == 0:
            return (shade(c, 4 * depth) for c in (state['f'], state['g'], state['h']))
        elif root == 1:
            return (shade(c, 4 * depth) for c in (state['h'], state['f'], state['g']))
        elif root == 2:
            return (shade(c, 4 * depth) for c in (state['g'], state['h'], state['f']))

        return 0, 0, 0


if __name__ == '__main__':
    fractal = CustomFractal()
    fractal.WIDTH = 720  # 1920  # 7680
    fractal.HEIGHT = 480  # 1080  # 4320
    fractal.X_RANGE = -10.666, 10.666
    fractal.Y_RANGE = -6, 6
    fractal.FRAMES = 180
    fractal.P = 4
    fractal.generate_animation("test.gif")
