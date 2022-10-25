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

Then all you have to do is add `fractal.py` to your project and you should be ready to go!  

## How to use:
`fractal.py` contains two classes: `FractalImage` and `FractalAnimation`.  
To use these classes they must be inherited by a custom class, as follows:  
```python
from fractal import FractalImage

class Fractal(FractalImage):
    def func(self, z: complex, state: dict) -> complex:
        ...

    def get_color(self, root: int, depth: int, smooth: float, state: dict) -> (int, int, int):
        ...
```

Important to note is that both `FractalImage` and `FractalAnimation` are abstract base classes, meaning they have abstract methods which must be implemented when the class is inherited.

Both classes have the following methods which must be implemented:  
`func(self, z: complex, state: dict) -> complex` which is the 
