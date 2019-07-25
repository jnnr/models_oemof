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

def calculate_storage_u_value(s_iso, lamb_iso, alpha_inside, alpha_outside):
    r"""
    Calculates the thermal transmittance (U-value) of a thermal storage.

    Parameters
    ----------
    s_iso : numeric
    lamb_iso : numeric
    alpha_inside : numeric
    alpha_outside : numeric

    Returns
    ------
    u_value : numeric
    """
    denominator = 1 / alpha_inside + s_iso / lamb_iso + 1 / alpha_outside
    u_value = 1 / denominator
    return u_value

def calculate_capacities(height, diameter, heat_capacity, density,
                         temp_h, temp_c, nonusable_storage_volume):
    r"""
    Calculates the capacity, surface area, minimum and maximum storage level
    of a stratified thermal storage

    Parameters
    ----------
    height : numeric
    diameter : numeric
    heat_capacity: numeric
    density : numeric
    temp_h : numeric
    temp_c : numeric
    nonusable_storage_volume : numeric

    Returns
    -------
    Q_N : numeric
    surface : numeric
    Q_max : numeric
    Q_min : numeric
    """
    Q_N = diameter**2 * 1/4 * np.pi * height * heat_capacity * density *(temp_h - temp_c)
    Q_max = Q_N * (1 - nonusable_storage_volume/2)
    Q_min = Q_N * nonusable_storage_volume/2
    surface = np.pi * diameter * height + 2 * np.pi * diameter**2 *1/4
    return Q_N, surface, Q_max, Q_min

def calculate_losses(u_value, surface, temp_h, temp_c):
    r"""
    Calculates loss rate and constant losses for a stratified thermal storage.

    Parameters
    ----------
    u_value : numeric
    surface : numeric
    temp_h : numeric
    temp_c : numeric

    Returns
    -------
    loss_rate : numeric
    loss_constant : numeric
    """
    loss_rate = u_value * surface * (temp_h - temp_c)
    loss_constant = u_value * surface * (temp_c - temp_env)
    return loss_rate, loss_constant

height = 10 # [m]
diameter = 4 # [m]
density = 1 # [kg/m3]
heat_capacity = 3 # [J/kgK]
temp_h = 95 # [°C]
temp_c = 60 # [°C]
temp_env = 10 # [°C]
inflow_conversion_factor = 0.9
outflow_conversion_factor = 0.9
nonusable_storage_volume = 0.2
s_iso = 1
lamb_iso = 1
alpha_inside = 1
alpha_outside = 1

u_value = calculate_storage_u_value(s_iso, lamb_iso, alpha_inside, alpha_outside)

Q_N, surface, Q_max, Q_min = calculate_capacities(height, diameter, heat_capacity, density,
                                                  temp_h, temp_c, nonusable_storage_volume)

loss_rate, loss_constant = calculate_losses(u_value, surface, temp_h, temp_c)

# storage = GenericStorage(label='storage',
#                          inputs={b_el: Flow(variable_costs=0.0001)},
#                          outputs={b_el: Flow()},
#                          nominal_storage_capacity=15,
#                          initial_storage_level=0.75,
#                          #min_storage_level=Q_min,
#                          #max_storage_level=Q_max,
#                          loss_rate=0.1,
#                          loss_constant=0.,
#                          inflow_conversion_factor=1.,
#                          outflow_conversion_factor=1.)

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