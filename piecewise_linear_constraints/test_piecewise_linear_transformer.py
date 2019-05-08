import pandas as pd
from oemof.solph import (Sink, Transformer, Bus, Flow, Model,
                         EnergySystem)
import oemof.outputlib as outputlib
import oemof.solph as solph
import numpy as np

solver = 'cbc'

# set timeindex and create data
periods = 24
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

energysystem.add(Transformer(
    label='pp_gas',
    inputs={b_gas: Flow()},
    outputs={b_el: Flow(nominal_value=100, variable_costs=40)},
    conversion_factors={b_el: 0.50}))

# create and solve the optimization model
optimization_model = Model(energysystem)
optimization_model.solve(solver=solver,
                         solve_kwargs={'tee': False, 'keepfiles': False})

results = outputlib.processing.results(optimization_model)
string_results = outputlib.processing.convert_keys_to_strings(results)
sequences = {k:v['sequences']['flow'] for k, v in string_results.items()}
df = pd.DataFrame(sequences)
df[('efficiency',None)] = df[('pp_gas', 'electricity')].divide(df[('gas', 'pp_gas')])
print(df)