from enum import Enum
from random import Random


class Vector2Int:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

    def __add__(self, other):
        if isinstance(other, int):
            return Vector2Int(self.x + other, self.y + other)
        elif isinstance(other, Vector2Int):
            return Vector2Int(self.x + other.x, self.y + other.y)
        else:
            raise TypeError

    def __mul__(self, other):
        if isinstance(other, int):
            return Vector2Int(self.x * other, self.y * other)
        elif isinstance(other, Vector2Int):
            return Vector2Int(self.x * other.x, self.y * other.y)
        else:
            raise TypeError

    def is_in_square_bounds(self, square_size: int):
        if 0 <= self.x < square_size and 0 <= self.y < square_size:
            return True
        else:
            return False

    @staticmethod
    def get_random_in_range(rng: int):
        return Vector2Int(Random().randint(0, rng), Random().randint(0, rng))

class Directions(Enum):
    left = Vector2Int(0, -1)
    right = Vector2Int(0, 1)
    up = Vector2Int(-1, 0)
    down = Vector2Int(1, 0)

    @staticmethod
    def all():
        return [Directions.left.value, Directions.right.value, Directions.up.value, Directions.down.value]

    @staticmethod
    def parse_from_string(s):
        match s:
            case "l":
                return Directions.left.value
            case "r":
                return Directions.right.value
            case "u":
                return Directions.up.value
            case "d":
                return Directions.down.value
            case _:
                return Directions.right.value


class ActionOutOfFieldError(BaseException):
    pass

class ShipIntersectionError(BaseException):
    pass

class HittingTwiceError(BaseException):
    pass

class FieldPopulationFailed(BaseException):
    pass
