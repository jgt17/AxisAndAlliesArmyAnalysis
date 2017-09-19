import pickle
import os

from units import Units
from config import land_battle_units, sea_battle_units


# generate all the possible armies with the money available
def generate_possible_armies(money, *allowed_unit_types, prohibited_units=(), land_battle=True, use_all_money=True):
    if (money > 400 and land_battle) or (money > 500 and not land_battle):
        raise Exception("Too many possibilities to compute.")
    # default land battle
    if not allowed_unit_types:
        allowed_unit_types = land_battle_units if land_battle else sea_battle_units

    # get list of permitted units
    allowed_units = [unit for unit in list(Units)
                     if (unit.get_type() in allowed_unit_types or
                         (unit.get_type() not in allowed_unit_types and unit.can_bombard()))
                     and unit not in prohibited_units]

    # configurations waiting to be completed
    working_set = set()
    # configurations seen at some point
    visited_set = set()
    # the list of complete configurations
    finished_set = set()

    # if not required to use all the money possible, every set is valid and finished
    if not use_all_money:
        visited_set = finished_set

    # gives the index of the unit in the tuples used at this stage
    # dicts are mutable and therefore cannot go in sets
    def army_index(unit):
        return allowed_units.index(unit)
    money_index = len(allowed_units)

    # buy one unit
    def generate_next_armies(current_resources):
        visited_set.add(current_resources)
        out_of_money = True
        for unit in allowed_units:
            if current_resources[money_index] >= unit.get_cost() and\
                    (not unit.is_unique() or current_resources[army_index(unit)] == 0):
                out_of_money = False
                new_resources_list = list(current_resources)
                new_resources_list[army_index(unit)] += 1
                new_resources_list[money_index] -= unit.get_cost()
                new_resources = tuple(new_resources_list)
                if new_resources not in visited_set:
                    working_set.add(new_resources)
        if out_of_money:
            finished_set.add(current_resources)

    empty_army = (0,)*len(allowed_units)
    working_set.add(empty_army + (money,))

    # generate all the armies
    i = 0
    while working_set:  # while the working set is not empty
        configuration = working_set.pop()
        generate_next_armies(configuration)
        if i % 100000 == 0:
            print(str(money) + "  "
                  + str(len(working_set)) + "  " + str(len(finished_set)))
        i += 1

    print(str(len(working_set)) + "  " + str(len(visited_set)) + "  " + str(len(finished_set)))

    # put results in a nicer format
    # helper function to convert the tuples describing the army configuration into more useful dicts
    def configuration_to_dict(configuration):
        dict_version = {}
        for unit in allowed_units:
            dict_version[unit] = configuration[army_index(unit)]
        dict_version["MONEY"] = configuration[money_index]
        return dict_version

    possible_armies_raw_list = sorted(list(finished_set))
    return [configuration_to_dict(configuration) for configuration in possible_armies_raw_list]


# generate list of armies and save it for future use
def generate_and_save_possible_armies(money, *allowed_unit_types, prohibited_units=(), land_battle, use_all_money=True):
    if not os.path.isdir("armies"):
        os.mkdir("armies")
    armies = generate_possible_armies(money,
                                      *allowed_unit_types,
                                      prohibited_units=prohibited_units,
                                      land_battle=land_battle,
                                      use_all_money=use_all_money)
    with open(get_filename(money, land_battle, use_all_money), "wb") as saveLoc:
        pickle.dump(armies, saveLoc)
    return armies


# get the filename of possible armies for a certain config
def get_filename(money, land_battle, use_all_money=True):
    return "armies/possible_armies_" + str(money) + \
           ("_land" if land_battle else "_sea") + ("_leftover_money_allowed" if not use_all_money else "")


# load the possible armies from a file if it exists, otherwise generate the armies, save it, and load it
def get_possible_armies(money, land_battle, use_all_money=True):
    filename = get_filename(money, land_battle, use_all_money)
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
    else:
        print("Generating Armies")
        return generate_and_save_possible_armies(money, land_battle=land_battle, use_all_money=use_all_money)


# generate common possible armies
def generate_and_save_armies_for_common_money_amounts():
    land_battle = True
    money = 10
    if not os.path.isfile(get_filename(money, land_battle)):
        generate_and_save_possible_armies(money, land_battle=land_battle)
    for money in range(50, 400, 50):
        if not os.path.isfile(get_filename(money, land_battle)):
            generate_and_save_possible_armies(money, land_battle=land_battle)

    land_battle = False
    money = 10
    if not os.path.isfile(get_filename(money, land_battle)):
        generate_and_save_possible_armies(money, land_battle=land_battle)
    for money in range(50, 600, 50):
        if not os.path.isfile(get_filename(money, land_battle)):
            generate_and_save_possible_armies(money, land_battle=land_battle)


if __name__ == "__main__":
    generate_and_save_armies_for_common_money_amounts()