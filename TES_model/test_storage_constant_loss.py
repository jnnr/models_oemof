import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from oemof.solph import (Source, Sink, Transformer, Bus, Flow,
                         Model, EnergySystem)
from oemof.solph.components import GenericStorage
import oemof.outputlib as outputlib

solver = 'cbc'

# set timeindex and create data
periods = 20
datetimeindex = pd.date_range('1/1/2019', periods=periods, freq='H')
x = np.arange(periods)
demand = np.zeros(20)
demand[-3:] = 2
wind = np.zeros(20)
wind[:3] = 3

# set up EnergySystem
energysystem = EnergySystem(timeindex=datetimeindex)

b_el = Bus(label='electricity')

wind = Source(label='wind', outputs={b_el: Flow(nominal_value=1,
                                                actual_value=wind,
                                                fixed=True)})

shortage = Source(label='shortage', outputs={b_el: Flow(variable_costs=1e6)})

excess = Sink(label='excess', inputs={b_el: Flow()})

demand = Sink(label='demand', inputs={b_el: Flow(nominal_value=1,
                                                 actual_value=demand,
                                                 fixed=True)})
storage = GenericStorage()

storage = GenericStorage(label='storage',
                         inputs={b_el: Flow(variable_costs=0.0001)},
                         outputs={b_el: Flow()},
                         nominal_storage_capacity=15,
                         initial_storage_level=0.75,
                         #min_storage_level=0.4,
                         #max_storage_level=0.9,
                         loss_rate=0.1,
                         loss_constant=0.,
                         inflow_conversion_factor=1.,
                         outflow_conversion_factor=1.)

energysystem.add(b_el, wind, shortage, excess, demand, storage)

# create and solve the optimization model
optimization_model = Model(energysystem)
optimization_model.write('/home/jann/Desktop/storage_model.lp', io_options={'symbolic_solver_labels': True})
optimization_model.solve(solver=solver,
                         solve_kwargs={'tee': False, 'keepfiles': False})
# get results
results = outputlib.processing.results(optimization_model)
string_results = outputlib.processing.convert_keys_to_strings(results)
sequences = {k:v['sequences'] for k, v in string_results.items()}
df = pd.concat(sequences, axis=1)

# print and plot results
df = df.reset_index()
print(df)

fig, (ax1, ax2) = plt.subplots(2, 1)
df[[('shortage', 'electricity', 'flow'),
    ('wind', 'electricity', 'flow'),
    ('storage', 'electricity', 'flow')]].plot.bar(ax=ax1, stacked=True, color=['y', 'b', 'k'])
(-df[('electricity', 'storage', 'flow')]).plot.bar(ax=ax1, color='g')
df[('electricity', 'demand', 'flow')].plot(ax=ax1, linestyle='', marker='o', color='r')
ax1.set_ylim(-5, 5)
ax1.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
df[('storage', 'None', 'capacity')].plot.bar(ax=ax2)
ax2.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
plt.tight_layout()
plt.show()