import loss_policies
from units import UnitTypes
from multiprocessing import cpu_count

# config
land_battle_units = (UnitTypes.LAND, UnitTypes.AIR)
sea_battle_units = (UnitTypes.SEA, UnitTypes.AIR)

attacker_loss_policy = loss_policies.least_power
defender_loss_policy = attacker_loss_policy

retreat_after_round = -1
retreat_when_x_units_left = -1
retreat_when_only_air_left = False
attacking_land_must_survive = True  # placeholder, not implemented yet
is_land_battle = True

low_luck = False

# recommended setting is True. False generates orders of magnitude more possible configurations
use_all_available_money = True

attacker_available_money = 75
defender_available_money = attacker_available_money
battle_simulation_count = 100


# number of processes to use for battle simulation
number_of_processes = None
if number_of_processes is None:
    number_of_processes = cpu_count()
