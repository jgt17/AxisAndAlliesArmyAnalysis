from enum import Enum


# unit type definitions
class UnitTypes(Enum):
    LAND = 0
    AIR = 1
    SEA = 3


# unit definitions
# "name":(cost,
#         attack,
#         defence,
#         receives support,
#         gives support,
#         movement,
#         hit points,
#         type,
#         attackable_types,
#         first strike,
#         prevents first strike,
#         can bombard,
#         attacks all attackable,
#         attacks once,
#         unique)
units = {"AA_GUN":(5, 0, 1, False, False, 1, -1, UnitTypes.LAND,
              (UnitTypes.AIR,), True, False, False, True, True, True),

            "INFANTRY": (3, 1, 2, True, False, 1, 1, UnitTypes.LAND,
                        (UnitTypes.LAND, UnitTypes.AIR), False, False, False, False, False, False),
            "ARTILLERY": (4, 2, 2, False, True, 1, 1, UnitTypes.LAND,
                         (UnitTypes.LAND, UnitTypes.AIR), False, False, False, False, False, False),
            "TANK": (5, 3, 3, False, False, 2, 1, UnitTypes.LAND,
                    (UnitTypes.LAND, UnitTypes.AIR), False, False, False, False, False, False),

            "FIGHTER": (10, 3, 4, False, False, 4, 1, UnitTypes.AIR,
                       (UnitTypes.LAND, UnitTypes.AIR, UnitTypes.SEA), False, False, False, False, False, False),
            "BOMBER": (15, 4, 1, False, False, 6, 1, UnitTypes.AIR,
                      (UnitTypes.LAND, UnitTypes.AIR, UnitTypes.SEA), False, False, False, False, False, False),

            "TRANSPORT":(8, 0, 1, False, False, 2, 1, UnitTypes.SEA,
                         (UnitTypes.AIR, UnitTypes.SEA), False, False, False, False, False, False),
            "AIRCRAFT_CARRIER":(16, 1, 3, False, False, 2, 1, UnitTypes.SEA,
                                (UnitTypes.AIR, UnitTypes.SEA), False, False, False, False, False, False),
            "SUBMARINE":(8, 2, 2, False, False, 2, 1, UnitTypes.SEA,
                         (UnitTypes.SEA,), True, False, False, False, False, False),
            "DESTROYER":(12, 3, 3, False, False, 2, 1, UnitTypes.SEA,
                         (UnitTypes.SEA, UnitTypes.AIR), False, True, False, False, False, False),
            "BATTLESHIP":(24, 4, 4, False, False, 2, 2, UnitTypes.SEA,
                          (UnitTypes.SEA, UnitTypes.AIR), False, False, True, False, False, False)}

# generate intermediate units for multiple hit points
units_to_add = []
for unit_name, properties in units.items():
    if properties[6] > 1:
        for i in range(1, properties[6]):
            new_properties = list(properties)
            new_properties[6] = properties[6] - i
            new_properties[0] = float('inf')
            units_to_add.append((unit_name + ("_"*i), tuple(new_properties)))
for new_unit in units_to_add:
    units[new_unit[0]] = new_unit[1]

Units = Enum("Units", units, module=__name__)


# property access methods
def get_name(cls):
    return cls.name.lower()


def get_cost(cls):
    return cls.value[0]


def get_attack(cls):
    return cls.value[1]


def get_defense(cls):
    return cls.value[2]


def receives_support(cls):
    return cls.value[3]


def gives_support(cls):
    return cls.value[4]


def get_movement(cls):
    return cls.value[5]


def get_hit_points(cls):
    return cls.value[6]


def get_type(cls):
    return cls.value[7]


def get_attackable_types(cls):
    return cls.value[8]


def has_first_strike(cls):
    return cls.value[9]


def prevents_first_strike(cls):
    return cls.value[10]


def can_bombard(cls):
    return cls.value[11]


def attacks_all(cls):
    return cls.value[12]


def attacks_once(cls):
    return cls.value[13]


def is_unique(cls):
    return cls.value[14]


def __repr__(cls):
    return cls.name


def get_damaged_unit(cls, damage):
    if 0 > damage >= get_hit_points(cls):
        raise Exception("Tried to get a " + str(cls) + " with " + str(damage) + "damage")
    return Units[cls.name + "_"*damage]


def get_base_unit(cls):
    return Units[cls.name.rstrip('_')]


# bind the methods
setattr(Units, 'get_name', get_name)
setattr(Units, 'get_cost', get_cost)
setattr(Units, 'get_attack', get_attack)
setattr(Units, 'get_defense', get_defense)
setattr(Units, 'receives_support', receives_support)
setattr(Units, 'gives_support', gives_support)
setattr(Units, 'get_movement', get_movement)
setattr(Units, 'get_hit_points', get_hit_points)
setattr(Units, 'get_type', get_type)
setattr(Units, 'get_attackable_types', get_attackable_types)
setattr(Units, 'has_first_strike', has_first_strike)
setattr(Units, 'prevents_first_strike', prevents_first_strike)
setattr(Units, 'can_bombard', can_bombard)
setattr(Units, 'attacks_all', attacks_all)
setattr(Units, 'attacks_once', attacks_once)
setattr(Units, 'is_unique', is_unique)
setattr(Units, '__repr__', __repr__)
setattr(Units, 'get_damaged_unit', get_damaged_unit)
setattr(Units, "get_base_unit", get_base_unit)