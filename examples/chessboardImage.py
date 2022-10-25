from fractal import FractalImage
from cmath import log, e, pi


def shade(val, depth):
    return int(max(0, val - depth))


class Fractal(FractalImage):
    def func(self, z: complex, state: dict) -> complex:
        return log(z ** 4 * pi, e * pi * 1j)

    def color(self, root: int, depth: int, smooth: float, state: dict) -> (int, int, int):
        depth += smooth
        if root == -1:
            return 0, 0, 0
        elif root % 4 in (1, 2):
            return (shade(c, 6 * depth) for c in (30, 30, 30))
        else:
            return (shade(c, 6 * depth) for c in (220, 220, 220))


if __name__ == '__main__':
    fractal = Fractal()
    fractal.WIDTH = 7680
    fractal.HEIGHT = 4320
    fractal.X_RANGE, fractal.Y_RANGE = (-10.666, 10.666), (-6, 6)
    fractal.generate("chessboardImage.png")
