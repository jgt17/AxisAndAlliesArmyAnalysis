from units import Units


def least_power(unit_list, hits, is_attacking, keep_surviving_land):
    keep_surviving_land += 1  # just to keep the inspector quiet
    # todo respect surviving land setting
    # do unit-specific damage first
    to_remove = []
    for hit_type in hits:
        if hit_type in Units:
            unit_list[hit_type] -= hits[hit_type]
            to_remove.append(hit_type)
    for hit_type in to_remove:
        del hits[hit_type]

    # now units with multiple hit points
    to_remove = []
    for hit_type in hits:
        if hit_type not in Units:
            num_hits = hits[hit_type]
            units = [unit for unit in unit_list
                     if unit in Units and
                     unit_list[unit] > 0 and
                     (unit.get_type() in hit_type or unit in hit_type) and
                     unit.get_hit_points() > 1]
            # order that free hits are taken doesn't matter (would if making an AI and had units with > 2 hits)
            for unit in units:
                to_apply = min(num_hits, unit.get_hit_points()-1 * unit_list[unit])
                number_units_to_min_health = to_apply//(unit.get_hit_points()-1)
                unit_list[unit] -= number_units_to_min_health
                critical_unit = unit.get_damaged_unit(unit.get_hit_points()-1)
                unit_list[critical_unit] = number_units_to_min_health
                if to_apply % (unit.get_hit_points()-1) != 0:
                    damaged_unit = unit.get_damaged_unit(to_apply % unit.get_hit_points()-1)
                    unit_list[damaged_unit] = 1
                    unit_list[unit] -= 1
                num_hits -= to_apply
                if num_hits == 0:
                    break
            if num_hits == 0:
                to_remove.append(hit_type)
    for hit_type in to_remove:
        del hits[hit_type]

    # now general damage
    for hit_type in hits:
        if hit_type not in Units:
            # types to units
            units = [unit for unit in unit_list
                     if unit in Units and
                     (unit.get_type() in hit_type or unit in hit_type) and
                     unit.get_hit_points() > 0]
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
