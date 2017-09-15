import pickle
import os

from units import Units
from config import attacker_available_money, defender_available_money, is_land_battle
from config import land_battle_units, sea_battle_units


# generate all the possible armies with the money available
def generate_possible_armies(*allowed_unit_types, prohibited_units=(), use_all_money=True, attacking=True):
    # default land battle
    if not allowed_unit_types:
        allowed_unit_types = land_battle_units if is_land_battle else sea_battle_units

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
    working_set.add(empty_army + (attacker_available_money if attacking else defender_available_money,))

    # generate all the armies
    i = 0
    while working_set:  # while the working set is not empty
        configuration = working_set.pop()
        generate_next_armies(configuration)
        if i % 100000 == 0:
            print(str(attacker_available_money if attacking else defender_available_money) + "  "
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
def generate_and_save_possible_armies(*allowed_unit_types, prohibited_units=(), use_all_money=True, attacking=True):
    if not os.path.isdir("armies"):
        os.mkdir("armies")
    with open(get_filename_from_config(use_all_money, attacking), "wb") as saveLoc:
        pickle.dump(generate_possible_armies(*allowed_unit_types,
                                             prohibited_units=prohibited_units, use_all_money=use_all_money),
                    saveLoc)


# get the filename of possible armies for a certain config
def get_filename_from_config(use_all_money=True, attacking=True):
    return "armies/possible_armies_" + str(attacker_available_money if attacking else defender_available_money) + \
           ("_land" if is_land_battle else "_sea") + ("_leftover_money_allowed" if not use_all_money else "")


if __name__ == "__main__":
    is_land_battle = True
    attacker_available_money = 10
    if not os.path.isfile(get_filename_from_config()):
        generate_and_save_possible_armies()
    for i in range(50, 600, 50):
        attacker_available_money = i
        if not os.path.isfile(get_filename_from_config()):
            generate_and_save_possible_armies()

    is_land_battle = False
    attacker_available_money = 10
    if not os.path.isfile(get_filename_from_config()):
        generate_and_save_possible_armies()
    for i in range(50, 600, 50):
        attacker_available_money = i
        if not os.path.isfile(get_filename_from_config()):
            generate_and_save_possible_armies()