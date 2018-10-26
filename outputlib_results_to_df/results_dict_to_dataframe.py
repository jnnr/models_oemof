from oemof import solph
from oemof import outputlib
import pandas as pd
import os

energysystem = solph.EnergySystem()
energysystem.restore(dpath=os.path.dirname(os.path.abspath(__file__)), filename="energysystem.dump")

# Getting results and views
results = outputlib.processing.convert_keys_to_strings(energysystem.results)
print(results.keys())

string_results = outputlib.processing.convert_keys_to_strings(results)

all_sequences = [value['sequences'].rename(columns={'flow': str(key)}) for (key, value) in string_results.items()]
all_sequences = pd.concat(all_sequences, axis=1).head()
print(all_sequences)
all_sequences.to_csv('all_sequences.csv')

all_scalars = [value['scalars'] for (key, value) in string_results.items()]
print(all_scalars)
all_scalars.to_csv('all_scalars.csv')

# data = xr.DataArray([(key, value['sequences'].head(2)) for (key, value) in string_results.items()])
# data
#
# data = xr.DataArray(string_results[('pp_lig', 'bel')]['sequences'])
# data
