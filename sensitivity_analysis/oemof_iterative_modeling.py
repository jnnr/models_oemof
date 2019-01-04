# -*- coding: utf-8 -*-

__copyright__ = "oemof developer group"
__license__ = "GPLv3"

import logging
import os
import pandas as pd

from oemof import solph
from oemof.outputlib import processing, views
from oemof.tools import logger
from oemof.tools import economics
from oemof.network import Node
import pickle

logger.define_logging()

# create timeindex and load timeseries data
date_time_index = pd.date_range('1/1/2012', periods=10, freq='H')
full_filename = os.path.join(os.path.dirname(__file__),
                             'storage_investment.csv')
data = pd.read_csv(full_filename, sep=",")

# set parameters
params = {'rgas_nom_val': 2000000,
          'wind_nom_val': 1000000,
          'pv_nom_val': 582000,
          'epc_storage': economics.annuity(capex=1000, n=20, wacc=0.05),
          'epc_wind': economics.annuity(capex=1000, n=20, wacc=0.05),
          'epc_pv': economics.annuity(capex=1000, n=20, wacc=0.05)}


def run_model(params, wind_invest=False, pv_invest=False, storage_invest=False):
    logging.info('Initialize the energy system')
    energysystem = solph.EnergySystem(timeindex=date_time_index)
    Node.registry = energysystem
    logging.info('Create oemof objects')
    bgas = solph.Bus(label="natural_gas")
    bel = solph.Bus(label="electricity")

    solph.Sink(label='excess_bel', inputs={bel: solph.Flow()})

    solph.Source(label='rgas', outputs={bgas: solph.Flow(nominal_value=params['rgas_nom_val'],
                                                         summed_max=1)})

    solph.Source(label='wind', outputs={bel: solph.Flow(
            actual_value=data['wind'], nominal_value=params['wind_nom_val'], fixed=True)})

    solph.Source(label='pv', outputs={bel: solph.Flow(
           actual_value=data['pv'], nominal_value=params['pv_nom_val'], fixed=True)})

    solph.Sink(label='demand', inputs={bel: solph.Flow(
        actual_value=data['demand_el'], fixed=True, nominal_value=1)})

    solph.Transformer(
        label="pp_gas",
        inputs={bgas: solph.Flow()},
        outputs={bel: solph.Flow(nominal_value=10e10, variable_costs=50)},
        conversion_factors={bel: 0.58})


    logging.info('Optimise the energy system')

    om = solph.Model(energysystem)

    logging.info('Solve the optimization problem')
    om.solve(solver='cbc')

    energysystem.results['main'] = processing.convert_keys_to_strings(processing.results(om))
    energysystem.results['param'] = processing.convert_keys_to_strings(processing.param_results(energysystem))


    return energysystem, om

energysystem, om =  run_model(params, wind_invest=True, pv_invest=True)

energysystem.entities
# electricity_results = views.node(string_results, 'electricity')
param_results = energysystem.results['param']
param_results_scalars = {key: value['scalars'] for (key,value) in param_results.items()}
print(param_results_scalars)
print('--------------------')
print(param_results_scalars[('pp_gas', 'electricity')]['nominal_value'])