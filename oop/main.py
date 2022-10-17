from fractal import Fractal
from cmath import log, e, pi


phi = (1 + 5 ** 0.5) / 2


class CustomFractal(Fractal):
    def __init__(self):
        super().__init__()

    def func(self, z: complex) -> complex:
        return log(z ** 4 * pi, 1j * e * pi)

    def get_color(self, z: complex, roots: [complex]) -> (int, int, int):
        # TODO: move find_root() out of this function
        root, depth = self.find_root(z, roots)

        if root == 0:
            return (self.adapt(c, 4 * depth) for c in (220, 220, 220))
        elif root == 1:
            return (self.adapt(c, -4 * depth) for c in (20, 20, 20))
        elif root == 2:
            return (self.adapt(c, -4 * depth) for c in (20, 20, 20))
        elif root == 3:
            return (self.adapt(c, 4 * depth) for c in (220, 220, 220))

        return 0, 0, 0


if __name__ == '__main__':
    fractal = CustomFractal()
    fractal.WIDTH = 1920  # 7680
    fractal.HEIGHT = 1080  # 4320
    fractal.X_RANGE = -10.666, 10.666
    fractal.Y_RANGE = -6, 6
    fractal.generate_image()
