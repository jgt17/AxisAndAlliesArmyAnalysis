import pickle
from statistics import mean, median
import operator
from PIL import Image

from optimizer import get_folder_name
from army_generator import get_possible_armies
import config


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
    with open(folder_name+"/full_results", 'rb') as f:
        return pickle.load(f)


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
        if len(results) != len(attacker_armies) or len(results[0]) != defender_armies:
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

    aggregated_results = [method_of_aggregation(battle_results[results_property] for battle_results in attacker_results)
                          for attacker_results in results]

    # find maximum using the aggregation method
    index, maximum = max(enumerate(aggregated_results), key=operator.itemgetter(1))
    army = attacker_armies[index]

    # find defending army that minimizes the property for the best attacking army
    defender_index, minimum = min(enumerate(battle_results[results_property] for battle_results in results[index]),
                                  key=operator.itemgetter(1))
    defender_army = defender_armies[defender_index]

    return maximum, index, army, minimum, defender_index, defender_army


# create a grayscale image showing the results for the specified property
def visualize(results, results_property):
    # extract relevant results_property
    filtered_results = [battle_results[results_property] for army_results in results for battle_results in army_results]

    bit_depth = 8
    max_brightness = (2**bit_depth)-1

    # scale results to 0-127 for grayscale interpretation
    # if delta tuv type result, scale to
    if 5 <= results_property <= 7:
        range_from_zero = max(abs(r) for r in filtered_results)
        filtered_results = [r*max_brightness/range_from_zero + (max_brightness+1)/2 for r in filtered_results]
    else:
        max_value = max(r for r in filtered_results)
        min_value = min(r for r in filtered_results)
        filtered_results = [(r-min_value)*max_brightness/(max_value-min_value) for r in filtered_results]

    return Image.new(filtered_results, (len(results), len(results[0])))


def do_all_stats():
    raise NotImplementedError
    # todo


def do_all_visualisation():
    raise NotImplementedError
    # todo


def do_and_save_all_analysis():
    raise NotImplementedError
    # todo
