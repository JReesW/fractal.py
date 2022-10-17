import numpy as np
import multiprocessing as mp
from PIL import Image
from math import isfinite
from cmath import log
from functools import partial


class Escape(Exception):
    """"""


class Fractal:
    def __init__(self):
        self.state = {}

        self.WIDTH = 1920
        self.HEIGHT = 1080
        self.TOLERANCE = 0.000001
        self.MAX_ITERATION = 100
        self.X_RANGE = -0.8, 0.8
        self.Y_RANGE = -1.1776, -0.2776

        self.P = 8  # mp.cpu_count()
        # self.STEP = self.WIDTH // self.P
        self.FRAMES = 30

    @property
    def STEP(self):
        return self.WIDTH // self.P

    def func(self, z: complex, state) -> complex:
        return log(z ** 4 - z * (self.state['factor'] * 1j))

    def deriv(self, z: complex, state) -> complex:
        h = 0.000000001
        return (self.func(z + h, state) - self.func(z - h, state)) / (2 * h)

    def find_roots(self, state) -> [complex]:
        found = []
        x_min = -5
        x_max = 5
        step = (x_max - x_min) / 100

        for x in range(100):
            for y in range(100):
                z = (x_min + x * step) + (x_min + y * step) * 1j

                try:
                    for a in range(10):
                        for root in found:
                            diff = z - root

                            if abs(diff.real) < self.TOLERANCE and abs(diff.imag) < self.TOLERANCE:
                                raise Escape

                        for b in range(10):
                            if not isfinite(z.real) or not isfinite(z.imag):
                                raise Escape

                            if self.deriv(z, state) != (0 + 0j):
                                try:
                                    z -= self.func(z, state) / self.deriv(z, state)
                                except ZeroDivisionError:
                                    raise Escape
                            else:
                                raise Escape
                    found.append(z)
                except (Escape, ZeroDivisionError, OverflowError, ValueError):
                    continue
        return found

    def find_root(self, z: complex, roots: [complex], state) -> (int, int):
        for i in range(self.MAX_ITERATION):
            try:
                z -= self.func(z, state) / self.deriv(z, state)
            except:
                return -1, 0

            for c, root in enumerate(roots):
                diff = z - root

                if abs(diff.real) < self.TOLERANCE and abs(diff.imag) < self.TOLERANCE:
                    return c, i

        return -1, 0

    @staticmethod
    def adapt(val, depth):
        return max(0, val - depth)

    def get_color(self, root, depth, state) -> (int, int, int):
        if root == 0:
            return (self.adapt(c, depth) for c in (255, 0, 0))
        elif root == 1:
            return (self.adapt(c, depth) for c in (0, 255, 0))
        elif root == 2:
            return (self.adapt(c, depth) for c in (0, 0, 255))
        elif root == 3:
            return (self.adapt(c, depth) for c in (255, 255, 0))

        return 0, 0, 0

    @staticmethod
    def convert_range(n, old_mn, old_mx, new_mn, new_mx):
        return (((n - old_mn) * (new_mx - new_mn)) / (old_mx - old_mn)) + new_mn

    def generate_segment(self, roots, state, segment: int) -> np.ndarray:
        img = np.zeros(shape=(self.HEIGHT, self.STEP, 3))

        for x in range(self.STEP):
            if x % 10 == 0:
                print(f"{x} / {self.STEP}")
            for y in range(self.HEIGHT):
                rl = self.convert_range(x + segment, 0, self.WIDTH, *self.X_RANGE)
                im = self.convert_range(y, 0, self.HEIGHT, *self.Y_RANGE[::-1])

                root, depth = self.find_root(rl + im * 1j, roots, state)
                r, g, b = self.get_color(root, depth, state)
                img[y, x, 0] = r
                img[y, x, 1] = g
                img[y, x, 2] = b

        return img

    def generate_image(self):
        ranges = [i * self.STEP for i in range(self.P)]
        state = {'exp': 4}
        roots = self.find_roots(state)

        with mp.Pool() as p:
            segments = p.map(partial(self.generate_segment, roots, state), ranges)

        image = Image.fromarray(np.uint8(np.concatenate(segments, axis=1)), mode="RGB")
        image.save("output.png")
