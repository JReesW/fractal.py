# fractal.py
Python library to easily generate custom Newton fractals!

## About
Newton fractals are a kind of fractal which can be generated for any holomorphic function $f(z)$, by repeatedly applying Newton's method and assigning a color depending on which root of $f(z)$ it reaches.  

This library aims to ease the process of generating these fractals, circumventing a lot of common problems one would run into, and even allowing more complicated functions than just standard polynomials.

All you have to do is provide a function $f(z)$, and a method for determining color.  
Also able to generate GIFs, provided an update function is given deciding what to change each frame.

## Installation:
Install numpy and pillow as follows:  
`pip install numpy`  
`pip install pillow`  

Then all you have to do is add `fractal.py` to your project, and you should be ready to go!  

## How to use:
`fractal.py` contains two classes for usage: `FractalImage` and `FractalAnimation`.  
Let's look at an example of a `FractalImage` implementation:

```python
from fractal import FractalImage


class Fractal(FractalImage):
  def func(self, z: complex, state: dict) -> complex:
    return z ** 3 - 1

  def color(self, root: int, depth: int, smooth: float, state: dict) -> (int, int, int):
    depth += smooth
    if root == 0:
      return (int(max(0, c - 8 * depth)) for c in (255, 0, 0))
    elif root == 1:
      return (int(max(0, c - 8 * depth)) for c in (0, 255, 0))
    elif root == 2:
      return (int(max(0, c - 8 * depth)) for c in (0, 0, 255))

    return 0, 0, 0


if __name__ == '__main__':
  fractal = Fractal()
  fractal.generate("output.png")
```
As can be seen, to use the classes, they need to be inherited from.  
This is because both `FractalImage` and `FractalAnimation` are abstract base classes.  
They have abstract methods which must be implemented when the class is inherited, otherwise errors will be raised.

Both classes have the following abstract methods which must be implemented:  
* `func(self, z: complex, state: dict) -> complex`
  * The holomorphic function $f(z)$, which determines the shape of the fractal
  * Parameter `z: complex`: the complex number input
  * Parameter `state: dict`: dynamic values used when generating an animation
  * Returns a new complex number


* `color(self, root: int, depth: int, smooth: float, state: dict) -> (int, int, int)`
  * The function deciding which color to assign to the result
  * Parameter `root: int`: the index of the root reached, generally decides which base color should be used (`-1` if no root is reached)
  * Parameter `depth: int`: the amount of iterations it took to reach this result, generally used for shading
  * Parameter `smooth: float`: the smoothening factor, to circumvent "banding" (see [this article](https://www.chiark.greenend.org.uk/~sgtatham/newton/), last part of "Decoration")
  * Parameter `state: dict`: internal information, here the dynamic values can be found which change during an animation
  * Returns a triplet of integers, the RGB values (0 - 255 inclusive)
  
&nbsp;  
The class `FractalAnimation` has an additional abstract method:
* `update(self, frame: int) -> dict`
  * The function updating the state each frame
  * Parameter `frame: int`: the current frame number
  * Returns a dictionary, which will be sent to `func()` and `color()` as the parameter `state`

&nbsp;  
After creating the class and implementing the abstract methods, the custom class can be instantiated.  
Due to `fractal.py` relying on the `multiprocessing` library to render images, 
it is required to start generation inside the `__name__ == '__main__'` guard, like so:
```python
if __name__ == '__main__':
    fractal = Fractal()  # instantiate the custom class from the example above
    fractal.WIDTH = 1920
    fractal.HEIGHT = 1080
    fractal.generate("output.png")
```
As can be seen, the classes have some attributes which can be set after instantiation.  
These are generation settings, and they are as follows:
```text
WIDTH -> The width in pixels of the image (default 1920)
HEIGHT -> The height in pixels of the image (default 1080)
X_RANGE -> The range of the real values (default (-7.111, 7.111))
Y_RANGE -> The range of the imaginary values (default (-4, 4))

TOLERANCE -> How close a complex number must be to a root to be accepted (default 0.000001)
MAX_ITERATIONS -> The maximum number of iterations to find a root (default 100)

P -> The amount of CPU cores used to render (default all cores) (Important! WIDTH must be evenly divisible by P)
FRAMES -> The amount of frames the animation should consist of (default 60) (Animations are 30 FPS)
TIMED -> Whether to print how long it took to render (default False)
```

Finally, the `.generate()` method should be called, which will start generation of the image and will save the image to the given path.

Multiple examples of how to use this can be found in the `examples/` directory.
