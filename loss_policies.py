from units import Units, UnitTypes


def least_power(unit_list, hits, is_attacking, keep_surviving_land):
    # do unit-specific damage first
    for hit_type in hits:
        if hit_type in Units:
            unit_list[hit_type] -= hits[hit_type]

    # now more general damage
    for hit_type in hits:
        if hit_type not in Units:
            # types to units
            units = [unit for unit in unit_list if unit in Units and (unit.get_type() in hit_type or unit in hit_type)]
            units = sorted(units, key=Units.get_attack if is_attacking else Units.get_defense)
            hit_count = hits[hit_type]
            for unit in units:
                if unit in Units:
                    hits_dealt_to_unit = min(hit_count, unit_list[unit])
                    unit_list[unit] -= hits_dealt_to_unit
                    hit_count -= hits_dealt_to_unit
                    if hit_count == 0:
                        break
    return unit_list


default = least_power


# todo support for multiple hit points
