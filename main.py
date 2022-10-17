import numpy as np
import multiprocessing as mp
from PIL import Image
from math import isfinite
from cmath import log
from functools import partial


class Escape(Exception):
    """"""


WIDTH = 1920
HEIGHT = 1080
TOLERANCE = 0.000001
MAX_ITERATION = 100
X_RANGE = -0.8, 0.8
Y_RANGE = -1.1776, -0.2776

P = mp.cpu_count()
STEP = WIDTH // P
FRAMES = 30

state = {}

if WIDTH % P != 0:
    raise Exception(f"Image width ({WIDTH}) not evenly divisible over the amount of cores ({P})")


phi = (1 + 5 ** 0.5) / 2


def func(z: complex, st) -> complex:
    return log(z ** 4 - z * (state['factor'] * 1j))


def deriv(z: complex, st) -> complex:
    h = 0.000000001
    return (func(z + h, st) - func(z - h, st)) / (2 * h)


def find_roots(st) -> [complex]:
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

                        if abs(diff.real) < TOLERANCE and abs(diff.imag) < TOLERANCE:
                            raise Escape

                    for b in range(10):
                        if not isfinite(z.real) or not isfinite(z.imag):
                            raise Escape

                        if deriv(z, st) != (0 + 0j):
                            try:
                                z -= func(z, st) / deriv(z, st)
                            except ZeroDivisionError:
                                raise Escape
                        else:
                            raise Escape
                found.append(z)
            except (Escape, ZeroDivisionError, OverflowError, ValueError):
                continue
    return found


def find_root(z: complex, roots: [complex], st) -> (int, int):
    for i in range(MAX_ITERATION):
        try:
            z -= func(z, st) / deriv(z, st)
        except:
            return -1, 0

        for c, root in enumerate(roots):
            diff = z - root

            if abs(diff.real) < TOLERANCE and abs(diff.imag) < TOLERANCE:
                return c, i

    return -1, 0


def adapt(val, depth):
    return max(0, val - depth)


def get_color(z: complex, roots: [complex], st) -> (int, int, int):
    root, depth = find_root(z, roots, st)

    if root == 0:
        return (adapt(c, depth) for c in (255, 0, 0))
    elif root == 1:
        return (adapt(c, depth) for c in (0, 255, 0))
    elif root == 2:
        return (adapt(c, depth) for c in (0, 0, 255))
    elif root == 3:
        return (adapt(c, depth) for c in (255, 255, 0))

    return 0, 0, 0


def convert_range(n, old_mn, old_mx, new_mn, new_mx):
    return (((n - old_mn) * (new_mx - new_mn)) / (old_mx - old_mn)) + new_mn


def generate_segment(st, segment: int) -> np.ndarray:
    img = np.zeros(shape=(HEIGHT, STEP, 3))

    roots = find_roots(st)

    for x in range(STEP):
        for y in range(HEIGHT):
            rl = convert_range(x + segment, 0, WIDTH, *X_RANGE)
            im = convert_range(y, 0, HEIGHT, *Y_RANGE)

            r, g, b = get_color(rl + im * 1j, roots, st)
            img[y, x, 0] = r
            img[y, x, 1] = g
            img[y, x, 2] = b

    return img


if __name__ == "__main__":
    ranges = [i * STEP for i in range(P)]

    for frame in range(FRAMES):
        state['factor'] = convert_range(frame, 0, FRAMES, 1, phi)
        factor = convert_range(frame, 0, FRAMES, 1, phi)

        with mp.Pool() as p:
            segments = p.map(partial(generate_segment, state), ranges)

        image = Image.fromarray(np.uint8(np.concatenate(segments, axis=1)), mode="RGB").transpose(Image.FLIP_TOP_BOTTOM)
        image.save(f"gif/{frame}.png")
        print(f"Finished frame {frame} using factor {state['factor']}")
