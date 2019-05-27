import pandas as pd
from oemof.solph import (Sink, Transformer, Bus, Flow, Model,
                         EnergySystem)
import oemof.outputlib as outputlib
import oemof.solph as solph
import numpy as np
import matplotlib.pyplot as plt

solver = 'cbc'

# set timeindex and create data
periods = 10
datetimeindex = pd.date_range('1/1/2019', periods=periods, freq='H')
x = np.arange(0, periods, 1)
demand = 50 * np.sin(x) + 50

# set up EnergySystem
energysystem = EnergySystem(timeindex=datetimeindex)
b_gas = Bus(label='gas', balanced=False)
b_el = Bus(label='electricity')
energysystem.add(b_gas, b_el)
energysystem.add(Sink(label='demand', inputs={b_el: Flow(
    nominal_value=1, actual_value=demand, fixed=True)}))

conv_func = lambda x: 0.01 * x**2
pwltf = solph.custom.PiecewiseLinearTransformer(
    label='pwltf',
    inputs={b_gas: solph.Flow(
    nominal_value=220,
    variable_costs=1)},
    outputs={b_el: solph.Flow()},
    in_breakpoints=[0, 0.25, 0.5, 0.75, 1],
    out_breakpoints=[0, 0.05, 0.15, 0.25, 0.4],
    conversion_function=conv_func,
    pw_repn='CC')

energysystem.add(pwltf)

# create and solve the optimization model
optimization_model = Model(energysystem)
optimization_model.write('/home/jann/Desktop/my_model.lp', io_options={'symbolic_solver_labels': True})
optimization_model.solve(solver=solver,
                         solve_kwargs={'tee': False, 'keepfiles': False})

results = outputlib.processing.results(optimization_model)
string_results = outputlib.processing.convert_keys_to_strings(results)
sequences = {k:v['sequences'] for k, v in string_results.items()}
df = pd.concat(sequences, axis=1)
df[('efficiency', None, None)] = df[('pwltf', 'electricity')].divide(df[('gas', 'pwltf')])
print(df)

fig, ax = plt.subplots()
ax.scatter(df[('gas', 'pwltf')], df[('pwltf', 'electricity')], marker='.', c='r')
x = np.arange(0,120,10)
y = conv_func(x)
ax.plot(x, y)
ax.set_ylabel('electricity output')
ax.set_xlabel('gas input')
plt.show()