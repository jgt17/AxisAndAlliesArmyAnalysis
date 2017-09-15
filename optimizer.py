import random

from units import Units, UnitTypes
from config import low_luck, retreat_after_round, retreat_when_x_units_left, retreat_when_only_air_left
from config import attacking_land_must_survive, attacker_loss_policy, defender_loss_policy
from config import is_land_battle, land_battle_units, sea_battle_units
import loss_policies


# get total unit value of an army
def get_tuv(army):
    return sum(unit.get_cost()*count for unit, count in army.items())


# battle emulation
def do_battle(attacking_army, defending_army):
    # roll a bunch of dice
    def roll_dice(num_to_roll):
        return [random.randint(1, 6)]

    # check hits
    def count_hits(die_results, power):
        return sum(1 for result in die_results if result < power)

    # get the total number of hits
    def get_total_hits(rolling_army, is_attacking):
        if is_attacking:
            power = Units.get_attack
        else:
            power = Units.get_defense



        if low_luck:
            army_power = sum(power(unit)*count for unit, count in rolling_army.items() if unit in Units)
            return army_power // 6 + count_hits(roll_dice(1), army_power % 6)
        else:
            return sum(count_hits(roll_dice(count), power(unit)) for unit, count in rolling_army.items if unit in Units)

    # apply losses
    def apply_losses(army, hits, is_attacking, loss_policy=loss_policies.default, keep_surviving_land=True):
        return loss_policy(army, hits, is_attacking, keep_surviving_land)

    # count the units an army has left
    def count_remaining_units(army):
        return sum(count for unit, count in army.items() if unit in Units)

    # check whether the attacking army should retreat based on the config
    def check_retreat():
        return 0 <= retreat_after_round <= round_of_combat or \
                0 <= retreat_when_x_units_left <= count_remaining_units(attacking_army) or\
               (retreat_when_only_air_left and 0 == sum(count for unit, count in attacking_army.items()
                                                        if unit in Units and unit.get_type is not UnitTypes.AIR))

    # work on copy of armies so battle can be re-run
    attacking_army = attacking_army.copy()
    defending_army = defending_army.copy()

    # record initial tuv of the armies
    attacking_army_tuv = get_tuv(attacking_army)
    defending_army_tuv = get_tuv(defending_army)

    # bombardment loss
    if low_luck:
        bombardment_power = sum(unit.get_attack()*count for unit, count in attacking_army.items()
                                if ((unit.get_type() not in land_battle_units and is_land_battle) or
                                (unit.get_type() not in sea_battle_units and not is_land_battle))
                                and unit.can_bombard())
        bombardment_loss = bombardment_power//6 + count_hits(roll_dice(1), bombardment_power%6)
    else:
        bombardment_loss = sum(count_hits(roll_dice(count), unit.get_attack()) for unit, count in attacking_army.items()
                               if ((unit.get_type() not in land_battle_units and is_land_battle) or
                               (unit.get_type() not in sea_battle_units and not is_land_battle))
                               and unit.can_bombard())
    bombardment_loss = [(land_battle_units if is_land_battle else sea_battle_units, bombardment_loss)]
    apply_losses(defending_army, bombardment_loss, False, defender_loss_policy)
    # remove bombardment units from army
    for unit in attacking_army.keys():
        if ((unit.get_type() not in land_battle_units and is_land_battle) or
                (unit.get_type() not in sea_battle_units and not is_land_battle)):
            del attacking_army[unit]
    for unit in defending_army.keys():
        if ((unit.get_type() not in land_battle_units and is_land_battle) or
                (unit.get_type() not in sea_battle_units and not is_land_battle)):
            del defending_army[unit]

    # anti-aircraft gun loss
    if aa_gun_present:
        aa_gun_fighter_hits = count_hits(roll_dice(attacking_army[Units.FIGHTER]), 1)
        aa_gun_bomber_hits = count_hits(roll_dice(attacking_army[Units.BOMBER]), 1)
        attacking_army[Units.FIGHTER] -= aa_gun_fighter_hits
        attacking_army[Units.BOMBER] -= aa_gun_bomber_hits

    # repeat rounds of combat until one side is done or the attacker retreats
    round_of_combat = 0
    while count_remaining_units(attacking_army) > 0\
            and count_remaining_units(defending_army > 0)\
            and not check_retreat():
        # first strike
        attacker_hits = get_total_first_strike_hits(attacking_army, True)
        defender_hits = get_total_first_strike_hits(defending_army, True)
        attacking_army = apply_losses(attacking_army, defender_hits,
                                      True, attacker_loss_policy, attacking_land_must_survive)
        defending_army = apply_losses(defending_army, attacker_hits,
                                      False, defender_loss_policy, attacking_land_must_survive)
        # normal combat
        attacker_hits = get_total_hits(attacking_army, True)
        defender_hits = get_total_hits(defending_army, False)
        attacking_army = apply_losses(attacking_army, defender_hits,
                                      True, attacker_loss_policy, attacking_land_must_survive)
        defending_army = apply_losses(defending_army, attacker_hits,
                                      False, defender_loss_policy, attacking_land_must_survive)
        round_of_combat += 1

    return (count_remaining_units(attacking_army) > 0,      # won
            count_remaining_units(attacking_army) == 0 and count_remaining_units(defending_army) == 0,    # draw
            count_remaining_units(defending_army),          # lost
            count_remaining_units(attacking_army),          # number attacking units remaining
            count_remaining_units(defending_army),          # number defending units remaining
            attacking_army_tuv - get_tuv(attacking_army),   # attacker delta tuv
            defending_army_tuv - get_tuv(defending_army),   # defender delta tuv
            attacking_army_tuv - get_tuv(attacking_army) - defending_army_tuv + get_tuv(defending_army),  # tuv swing
            round_of_combat + 1)                            # number of rounds of combat


# do a bunch of battles and aggregate results
def do_many_battles():
    raise NotImplementedError
    # todo

# todo all possible armies, analysis
# todo load or generate and save possible armies
