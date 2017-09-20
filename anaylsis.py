import pickle
from statistics import mean, median
import operator
from PIL import Image

from optimizer import get_folder_name, generate_and_save_all_battles
from army_generator import get_possible_armies
import config


list_of_stat_names = ("Percent Won", "Percent Draw", "Percent Lost",
                      "Percent Attacking Units Remaining", "Percent Attacking Units Remaining If Attacker Won",
                      "Percent Defending Units Remaining", "Percent Defending Units Remaining If Defender Won",
                      "Attacker \u0394TUV", "Defender \u0394TUV", "TUV Swing", "Rounds")


# loads results from a file
def load_results(attacker_money, defender_money, land_battle, version=None):
    # input reconciliation
    attacker_was_none = False
    if attacker_money is None:
        attacker_money = config.attacker_available_money
        attacker_was_none = True
    if defender_money is None:
        if attacker_was_none:
            defender_money = config.defender_available_money
        else:
            defender_money = attacker_money
    if land_battle is None:
        land_battle = config.is_land_battle

    folder_name = get_folder_name(attacker_money, defender_money, land_battle, version)
    try:
        with open(folder_name+"/full_results", 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        print("No Results Found. Generating Results Now")
        return generate_and_save_all_battles(attacker_money, defender_money, config.battle_simulation_count,
                                             land_battle, config.use_all_available_money)


# returns the index of and the contents of the army with the highest
# results property according to the method of aggregation
def find_best(attacker_money=None, defender_money=None, land_battle=None,
              results=None, attacker_armies=None, defender_armies=None,
              results_property=0, method_of_aggregation=mean):
    # input reconciliation
    if attacker_armies is not None:
        if defender_armies is None:
            defender_armies = attacker_armies

        if results is None:
            raise Exception("No results provided for analysis.")
        if (len(results) != len(attacker_armies)) or (len(results[0]) != len(defender_armies)):
            raise Exception("Provided results do not match provided arimes.")
    else:
        if attacker_money is None:
            attacker_money = config.attacker_available_money
        if defender_money is None:
            defender_money = config.defender_available_money
        if land_battle is None:
            land_battle = config.is_land_battle

        results = load_results(attacker_money, defender_money, land_battle)
        attacker_armies = get_possible_armies(attacker_money, land_battle)
        defender_armies = get_possible_armies(defender_money, land_battle)
    if not isinstance(results_property, int):
        results_property = list_of_stat_names.index(results_property)

    aggregated_results = [method_of_aggregation(battle_results[results_property] for battle_results in attacker_results)
                          for attacker_results in results]

    # find maximum using the aggregation method
    indices = []
    index, maximum = max(enumerate(aggregated_results), key=operator.itemgetter(1))
    army = attacker_armies[index]

    # find defending army that minimizes the property for the best attacking army
    defender_index, minimum = min(enumerate(battle_results[results_property] for battle_results in results[index]),
                                  key=operator.itemgetter(1))
    defender_army = defender_armies[defender_index]

    return maximum, index, army, minimum, defender_index, defender_army


# create a grayscale image showing the results for the specified property
def visualize(results, results_property_name, folder_name):
    results_property = list_of_stat_names.index(results_property_name)

    # extract relevant results_property
    filtered_results = [battle_results[results_property] for army_results in results for battle_results in army_results]

    bit_depth = 8
    max_brightness = (2**bit_depth)-1

    # scale results to 0-127 for grayscale interpretation
    # if delta tuv type result, scale to
    if results_property == 7:
        range_from_zero = max(abs(r) for r in filtered_results)
        filtered_results = [r*max_brightness/range_from_zero + (max_brightness+1)/2 for r in filtered_results]
    else:
        max_value = max(r for r in filtered_results)
        min_value = min(r for r in filtered_results)
        filtered_results = [(r-min_value)*max_brightness/(max_value-min_value) if max_value-min_value != 0 else 0
                            for r in filtered_results]

    pic = Image.new("L", (len(results), len(results[0])))
    pic.putdata(filtered_results)
    pic.save(folder_name+"/"+results_property_name+".png")


def do_all_stats(attacker_money=None, defender_money=None, land_battle=None,
                 results=None, attacker_armies=None, defender_armies=None):
    aggregation_methods = [mean, median]
    return [[method,
             [[stat,
               find_best(attacker_money=attacker_money, defender_money=defender_money, land_battle=land_battle,
                         results=results, attacker_armies=attacker_armies, defender_armies=defender_armies,
                         results_property=stat)]
              for stat in list_of_stat_names]]
            for method in aggregation_methods]


# generate and save images for all the stats at once
def do_all_visualisation(results, folder_name):
    for stat in list_of_stat_names:
        visualize(results, stat, folder_name)


# get and save all the stats in a human-readable file, and generate the images of the results
def do_and_save_all_analysis(attacker_money=None, defender_money=None, land_battle=None,
                             results=None, attacker_armies=None, defender_armies=None,
                             version=None):
    # input reconciliation
    if attacker_armies is not None:
        if defender_armies is None:
            defender_armies = attacker_armies

        if results is None:
            raise Exception("No results provided for analysis.")
        if len(results) != len(attacker_armies) or len(results[0]) != defender_armies:
            raise Exception("Provided results do not match provided armies.")
    else:
        if attacker_money is None:
            attacker_money = config.attacker_available_money
        if defender_money is None:
            defender_money = config.defender_available_money
        if land_battle is None:
            land_battle = config.is_land_battle

        results = load_results(attacker_money, defender_money, land_battle)
        attacker_armies = get_possible_armies(attacker_money, land_battle)
        defender_armies = get_possible_armies(defender_money, land_battle)

    folder_name = get_folder_name(attacker_money, defender_money, land_battle, version)

    attacker_armies = trim_armies(attacker_armies)
    defender_armies = trim_armies(defender_armies)

    do_all_visualisation(results, folder_name)
    stats = do_all_stats(attacker_armies=attacker_armies, defender_armies=defender_armies, results=results)
    with open(folder_name + "/summary.txt", 'w', encoding="utf-8") as f:
        for method in stats:
            f.write(method[0].__name__.title() + ": \n")
            for stat in method[1]:
                f.write("    " + stat[0].title() + ": \n")
                f.write("        Maximizing Attacker: " + str(stat[1][2]) + "\n")
                f.write("        Index:               " + str(stat[1][1]) + "\n")
                method_name = method[0].__name__.title()
                f.write("        " + method_name + " Score:" + (" "*(14-len(method_name))) + str(stat[1][0]) + "\n")
                f.write("        Min-max Defender:    " + str(stat[1][5]) + "\n")
                f.write("        Index:               " + str(stat[1][4]) + "\n")
                f.write("        " + method_name + " Score:" + (" "*(14-len(method_name))) + str(stat[1][3]) + "\n\n")

    # record army indices
    if attacker_armies == defender_armies:
        with open(folder_name + "/army_indices.txt", 'w', encoding="utf-8") as f:
            for i, army in enumerate(attacker_armies):
                f.write(str(i) + ": " + str(army)+"\n")
    else:
        with open(folder_name + "/attacker_army_indices.txt", 'w', encoding="utf-8") as f:
            for i, army in enumerate(attacker_armies):
                f.write(str(i) + ": " + str(army)+"\n")
        with open(folder_name + "/defender_army_indices.txt", 'w', encoding="utf-8") as f:
            for i, army in enumerate(defender_armies):
                f.write(str(i) + ": " + str(army)+"\n")


# remove entries for units whose count is zero from all army entries
def trim_armies(army_list):
    return [trim_army(army) for army in army_list]


# remove entries for units whose count is zero from an army
def trim_army(army):
    to_remove = [unit for unit, count in army.items() if count <= 0]
    for unit in to_remove:
        del army[unit]
    return army


if __name__ == "__main__":
    do_and_save_all_analysis(attacker_money=config.attacker_available_money,
                             defender_money=config.defender_available_money,
                             land_battle=config.is_land_battle,
                             version=None)
