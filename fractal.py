import numpy as np
import multiprocessing as mp
from PIL import Image

from math import isfinite, log
from functools import partial
from abc import ABC, abstractmethod
from time import time


class Escape(Exception):
    """
    Escapes nested loops, as long as it is caught
    """


def _convert_range(n: float, old_mn: float, old_mx: float, new_mn: float, new_mx: float) -> float:
    """
    Convert a number based on its old range to its proportional equivalent in a new range
    """
    return (((n - old_mn) * (new_mx - new_mn)) / (old_mx - old_mn)) + new_mn


def _correct_extension(filename: str, extension: str) -> bool:
    """
    Check if a given filename has the given extension
    """
    return filename.split('.')[-1] == extension


def _dist(a: complex, b: complex) -> float:
    """
    Return the Euclidean distance between two complex numbers
    """
    return ((a.real - b.real) ** 2 + (a.imag - b.imag) ** 2) ** 0.5


class _Fractal(ABC):
    """
    Fractal base class
    """
    def __init__(self):
        super().__init__()
        self.WIDTH = 1920
        self.HEIGHT = 1080
        self.TOLERANCE = 0.000001
        self.MAX_ITERATIONS = 100
        self.X_RANGE = -7.111, 7.111
        self.Y_RANGE = -4, 4

        self.P = mp.cpu_count()
        self.FRAMES = 60

        self.TIMED = False

    @property
    def step(self) -> int:
        """
        The width of each segment a process gets
        """
        return self.WIDTH // self.P

    @abstractmethod
    def func(self, z: complex, state: dict) -> complex:
        """
        The function on which Newton's method will be applied.

        params:
        - z: The starting point for Newton's method
        - state: Internal variables, for changing values during animations
        """
        pass

    def _deriv(self, z: complex, state: dict) -> complex:
        """
        Approximates the derivative of func()
        """
        h = 0.000000001
        return (self.func(z + h, state) - self.func(z - h, state)) / (2 * h)

    def _find_roots(self, state: dict) -> [complex]:
        """
        Scatter 10.000 points and apply Newton's method to each, to approximate the roots of func()
        """
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

                            if self._deriv(z, state) != (0 + 0j):
                                try:
                                    z -= self.func(z, state) / self._deriv(z, state)
                                except ZeroDivisionError:
                                    raise Escape
                            else:
                                raise Escape
                    found.append(z)
                except (Escape, ZeroDivisionError, OverflowError, ValueError):
                    continue
        return sorted(found, key=lambda c: (round(c.real, 8), round(c.imag, 8)))

    def _find_root(self, z: complex, roots: [complex], state: dict) -> (int, int, float):
        """
        Given a complex number and a list of roots, returns which root it approaches, the depth, and smoothness addend
        """
        for i in range(self.MAX_ITERATIONS):
            prev = z
            try:
                z -= self.func(z, state) / self._deriv(z, state)
            except (ZeroDivisionError, OverflowError, ValueError):
                return -1, 0, 0

            for c, root in enumerate(roots):
                diff = z - root

                if abs(diff.real) < self.TOLERANCE and abs(diff.imag) < self.TOLERANCE:
                    d0 = _dist(prev, root)
                    d1 = _dist(z, root)
                    try:
                        s = (log(self.TOLERANCE) - log(d0)) / (log(d1) - log(d0))
                    except (ValueError, ZeroDivisionError):
                        s = 0
                    return c, i, s

        return -1, 0, 0

    @abstractmethod
    def color(self, root: int, depth: int, smooth: float, state: dict) -> (int, int, int):
        """
        Given the index of the found root, the iteration depth it took to find it, and a smoothening addend:
        Return the RGB color for these given values.

        params:
        - root: The index of the root found, often decides the base color
        - depth: No. of iterations it took to find the root
        - smooth: Extra smoothness value, add to the depth to avoid 'banding'
        - state: Internal variables, for changing values during animations
        """
        pass

    def _generate_segment(self, roots: [complex], state: dict, segment: int) -> np.ndarray:
        """
        Generate a segment of the total image, given the roots and the starting point of the segment
        """
        img = np.zeros(shape=(self.HEIGHT, self.step, 3))

        for x in range(self.step):
            for y in range(self.HEIGHT):
                rl = _convert_range(x + segment, 0, self.WIDTH, *self.X_RANGE)
                im = _convert_range(y, 0, self.HEIGHT, *self.Y_RANGE[::-1])

                root, depth, smooth = self._find_root(rl + im * 1j, roots, state)
                r, g, b = self.color(root, depth, smooth, state)
                img[y, x, 0] = r
                img[y, x, 1] = g
                img[y, x, 2] = b

        return img


class FractalImage(_Fractal, ABC):
    """
    Class for generating an image of a Newton fractal
    """

    def __init__(self):
        super().__init__()

    def generate(self, output: str) -> None:
        """
        Render a fractal to the given output path
        """
        start_time = 0
        if self.TIMED:
            start_time = time()
        if self.WIDTH % self.P != 0:
            raise Exception(f"Image width ({self.WIDTH}) not evenly divisible by configured amount of cores ({self.P})")

        ranges = [i * self.step for i in range(self.P)]
        state = {}
        roots = self._find_roots(state)

        with mp.Pool() as p:
            segments = p.map(partial(self._generate_segment, roots, state), ranges)

        image = Image.fromarray(np.uint8(np.concatenate(segments, axis=1)), mode="RGB")
        image.save(output)

        if self.TIMED:
            print(f"Took {time() - start_time:.2f} seconds!")


class FractalAnimation(_Fractal, ABC):
    """
    Class for generating an animation of a Newton fractal
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def update(self, frame: int) -> dict:
        """
        Return the new state dictionary based on the current frame number
        """
        pass

    def generate(self, output: str) -> None:
        """
        Render a fractal animation to the given output path (.gif extension required)
        """
        start_time = 0
        if self.TIMED:
            start_time = time()
        if not _correct_extension(output, 'gif'):
            raise Exception("File extension should be '.gif' for an animation!")
        if self.WIDTH % self.P != 0:
            raise Exception(f"Image width ({self.WIDTH}) not evenly divisible by chosen amount of cores ({self.P})")

        ranges = [i * self.step for i in range(self.P)]
        frames: [Image] = []

        for frame in range(self.FRAMES):
            state = self.update(frame)
            roots = self._find_roots(state)

            with mp.Pool() as p:
                segments = p.map(partial(self._generate_segment, roots, state), ranges)

            frames.append(Image.fromarray(np.uint8(np.concatenate(segments, axis=1)), mode="RGB"))
            print(f"frame {frame} complete")

        first, *rest = frames
        first.save(output, save_all=True, append_images=rest, duration=1000//30, loop=0)

        if self.TIMED:
            print(f"Took {time() - start_time:.2f} seconds!")
