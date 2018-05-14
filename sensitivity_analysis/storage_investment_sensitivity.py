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
date_time_index = pd.date_range('1/1/2012', periods=24*7*8, freq='H')
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

    if wind_invest == True:
        solph.Source(label='wind', outputs={bel: solph.Flow(
            actual_value=data['wind'], fixed=True,
            investment=solph.Investment(ep_costs=params['epc_wind']))})
    else:
        solph.Source(label='wind', outputs={bel: solph.Flow(
            actual_value=data['wind'], nominal_value=params['wind_nom_val'], fixed=True)})

    if pv_invest == True:
        pv = solph.Source(label='pv', outputs={bel: solph.Flow(
            actual_value=data['pv'], fixed=True,
            investment=solph.Investment(ep_costs=params['epc_pv']))})
    else:
        solph.Source(label='pv', outputs={bel: solph.Flow(
           actual_value=data['pv'], nominal_value=params['pv_nom_val'], fixed=True)})

    solph.Sink(label='demand', inputs={bel: solph.Flow(
        actual_value=data['demand_el'], fixed=True, nominal_value=1)})

    solph.Transformer(
        label="pp_gas",
        inputs={bgas: solph.Flow()},
        outputs={bel: solph.Flow(nominal_value=10e10, variable_costs=50)},
        conversion_factors={bel: 0.58})


    storage = solph.components.GenericStorage(
        label='storage',
        inputs={bel: solph.Flow(variable_costs=10e10)},
        outputs={bel: solph.Flow(variable_costs=10e10)},
        capacity_loss=0.00, initial_capacity=0,
        nominal_input_capacity_ratio=1/6,
        nominal_output_capacity_ratio=1/6,
        inflow_conversion_factor=1, outflow_conversion_factor=0.8,
        investment=solph.Investment(ep_costs=params['epc_storage']),
    )

    logging.info('Optimise the energy system')

    om = solph.Model(energysystem)

    logging.info('Solve the optimization problem')
    om.solve(solver='cbc')

    string_results = processing.convert_keys_to_strings(processing.results(om))
    electricity_results = views.node(string_results, 'electricity')
    param_results = processing.convert_keys_to_strings(processing.param_results(energysystem))
    param_results_scalars = {key: value['scalars'] for (key,value) in param_results.items()}

    # save
    directory = 'results/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    electricity_results['sequences'].to_csv(directory+'el_seq.csv')
    electricity_results['scalars'].to_csv(directory+'el_scal.csv')

    results_filename = directory+'results_dict.pickle'
    pickle_out = open(results_filename, "wb")
    pickle.dump(param_results_scalars, pickle_out)
    pickle_out.close()

    # energysystem.results['main'] = processing.results(om)
    # energysystem.results['meta'] = processing.meta_results(om)
    # energysystem.results['params'] = params
    # energysystem.dump(dpath=os.path.dirname(os.path.abspath(__file__)), filename="varation_1")

run_model(params, wind_invest=True, pv_invest=True)
