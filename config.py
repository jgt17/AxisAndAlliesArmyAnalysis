import loss_policies
from units import UnitTypes

# config
land_battle_units = (UnitTypes.LAND, UnitTypes.AIR)
sea_battle_units = (UnitTypes.SEA, UnitTypes.AIR)

attacker_loss_policy = loss_policies.least_power
defender_loss_policy = attacker_loss_policy

retreat_after_round = -1
retreat_when_x_units_left = -1
retreat_when_only_air_left = False
attacking_land_must_survive = True
is_land_battle = True

low_luck = True

use_all_available_money = True

# low values for debugging
attacker_available_money = 10
defender_available_money = attacker_available_money
battle_simulation_count = 500
