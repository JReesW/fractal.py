from fractal import FractalImage


def shade(val, depth):
    return int(max(0, val - depth))


class CustomFractal(FractalImage):
    def __init__(self):
        super().__init__()

    def func(self, z: complex, state: dict) -> complex:
        return z ** 3 - z ** 1j

    def get_color(self, root: int, depth: int, smooth: float, state: dict) -> (int, int, int):
        depth += smooth
        if root == 0:
            return (shade(c, 8 * depth) for c in (235, 235, 252))
        elif root == 1:
            return (shade(c, 8 * depth) for c in (52, 201, 235))
        elif root == 2:
            return (shade(c, 8 * depth) for c in (52, 52, 235))

        return 0, 0, 0


if __name__ == '__main__':
    frac = CustomFractal()
    frac.WIDTH = 7680
    frac.HEIGHT = 4320
    frac.X_RANGE, frac.Y_RANGE = (-0.637, 4.422), (0.555, 3.4)
    frac.generate_image("wavesImage.png")
