from fuzzywuzzy import process, fuzz

global config

_all_cities = list()
_syn_list = list()

_syn_inverted_dict = dict()


def init(cities_list, synonyms_dict):
    global _syn_list, _all_cities, _syn_inverted_dict

    _syn_list = _synonyms_list(synonyms_dict)
    _syn_inverted_dict = _synonyms_inverted_dict(synonyms_dict)
    _all_cities = cities_list


def _synonyms_list(synonyms_dict):
    s_list = list()
    for city, syn_list in synonyms_dict.items():
        for syn in syn_list:
            s_list.append(syn)

    return s_list


def _synonyms_inverted_dict(synonyms_dict):
    syn_inv_dict = dict()

    for city, syn_list in synonyms_dict.items():
        for syn in syn_list:
            syn_inv_dict[syn] = city
    return syn_inv_dict


def detect_city(message, threshold, all_cities: list = None, synonyms_list: list = None, syn_inverted_dict: dict = None):
    """
    returns tuple of ("city from all_cities", <tolerance score from 0 to threshold as int>)
    or None if score less than threshold.

    if  all_cities, synonyms_list or syn_inverted_dict not provided  - they are taken from module level vars
    """

    all_cities = all_cities or _all_cities
    synonyms_list = synonyms_list or _syn_list
    syn_inverted_dict = syn_inverted_dict or _syn_inverted_dict

    # step 1: check synonyms first
    # cities_from_synonyms = process.extractBests(message, synonyms_list, limit=3, score_cutoff=threshold)

    # if len(cities_from_synonyms) == 0:
    #     cities_from_synonyms.append(("", 0))

    # if cities_from_synonyms[0][1] == 100:
    #     if cities_from_synonyms[0][0] in syn_inverted_dict:
    #         return syn_inverted_dict[cities_from_synonyms[0][0]], cities_from_synonyms[0][1]

    # step 2: check all cities
    cities_from_all = process.extractBests(message, all_cities, limit=3, scorer=fuzz.UWRatio, score_cutoff=threshold)

    if len(cities_from_all) == 0:
        cities_from_all.append(("", 0))

    if cities_from_all[0][1] == 100:
        return cities_from_all[0]

    return cities_from_all[0]

    if 0 < cities_from_all[0][1] >= cities_from_synonyms[0][1]:
        return cities_from_all[0]

    elif 0 < cities_from_synonyms[0][1] and cities_from_synonyms[0][0] in syn_inverted_dict:
        return syn_inverted_dict[cities_from_synonyms[0][0]], cities_from_synonyms[0][1]

    return None
