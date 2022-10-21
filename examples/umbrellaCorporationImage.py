from fractal import FractalImage
from cmath import log, e, pi


def shade(val, depth):
    return int(max(0, val - depth))


class Fractal(FractalImage):
    def __init__(self):
        super().__init__()

    def func(self, z: complex, state: dict) -> complex:
        return log(z ** 8 * pi, e * pi * 1j)

    def get_color(self, root: int, depth: int, smooth: float, state: dict) -> (int, int, int):
        depth += smooth
        if root == -1:
            return 0, 0, 0
        elif root % 4 in (0, 3):
            return (shade(c, 6 * depth) for c in (180, 0, 0))
        else:
            return (shade(c, 6 * depth) for c in (220, 220, 220))


if __name__ == '__main__':
    fractal = Fractal()
    fractal.WIDTH = 7680
    fractal.HEIGHT = 4320
    fractal.X_RANGE, fractal.Y_RANGE = (-12.444, 12.444), (-7, 7)
    fractal.generate_image("umbrellaCorporationImage.png")
