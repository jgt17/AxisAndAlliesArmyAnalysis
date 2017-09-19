import random
import os
import pickle
from operator import add

from units import Units, UnitTypes
from config import low_luck, retreat_after_round, retreat_when_x_units_left, retreat_when_only_air_left
from config import attacking_land_must_survive, attacker_loss_policy, defender_loss_policy
from config import is_land_battle, land_battle_units, sea_battle_units
from config import attacker_available_money, defender_available_money, battle_simulation_count, use_all_available_money
import loss_policies
from army_generator import get_possible_armies


# get total unit value of an army
def get_tuv(army):
    return sum(unit.get_base_unit().get_cost()*count for unit, count in army.items() if unit in Units)


# roll a bunch of dice
def roll_dice(num_to_roll):
    return [random.randint(1, 6) for i in range(num_to_roll)]


# check hits
def count_hits(die_results, power):
    return sum(1 for result in die_results if result <= power)


# get the number of hits and the units they can apply to
def get_all_hits(rolling_army, receiving_army, is_attacking, is_first_strike, round_of_battle):
    if is_attacking:
        power = Units.get_attack
    else:
        power = Units.get_defense

    # if first strike should be applied
    if is_attacking and is_first_strike:
        if all(not (unit.prevents_first_strike() and count > 0)
               for unit, count in receiving_army.items() if unit in Units):
            striking_army = dict()
            for unit in rolling_army:
                if unit in Units and unit.has_first_strike():
                    striking_army[unit] = rolling_army[unit]
            rolling_army = striking_army
        else:
            return dict()
    # if first strike should not be applied
    elif is_attacking and not is_first_strike and \
            all(not (unit.prevents_first_strike() and count > 0)
                for unit, count in receiving_army.items() if unit in Units):
        non_striking_army = dict()
        for unit in rolling_army:
            if unit in Units and not unit.has_first_strike():
                non_striking_army[unit] = rolling_army[unit]
        rolling_army = non_striking_army
    # if first strike should be ignored
    else:
        pass

    remaining_supporting_units = sum(count for unit, count in rolling_army.items()
                                     if unit in Units and unit.gives_support())
    if remaining_supporting_units > 0:
        exit(0)

    if low_luck:
        damage_type_power = dict()
        for unit, count in rolling_army.items():
            if unit in Units:
                # don't attack if the unit only attacks once
                if unit.attacks_once() and round_of_battle > 0:
                    continue
                # if the unit's attacks do not stack (like aa_guns), only count the attack from one
                if unit.is_unique():
                    count = 1
                # apply support
                if unit.receives_support():
                    supported = min(count, remaining_supporting_units)
                    remaining_supporting_units -= supported
                    count -= supported
                else:
                    supported = 0
                # if the unit attacks each unit it can, instead of just once (again like aa_guns do)
                if unit.attacks_all():
                    for receiving_unit, receiving_count in receiving_army.items():
                        if receiving_unit in Units and (receiving_unit.get_type() in unit.get_attackable_types()):
                            # don't attack units that are technically dead
                            if receiving_unit in damage_type_power:
                                damage_type_power[receiving_unit] += int(((1-((1-power(unit)/6)**count))*6)+0.5)\
                                                                     * receiving_count \
                                                                     + int(
                                                                        ((1-((1-(power(unit)+1)/6)**supported))*6)+0.5)\
                                                                     * receiving_count
                            else:
                                damage_type_power[receiving_unit] = int(((1-((1-power(unit)/6)**count))*6)+0.5)\
                                                                    * receiving_count \
                                                                    + int(
                                                                    ((1-((1-(power(unit)+1)/6)**supported))*6)+0.5)\
                                                                    * receiving_count
                # normal attack
                else:
                    unit_power = power(unit)*count + (power(unit)+1)*supported
                    attackable_types_in_receiving_army = \
                        tuple([receiving_type for receiving_type in unit.get_attackable_types()
                               if any(receiving_unit.get_type() == receiving_type
                                      for receiving_unit in receiving_army if receiving_unit in Units)])
                    if attackable_types_in_receiving_army in damage_type_power:
                        damage_type_power[attackable_types_in_receiving_army] += unit_power
                    else:
                        damage_type_power[attackable_types_in_receiving_army] = unit_power
        hits_per_type_or_unit = dict()
        for type_or_unit, power in damage_type_power.items():
            hits_per_type_or_unit[type_or_unit] = power//6 + count_hits(roll_dice(1), power % 6)
    else:
        hits_per_type_or_unit = dict()
        for unit, count in rolling_army.items():
            if unit in Units and count > 0:
                # don't attack if the unit only attacks once and it's not the first round
                if unit.attacks_once() and round_of_battle > 0:
                    continue
                # if the unit's attacks do not stack (like aa_guns), only count the attack from one
                if unit.is_unique():
                    count = 1
                # apply support
                if unit.receives_support():
                    supported = min(count, remaining_supporting_units)
                    remaining_supporting_units -= supported
                    count -= supported
                else:
                    supported = 0
                # if the unit attacks each unit it can, instead of just once (again like aa_guns do)
                if unit.attacks_all():
                    for receiving_unit, receiving_count in receiving_army.items():
                        if receiving_unit in Units:
                            if receiving_unit.get_type() in unit.get_attackable_types():
                                # don't continue to attack units that have technically been killed
                                for i in range(supported):
                                    if receiving_unit in hits_per_type_or_unit:
                                        hits_per_type_or_unit[receiving_unit] += count_hits(
                                            roll_dice(receiving_count-hits_per_type_or_unit[receiving_unit]),
                                            power(unit)+1)
                                    else:
                                        hits_per_type_or_unit[receiving_unit] = count_hits(
                                            roll_dice(receiving_count-hits_per_type_or_unit[receiving_unit]),
                                            power(unit)+1)
                                for i in range(count):
                                    if receiving_unit in hits_per_type_or_unit:
                                        hits_per_type_or_unit[receiving_unit] += count_hits(
                                            roll_dice(receiving_count - hits_per_type_or_unit[receiving_unit]),
                                            power(unit))
                                    else:
                                        hits_per_type_or_unit[receiving_unit] = count_hits(
                                            roll_dice(receiving_count),
                                            power(unit))
                # normal attack
                else:
                    attackable_types_in_receiving_army = \
                        tuple([receiving_type for receiving_type in unit.get_attackable_types()
                              if any(receiving_unit.get_type() == receiving_type for receiving_unit in receiving_army
                                     if receiving_unit in Units)])
                    if attackable_types_in_receiving_army in hits_per_type_or_unit:
                        hits_per_type_or_unit[attackable_types_in_receiving_army] += \
                            count_hits(roll_dice(count), power(unit)) + count_hits(roll_dice(supported), power(unit)+1)
                    else:
                        hits_per_type_or_unit[attackable_types_in_receiving_army] = \
                            count_hits(roll_dice(count), power(unit)) + count_hits(roll_dice(supported), power(unit) + 1)
    return hits_per_type_or_unit


# apply losses
def apply_losses(army, hits, is_attacking, loss_policy=loss_policies.default, keep_surviving_land=True):
    return loss_policy(army, hits, is_attacking, keep_surviving_land)


# count the units that can be lost an army has left
def count_remaining_units(army):
    return sum(count for unit, count in army.items() if unit in Units and unit.get_hit_points() > 0)


# check whether the attacking army should retreat based on the config
def check_retreat(attacking_army, round_of_battle):
    return 0 <= retreat_after_round <= round_of_battle or \
            0 <= retreat_when_x_units_left <= count_remaining_units(attacking_army) or\
            (retreat_when_only_air_left and 0 == sum(count for unit, count in attacking_army.items()
                                                     if unit in Units and unit.get_type is not UnitTypes.AIR))


# battle emulation
def do_battle(attacking_army, defending_army, land_battle=True):
    # work on copy of armies so battle can be re-run
    attacking_army = attacking_army.copy()
    defending_army = defending_army.copy()

    # record initial tuv of the armies
    attacking_army_tuv = get_tuv(attacking_army)
    defending_army_tuv = get_tuv(defending_army)

    # bombardment loss
    if low_luck:
        bombardment_power = sum(unit.get_attack()*count for unit, count in attacking_army.items()
                                if unit in Units and ((unit.get_type() not in land_battle_units and land_battle) or
                                (unit.get_type() not in sea_battle_units and not land_battle))
                                and unit.can_bombard())
        bombardment_loss_count = bombardment_power//6 + count_hits(roll_dice(1), bombardment_power % 6)
    else:
        bombardment_loss_count = sum(count_hits(roll_dice(count), unit.get_attack())
                                     for unit, count in attacking_army.items()
                                     if unit in Units and
                                     ((unit.get_type() not in land_battle_units and land_battle) or
                                     (unit.get_type() not in sea_battle_units and not land_battle))
                                     and unit.can_bombard())
    bombardment_loss = dict()
    bombardment_loss[land_battle_units if land_battle else sea_battle_units] = bombardment_loss_count
    apply_losses(defending_army, bombardment_loss, False, defender_loss_policy)
    # remove bombardment units from army
    units_to_remove = []
    for unit in attacking_army.keys():
        if unit in Units and ((unit.get_type() not in land_battle_units and land_battle) or
                              (unit.get_type() not in sea_battle_units and not land_battle)):
            units_to_remove.append(unit)
    for unit in units_to_remove:
        del attacking_army[unit]
    units_to_remove = []
    for unit in defending_army.keys():
        if unit in Units and ((unit.get_type() not in land_battle_units and land_battle) or
                              (unit.get_type() not in sea_battle_units and not land_battle)):
            units_to_remove.append(unit)
    for unit in units_to_remove:
        del defending_army[unit]

    # repeat rounds of combat until one side is done or the attacker retreats
    round_of_combat = 0
    while count_remaining_units(attacking_army) > 0\
            and count_remaining_units(defending_army) > 0\
            and not check_retreat(attacking_army, round_of_combat):
        # first strike
        attacker_hits = get_all_hits(attacking_army, defending_army, True, True, round_of_combat)
        defending_army = apply_losses(defending_army, attacker_hits,
                                      False, defender_loss_policy, attacking_land_must_survive)
        # normal combat
        attacker_hits = get_all_hits(attacking_army, defending_army, True, False, round_of_combat)
        defender_hits = get_all_hits(defending_army, attacking_army, False, False, round_of_combat)
        attacking_army = apply_losses(attacking_army, defender_hits,
                                      True, attacker_loss_policy, attacking_land_must_survive)
        defending_army = apply_losses(defending_army, attacker_hits,
                                      False, defender_loss_policy, attacking_land_must_survive)
        round_of_combat += 1

    return [count_remaining_units(attacking_army) > 0,      # won
            count_remaining_units(attacking_army) == 0 and count_remaining_units(defending_army) == 0,    # draw
            count_remaining_units(defending_army) > 0,      # lost
            count_remaining_units(attacking_army),          # number attacking units remaining
            count_remaining_units(defending_army),          # number defending units remaining
            get_tuv(attacking_army) - attacking_army_tuv,   # attacker delta tuv
            get_tuv(defending_army) - defending_army_tuv,   # defender delta tuv
            get_tuv(attacking_army) - attacking_army_tuv - get_tuv(defending_army) + defending_army_tuv,  # tuv swing
            round_of_combat]                            # number of rounds of combat


# do a bunch of battles and aggregate results
def do_many_battles(attacking_army, defending_army, battle_count, land_battle=True):
    print("Simulating Battles\nAttacker: " + str(attacking_army) + "\nDefender: " + str(defending_army))
    # won, draw, lost, attackers remaining, defenders remaining, attack delta tuv, defend delta tuv, tuv swing, rounds
    full_results = (0,)*9
    for i in range(battle_count):
        full_results = [*map(add, full_results, do_battle(attacking_army, defending_army, land_battle))]
        # progress update
        if i % 2000 == 0:
            print("Completed " + str(i+1) + " simulations out of " + str(battle_count))
    return [elem/battle_count for elem in full_results]


# do all possible battles
def do_all_possible_battles(attacker_money, defender_money, battle_count, land_battle=True, use_all_money=True):
    attacker_armies = get_possible_armies(attacker_money, land_battle, use_all_money)
    if defender_money == attacker_money:
        defender_armies = attacker_armies.copy()
    else:
        defender_armies = get_possible_armies(defender_money, land_battle, use_all_money)
    all_results = [[[] for i in range(len(defender_armies))] for i in range(len(attacker_armies))]
    for i, attacker_army in enumerate(attacker_armies):
        for j, defender_army in enumerate(defender_armies):
            all_results[i][j] = do_many_battles(attacker_army, defender_army, battle_count, land_battle)
    return all_results


# generate folder name for storing results of a run
def get_new_folder_name(attacker_money, defender_money, land_battle):
    base = "results_" + ("land_" if land_battle else "sea_") + \
           str(attacker_money) + ("_" + defender_money if attacker_money != defender_money else "")
    if os.path.isdir(base):
        i = 1
        while os.path.isdir(base + "-" + str(i)):
            i += 1
        base += "-" + str(i)
    return base


# save config settings when run
def save_config(folder_name, attacker_money, defender_money, battle_count, land_battle, use_all_money):
    config_settings = "Config:\n\n" \
                      "Attacker Money:             " + str(attacker_money) + "\n" \
                      "Attacker Loss Policy:       " + str(attacker_loss_policy) + "\n\n" \
                      "Defender money:             " + str(defender_money) + "\n" \
                      "Defender Loss Policy:       " + str(defender_loss_policy) + "\n\n" \
                      "" + ("Don't Use All Money\n\n" if not use_all_money else "") + "" \
                      "Battle Type:                " + ("Land" if land_battle else "Sea") + "\n" \
                      "Number of Battles:          " + str(battle_count) + "\n" \
                      "Low Luck:                   " + ("On" if low_luck else "Off") + "\n\n" \
                      "Retreat After Round:        " + str(retreat_after_round) + "\n" \
                      "Retreat When X Units Left:  " + str(retreat_when_x_units_left) + "\n" \
                      "Retreat When Only Air Left: " + ("Yes" if retreat_when_only_air_left else "No")
    with open(folder_name + "/config.txt", "w") as f:
        f.write(config_settings)


# save results of all possible battles with the config that made them
def generate_and_save_all_battles(attacker_money, defender_money, battle_count, land_battle=True, use_all_money=True):
    folder_name = get_new_folder_name(attacker_money, defender_money, land_battle)
    os.mkdir(folder_name)
    save_config(folder_name, attacker_money, defender_money, battle_count, land_battle, use_all_money)
    results = do_all_possible_battles(attacker_money, defender_money, battle_count, land_battle, use_all_money)
    with open(folder_name + "/full_results", "wb") as f:
        pickle.dump(results, f)
    return results


if __name__ == "__main__":
    results = generate_and_save_all_battles(attacker_available_money,
                                            defender_available_money,
                                            battle_simulation_count,
                                            is_land_battle,
                                            use_all_available_money)
    for row in results:
        print([col[0] for col in row])
    attacker_possible_armies = get_possible_armies(attacker_available_money, is_land_battle, use_all_available_money)
    print("Attacking Armies:")
    for i, army in enumerate(attacker_possible_armies):
        print(str(i) + ": " + str(army))
    print("\nDefending Armies:")
    defender_possible_armies = get_possible_armies(defender_available_money, is_land_battle, use_all_available_money)
    for i, army in enumerate(defender_possible_armies):
        print(str(i) + ": " + str(army))

# todo analysis
