import itertools as it
import oemof.solph as solph
import os
from oemof import outputlib

# param_combs = list(it.product([1,2],[2,3]))
# print(param_combs)
#
# def dict_product(d):
#     keys = d.keys()
#     for element in product(*d.values()):
#         yield dict(zip(keys, element))
#
# params = {'rgas_nom_val': [1,2,3],
#           'wind_nom_val': [1],
#           'pv_nom_val': [2,3],
#           'epc': [5,7]}
#
# combs = dict_product(params)
# combs

energysystem = solph.EnergySystem()
energysystem.restore(dpath=os.path.dirname(os.path.abspath(__file__)), filename="varation_1")

# Getting results and views
results = outputlib.processing.convert_keys_to_strings(energysystem.results['main'])
print(results.keys())
print(results[(('storage', 'None'))]['scalars']['invest'])