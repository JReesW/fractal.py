import numpy as np
import multiprocessing as mp
from PIL import Image

from math import isfinite
from functools import partial
from abc import ABC, abstractmethod


class Escape(Exception):
    """"""


def _correct_extension(filename, extension):
    return filename.split('.')[-1] == extension


def _compare_complex(a: complex, b: complex) -> complex:
    if a.real > b.real:
        return a
    if a.real == b.real:
        if a.imag > b.imag:
            return a
    return b


class _Fractal(ABC):
    def __init__(self):
        super().__init__()
        self.state = {}

        self.WIDTH = 1920
        self.HEIGHT = 1080
        self.TOLERANCE = 0.000001
        self.MAX_ITERATION = 100
        self.X_RANGE = -0.8, 0.8
        self.Y_RANGE = -1.1776, -0.2776

        self.P = mp.cpu_count()
        self.FRAMES = 60

    @property
    def STEP(self):
        return self.WIDTH // self.P

    @abstractmethod
    def func(self, z: complex, state: dict) -> complex:
        """
        The function on which Newton's method will be applied.

        params:
        - z: the starting point for Newton's method
        - state: internal variables, for changing values during animations
        """
        pass

    def deriv(self, z: complex, state: dict) -> complex:
        h = 0.000000001
        return (self.func(z + h, state) - self.func(z - h, state)) / (2 * h)

    def find_roots(self, state: dict) -> [complex]:
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
        return sorted(found, key=lambda c: (round(c.real, 8), round(c.imag, 8)))

    def find_root(self, z: complex, roots: [complex], state: dict) -> (int, int):
        for i in range(self.MAX_ITERATION):
            try:
                z -= self.func(z, state) / self.deriv(z, state)
            except (ZeroDivisionError, OverflowError, ValueError):
                return -1, 0

            for c, root in enumerate(roots):
                diff = z - root

                if abs(diff.real) < self.TOLERANCE and abs(diff.imag) < self.TOLERANCE:
                    return c, i

        return -1, 0

    @abstractmethod
    def get_color(self, root: int, depth: int, state: dict) -> (int, int, int):
        pass

    @staticmethod
    def convert_range(n, old_mn, old_mx, new_mn, new_mx):
        return (((n - old_mn) * (new_mx - new_mn)) / (old_mx - old_mn)) + new_mn

    def generate_segment(self, roots: [complex], state: dict, segment: int) -> np.ndarray:
        img = np.zeros(shape=(self.HEIGHT, self.STEP, 3))

        for x in range(self.STEP):
            # if x % 10 == 0:
            #     print(f"{x} / {self.STEP}")
            for y in range(self.HEIGHT):
                rl = self.convert_range(x + segment, 0, self.WIDTH, *self.X_RANGE)
                im = self.convert_range(y, 0, self.HEIGHT, *self.Y_RANGE[::-1])

                root, depth = self.find_root(rl + im * 1j, roots, state)
                r, g, b = self.get_color(root, depth, state)
                img[y, x, 0] = r
                img[y, x, 1] = g
                img[y, x, 2] = b

        return img


class FractalImage(_Fractal, ABC):
    def __init__(self):
        super().__init__()

    def generate_image(self, output: str) -> None:
        ranges = [i * self.STEP for i in range(self.P)]
        state = {}
        roots = self.find_roots(state)

        with mp.Pool() as p:
            segments = p.map(partial(self.generate_segment, roots, state), ranges)

        image = Image.fromarray(np.uint8(np.concatenate(segments, axis=1)), mode="RGB")
        image.save(output)


class FractalAnimation(_Fractal, ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def update(self, frame: int) -> dict:
        """
        Return the new state dictionary based on the current frame
        """
        return {}

    def generate_animation(self, output: str) -> None:
        if not _correct_extension(output, 'gif'):
            raise Exception("File extension should be '.gif' for an animation!")

        ranges = [i * self.STEP for i in range(self.P)]
        frames: [Image] = []

        for frame in range(self.FRAMES):
            state = self.update(frame)
            roots = self.find_roots(state)

            with mp.Pool() as p:
                segments = p.map(partial(self.generate_segment, roots, state), ranges)

            frames.append(Image.fromarray(np.uint8(np.concatenate(segments, axis=1)), mode="RGB"))
            print(f"frame {frame} complete")

        first, *rest = frames
        first.save(output, save_all=True, append_images=rest, duration=1000//30, loop=0)

