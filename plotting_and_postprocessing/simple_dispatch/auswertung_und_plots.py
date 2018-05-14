import oemof.solph as solph
import oemof.outputlib as outputlib
import pickle
import os
import pandas as pd

# one way: load an energysystem
energysystem = solph.EnergySystem()
energysystem.restore(dpath=None, filename=None)

# print some results
print(energysystem.results['meta'])
string_results = outputlib.views.convert_keys_to_strings(energysystem.results['main'])
print(string_results.keys())

node_results_bel = outputlib.views.node(energysystem.results['main'], 'bel')
node_results_flows = node_results_bel['sequences']




# the alternative way: load a dictionary you have saved before
# load results dictionary:
results_filename = os.path.dirname(os.path.abspath(__file__))+"/results_dict.pickle"
results_dict = pickle.load(open(results_filename,'rb'))

# print keys and number of keys
# print(results_dict.keys())
print(len(results_dict.keys()))

# collect results by keys in variables and goto matplotlib
# consumption_oil
# consumption_coal
# consumption_gas
# consumption_lignite
# consumption_el_hp