from helpers import *

WaterTile = "~"
ShipTile = "O"
HitTile = "X"
MissTile = "T"
FieldSize: int = 6
Fleet = [(3, 1), (2, 2), (1, 4)]

class Ship:
    _size: int = 1

    def __init__(self, size: int, location: Vector2Int, direction: Vector2Int):
        self._size = size
        self._location = location
        self._direction = direction

    @property
    def size(self):
        return self._size

    @property
    def location(self):
        return self._location

    def get_coordinates(self):
        return [self._location + (self._direction * _) for _ in range(self._size)]

class Field:

    def __init__(self, size: int = 6):
        self._size = size
        self._field = [[WaterTile for _ in range(size)] for _ in range(size)]

    def get_row(self, row: int, fog_of_war: bool = False):

        if not fog_of_war:
            return self._field[row]
        else:
            return [x.replace(ShipTile, WaterTile) for x in self._field[row]]

    def place_ship(self, ship: Ship):

        for coord in ship.get_coordinates():

            if not coord.is_in_square_bounds(self._size):
                raise ActionOutOfFieldError

            if self._field[coord.x][coord.y] == ShipTile:
                raise ShipIntersectionError

            for direction in Directions.all():
                offset = coord + direction
                if not offset.is_in_square_bounds(self._size):
                    continue
                if self._field[offset.x][offset.y] == ShipTile:
                    raise ShipIntersectionError

        else:
            for c in ship.get_coordinates():
                self._field[c.x][c.y] = ShipTile

    def place_shot(self, shot: Vector2Int):

        if not shot.is_in_square_bounds(self._size):
            raise ActionOutOfFieldError

        if self._field[shot.x][shot.y] in [HitTile, MissTile]:
            raise HittingTwiceError

        if self._field[shot.x][shot.y] == WaterTile:
            self._field[shot.x][shot.y] = MissTile
            return
        elif self._field[shot.x][shot.y] == ShipTile:
            self._field[shot.x][shot.y] = HitTile
            return

    def contains_ships(self):
        for row in range(FieldSize):
            if ShipTile in self.get_row(row):
                return True
        return False

class Player:
    def __init__(self):
        self._field = Field(FieldSize)
        self._fleet = Fleet

    def place_boats(self):
        pass

    def shoot(self, opponent_field: Field):
        pass

    @property
    def get_field(self):
        return self._field

    def reset_field(self):
        self._field = Field()


class Human(Player):

    @staticmethod
    def _query_ship_input(size: int):
        while True:
            try:
                location = input(f"place the ship with the size {size}"
                                 f" and direction ( u, d, r, l) in format 'x y dir': \n"
                                 f"'2 3 u'").split(" ")
                if len(location) != 3:
                    continue
                if len(location[-1]) != 1 or location[-1].lower() not in "udrl":
                    continue
                return Ship(size, Vector2Int(int(location[0]), int(location[1])), Directions.parse_from_string(location[-1].lower()))
            except ValueError:
                continue

    @staticmethod
    def _query_shot_input():
        while True:
            try:
                coords = input(f"enter coordinates to make a shot in format 'x y': '2 4'").split(" ")
                return Vector2Int(int(coords[0]), int(coords[1]))
            except (ValueError, IndexError):
                continue

    def _print_field(self):
        print(*range(FieldSize))
        for row in range(FieldSize):
            print(*self._field.get_row(row) + [row])

    def place_boats(self):
        for boat_type in self._fleet:
            for amount in range(boat_type[1]):
                while True:
                    try:
                        self._field.place_ship(Human._query_ship_input(boat_type[0]))
                        self._print_field()
                        print("success")
                        break
                    except ShipIntersectionError:
                        print("ships are intersecting or too close, the distance between ships must be at least 1 tile")
                        continue
                    except ActionOutOfFieldError:
                        print("the ship (or it's parts) are outside of the field")
                        continue

    def shoot(self, opponent_field: Field):
        while True:
            try:
                opponent_field.place_shot(Human._query_shot_input())
                break
            except HittingTwiceError:
                print("you have already shot there!")
                continue
            except ActionOutOfFieldError:
                print("trying to shoot outside the field")
                continue


class Bot(Player):

    def place_boats(self):
        while True:
            try:
                self._place_boats()
                break
            except FieldPopulationFailed:
                self.reset_field()
                continue

    def _place_boats(self):
        for ship in self._fleet:
            size = ship[0]
            for amount in range(ship[1]):
                ship_placed = False
                attempts = 0

                while not ship_placed:
                    if attempts >= 10000:
                        raise FieldPopulationFailed
                    rand_coords = Vector2Int.get_random_in_range(FieldSize)
                    dir_count = 0
                    while dir_count < 4:
                        attempts += 1
                        dir_count += 1
                        try:
                            self._field.place_ship(Ship(size, rand_coords, Directions.all()[dir_count]))
                            ship_placed = True
                            break
                        except (ActionOutOfFieldError, ShipIntersectionError):
                            continue
                        except IndexError:
                            break

    def shoot(self, opponent_field: Field):
        while True:
            try:
                random_coords = Vector2Int.get_random_in_range(FieldSize)
                opponent_field.place_shot(random_coords)
                break
            except (HittingTwiceError, ActionOutOfFieldError):
                continue


def game_loop():

    def _print_fields():
        spaces = list("      ")
        print(*([*range(FieldSize)] + [" "] + spaces + [" "] + [*range(FieldSize)]))
        for row in range(FieldSize):
            print(*(human_field.get_row(row) + [row] + spaces + [row] + bot_field.get_row(row, True)))

    human = Human()
    human_field = human.get_field
    bot = Bot()
    bot_field = bot.get_field
    bot.place_boats()
    human.place_boats()

    _print_fields()
    while True:
        human.shoot(bot_field)
        if not bot_field.contains_ships():
            _print_fields()
            print("you won!")
            break
        _print_fields()
        bot.shoot(human_field)
        if not human_field.contains_ships():
            _print_fields()
            print("bot won")
            break
        _print_fields()


game_loop()
