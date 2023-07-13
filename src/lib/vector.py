import math
from typing import Union, Tuple, List


class Vector2D:
    def __init__(self, x: Union[int, float] = 0, y: Union[int, float] = 0):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"Vector2D({self.x}, {self.y})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vector2D(self.x * other, self.y * other)
        elif isinstance(other, Vector2D):
            return self.x * other.x + self.y * other.y
        else:
            raise TypeError(f"Unsupported operand type(s) for *: '{type(self)}' and '{type(other)}'")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __abs__(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __iter__(self):
        return iter((self.x, self.y))

    def __tuple__(self):
        return self.x, self.y

    def rotate(self, rotation_matrix) -> "Vector2D":
        a, b = rotation_matrix[0]
        c, d = rotation_matrix[1]
        x, y = (a * self.x + b * self.y, c * self.x + d * self.y)
        if math.isclose(x, 0, abs_tol=1e-9):
            x = 0
        if math.isclose(y, 0, abs_tol=1e-9):
            y = 0
        return Vector2D(x, y)

    def flip_horizontally(self) -> "Vector2D":
        return Vector2D(self.x * -1, self.y)

    def flip_vertically(self) -> "Vector2D":
        return Vector2D(self.x, self.y * -1)

    def normalize(self) -> "Vector2D":
        mag = abs(self)
        if mag > 0:
            return Vector2D(self.x / mag, self.y / mag)
        else:
            return Vector2D(0, 0)

    @classmethod
    def from_tuple(cls, vector: Union[Tuple[Union[int, float]], List[Union[int, float]]]) -> "Vector2D":
        if not isinstance(vector, (tuple, list)):
            raise TypeError
        return cls(vector[0], vector[1])
