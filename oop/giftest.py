from fractal import FractalAnimation
from cmath import log, e, pi, exp, sin


phi = (1 + 5 ** 0.5) / 2


class CustomFractal(FractalAnimation):
    def __init__(self):
        super().__init__()

    def func(self, z: complex, state) -> complex:
        return log(z ** 4 - (z * 1j))

    def get_color(self, root, depth, state) -> (int, int, int):
        if root == 0:
            return (self.adapt(c, 4 * depth) for c in (255, 0, 0))
        elif root == 1:
            return (self.adapt(c, 4 * depth) for c in (0, 255, 0))
        elif root == 2:
            return (self.adapt(c, 4 * depth) for c in (0, 0, 255))
        elif root == 3:
            return (self.adapt(c, 4 * depth) for c in (220, 220, 220))

        return 0, 0, 0


if __name__ == '__main__':
    fractal = CustomFractal()
    fractal.WIDTH = 1920  # 7680
    fractal.HEIGHT = 1080  # 4320
    fractal.X_RANGE = -10.666, 10.666
    fractal.Y_RANGE = -6, 6
    fractal.generate_animation().save("test.png")
