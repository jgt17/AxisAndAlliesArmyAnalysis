from enum import Enum


# unit type definitions
class UnitTypes(Enum):
    LAND = 0
    AIR = 1
    SEA = 3


# unit definitions
class Units(Enum):
    # name=(
    # cost,
    # attack,
    # defence,
    # receives support,
    # gives support,
    # movement,
    # hit points,
    # type,
    # attackable_types,
    # first strike,
    # prevents first strike,
    # can bombard,
    # attacks all attackable,
    # attacks once,
    # unique)

    AA_GUN = (5, 0, 1, False, False, 1, -1, UnitTypes.LAND,
              (UnitTypes.AIR), True, False, False, True, True, True)

    INFANTRY = (3, 1, 2, True, False, 1, 1, UnitTypes.LAND,
                (UnitTypes.LAND, UnitTypes.AIR), False, False, False, False, False, False)
    ARTILLERY = (4, 2, 2, False, True, 1, 1, UnitTypes.LAND,
                 (UnitTypes.LAND, UnitTypes.AIR), False, False, False, False, False, False)
    TANK = (5, 3, 3, False, False, 2, 1, UnitTypes.LAND,
            (UnitTypes.LAND, UnitTypes.AIR), False, False, False, False, False, False)

    FIGHTER = (10, 3, 4, False, False, 4, 1, UnitTypes.AIR,
               (UnitTypes.LAND, UnitTypes.AIR, UnitTypes.SEA), False, False, False, False, False, False)
    BOMBER = (15, 4, 1, False, False, 6, 1, UnitTypes.AIR,
              (UnitTypes.LAND, UnitTypes.AIR, UnitTypes.SEA), False, False, False, False, False, False)

    TRANSPORT = (8, 0, 1, False, False, 2, 1, UnitTypes.SEA,
                 (UnitTypes.AIR, UnitTypes.SEA), False, False, False, False, False, False)
    AIRCRAFT_CARRIER = (16, 1, 3, False, False, 2, 1, UnitTypes.SEA,
                        (UnitTypes.AIR, UnitTypes.SEA), False, False, False, False, False, False)
    SUBMARINE = (8, 2, 2, False, False, 2, 1, UnitTypes.SEA,
                 (UnitTypes.SEA,), True, False, False, False, False, False)
    DESTROYER = (12, 3, 3, False, False, 2, 1, UnitTypes.SEA,
                 (UnitTypes.SEA, UnitTypes.AIR), False, True, False, False, False, False)
    BATTLESHIP = (24, 4, 4, False, False, 2, 2, UnitTypes.SEA,
                  (UnitTypes.SEA, UnitTypes.AIR), False, False, True, False, False, False)

    def get_name(self):
        return self.name.lower()

    def get_cost(self):
        return self.value[0]

    def get_attack(self):
        return self.value[1]

    def get_defense(self):
        return self.value[2]

    def receives_support(self):
        return self.value[3]

    def gives_support(self):
        return self.value[4]

    def get_movement(self):
        return self.value[5]

    def get_hit_points(self):
        return self.value[6]

    def get_type(self):
        return self.value[7]

    def get_attackable_types(self):
        return self.value[8]

    def is_first_strike(self):
        return self.value[9]

    def prevents_first_strike(self):
        return self.value[10]

    def can_bombard(self):
        return self.value[11]

    def attacks_all(self):
        return self.value[12]

    def attacks_once(self):
        return self.value[13]

    def is_unique(self):
        return self.value[14]

    def __repr__(self):
        return self.name
