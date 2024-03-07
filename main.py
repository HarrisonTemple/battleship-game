from helpers import *

water_tile = "~"
ship_tile = "O"
hit_tile = "X"
miss_tile = "T"
field_size: int = 6
fleet = [(3, 1), (2, 2), (1, 4)]

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
        self._field = [[water_tile for _ in range(size)] for _ in range(size)]

    def get_row(self, row: int, fog_of_war: bool):

        if not fog_of_war:
            return self._field[row]
        else:
            return [x.replace(ship_tile, water_tile) for x in self._field[row]]

    def place_ship(self, ship: Ship):

        for coord in ship.get_coordinates():

            if not coord.is_in_square_bounds(self._size):
                raise ActionOutOfFieldError

            if self._field[coord.x][coord.y] == ship_tile:
                raise ShipIntersectionError

            for direction in Directions.all():
                offset = coord + direction
                if not offset.is_in_square_bounds(self._size):
                    continue
                if self._field[offset.x][offset.y] == ship_tile:
                    raise ShipIntersectionError

        else:
            for c in ship.get_coordinates():
                self._field[c.x][c.y] = ship_tile

    def place_shot(self, shot: Vector2Int):

        if not shot.is_in_square_bounds(self._size):
            raise ActionOutOfFieldError

        if self._field[shot.x][shot.y] in [hit_tile, miss_tile]:
            raise HittingTwiceError

        if self._field[shot.x][shot.y] == water_tile:
            self._field[shot.x][shot.y] = miss_tile
            return
        elif self._field[shot.x][shot.y] == ship_tile:
            self._field[shot.x][shot.y] = hit_tile
            return

class Player:
    def __init__(self):
        self._field = Field(field_size)
        self._fleet = fleet

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
        print(*range(field_size))
        for row in range(field_size):
            print(*self._field.get_row(row, False) + [row])

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
                    rand_coords = Vector2Int.get_random_in_range(field_size)
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
                random_coords = Vector2Int.get_random_in_range(field_size)
                opponent_field.place_shot(random_coords)
                break
            except (HittingTwiceError, ActionOutOfFieldError):
                continue


def game_loop():

    def _print_fields():
        spaces = list("      ")
        print(*([*range(field_size)] + [" "] + spaces + [" "] + [*range(field_size)]))
        for row in range(field_size):
            print(*(human_field.get_row(row, False) + [row] + spaces + [row] + bot_field.get_row(row, True)))

    def _contains_ships(field: Field):
        contains_ships = False
        for row in range(field_size):
            if ship_tile in field.get_row(row, False):
                contains_ships = True
            else:
                contains_ships = False
        return contains_ships

    human = Human()
    human_field = human.get_field
    bot = Bot()
    bot_field = bot.get_field
    bot.place_boats()
    human.place_boats()

    _print_fields()
    while True:
        human.shoot(bot_field)
        if not _contains_ships(bot_field):
            print("you won!")
            break
        _print_fields()
        bot.shoot(human_field)
        if not _contains_ships(human_field):
            print("bot won")
            break
        _print_fields()


game_loop()