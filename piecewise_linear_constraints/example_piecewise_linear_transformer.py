import pandas as pd
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt

from oemof.solph import (Sink, Source, Transformer, Bus, Flow, Model,
                         EnergySystem, Investment, NonConvex)
import oemof.outputlib as outputlib
import oemof.solph as solph
import oemof.graph as graph
from oemof.tools import economics

import pyomo.environ as po
import numpy as np

solver = 'cbc'

def initialize_basic_energysystem():
    # initialize and provide data
    datetimeindex = pd.date_range('1/1/2016', periods=24, freq='H')
    filename = 'input_data.csv'
    data = pd.read_csv(filename, sep=",")
    energysystem = EnergySystem(timeindex=datetimeindex)

    # buses
    bcoal = Bus(label='coal', balanced=False)
    bgas = Bus(label='gas', balanced=False)
    bel = Bus(label='electricity')
    energysystem.add(bcoal, bgas, bel)

    # sources
    energysystem.add(Source(label='wind', outputs={bel: Flow(
        actual_value=data['wind'], nominal_value=66.3, fixed=True)}))

    energysystem.add(Source(label='pv', outputs={bel: Flow(
        actual_value=data['pv'], nominal_value=65.3, fixed=True)}))

    # excess and shortage to avoid infeasibilies
    energysystem.add(Sink(label='excess_el', inputs={bel: Flow()}))
    energysystem.add(Source(label='shortage_el',
                            outputs={bel: Flow(variable_costs=200)}))

    # demands (electricity/heat)
    energysystem.add(Sink(label='demand_el', inputs={bel: Flow(
        nominal_value=85, actual_value=data['demand_el'], fixed=True)}))

    return bcoal, bgas, bel, energysystem

bcoal, bgas, bel, energysystem = initialize_basic_energysystem()

# power plants
energysystem.add(solph.Transformer(
    label='pp_coal',
    inputs={bcoal: Flow()},
    outputs={bel: Flow(nominal_value=20.2, variable_costs=25)},
    conversion_factors={bel: 0.5}))

energysystem.add(Transformer(
    label='pp_gas',
    inputs={bgas: Flow()},
    outputs={bel: Flow(nominal_value=41, variable_costs=40)},
    conversion_factors={bel: 0.50}))

energysystem.add(solph.custom.OffsetTransformer(
    label='ostf',
    inputs={bgas: solph.Flow(
    nominal_value=60, min=0.5, max=1.0,
    nonconvex=solph.NonConvex())},
    outputs={bel: solph.Flow()},
    coefficients={(bgas, bel): [20, 0.5]}))

# create the model
optimization_model = Model(energysystem)

# solve problem
optimization_model.solve(solver=solver,
                         solve_kwargs={'tee': False, 'keepfiles': False})

meta_results = outputlib.processing.meta_results(optimization_model)
print(meta_results)