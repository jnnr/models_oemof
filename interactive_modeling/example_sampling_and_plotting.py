import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from oemof.solph import (Sink, Source, Transformer, Bus, Flow, Model,
                         EnergySystem, Investment, NonConvex)
import oemof.outputlib as outputlib
import oemof.solph as solph
import numpy as np
import holoviews as hv
hv.extension('bokeh')
import xarray as xr
import pyomo.environ as po
import time
import itertools as it
from collections import OrderedDict
solver = 'cbc'

color_dict ={
             'coal': '#755d5d',
             'gas': '#c76c56',
             'oil': '#494a19',
             'lignite': '#56201d',
             'wind': '#4ca7c3',
             'pv': '#ffde32',
             'excess_el': '#9a9da1',
             'pp_coal': '#755d5d',
             'pp_gas': '#c76c56',
             'pp_chp': '#eeac7e',
             'b_heat_source': '#cd3333',
             'heat_source': '#cd3333',
             'heat_pump': '#42c77a',
             'electricity': '#0079ff',
             'demand_el': '#0079ff',
             'shortage_el': '#ff2626',
             'excess_el': '#ff2626',
             'biomass': '#01b42e',
             'pp_biomass': '#01b42e'}

datetimeindex = pd.date_range('1/1/2016', periods=24*10, freq='H')
filename = 'input_data.csv'
data = pd.read_csv(filename, sep=",")

def run_basic_energysystem(args):
    n_val_wind = args[0]
    n_val_solar = args[1]
    start = time.time()
    # initialize and provide data
    energysystem = EnergySystem(timeindex=datetimeindex)

    # buses
    bcoal = Bus(label='coal', balanced=False)
    bgas = Bus(label='gas', balanced=False)
    bel = Bus(label='electricity')
    energysystem.add(bcoal, bgas, bel)

    # sources
    energysystem.add(Source(label='wind', outputs={bel: Flow(
        actual_value=data['wind'], nominal_value=n_val_wind, fixed=True)}))

    energysystem.add(Source(label='pv', outputs={bel: Flow(
        actual_value=data['pv'], nominal_value=n_val_solar, fixed=True)}))

    # excess and shortage to avoid infeasibilies
    energysystem.add(Sink(label='excess_el', inputs={bel: Flow()}))
    energysystem.add(Source(label='shortage_el',
                         outputs={bel: Flow(variable_costs=200)}))

    # demands (electricity/heat)
    energysystem.add(Sink(label='demand_el', inputs={bel: Flow(
        nominal_value=65, actual_value=data['demand_el'], fixed=True)}))

    # power plants
    energysystem.add(Transformer(
        label='pp_coal',
        inputs={bcoal: Flow()},
        outputs={bel: Flow(nominal_value=20.2, variable_costs=25)},
        conversion_factors={bel: 0.39}))

    energysystem.add(Transformer(
        label='pp_gas',
        inputs={bgas: Flow()},
        outputs={bel: Flow(nominal_value=41, variable_costs=40)},
        conversion_factors={bel: 0.50}))

    # create optimization model based on energy_system
    optimization_model = Model(energysystem=energysystem)

    # solve problem
    optimization_model.solve(solver=solver,
                             solve_kwargs={'tee': False, 'keepfiles': False})

    results = outputlib.processing.results(optimization_model)

    results_el = outputlib.views.node(results, 'electricity')
    el_sequences = results_el['sequences']
    el_prod = el_sequences[[(('wind', 'electricity'), 'flow'),
                            (('pv', 'electricity'), 'flow'),
                            (('pp_coal', 'electricity'), 'flow'),
                            (('pp_gas', 'electricity'), 'flow'),
                            (('shortage_el', 'electricity'), 'flow')]]
    
    inputs = outputlib.processing.convert_keys_to_strings(outputlib.processing.parameter_as_dict(optimization_model))
    nom_vals = [[key, value['scalars']['nominal_value']] for key, value in inputs.items() if 'nominal_value' in value['scalars']]
    nom_vals = pd.DataFrame(nom_vals, columns=['flow', 'nominal_value'])
    summed_flows = [(key, value['sequences'].sum()[0]) for key, value in outputlib.processing.convert_keys_to_strings(results).items()]
    summed_flows = pd.DataFrame(summed_flows, columns=['flow', 'summed_flows'])

    end = time.time()
    print('simulation lasted: ', end - start, 'sec')
    
    return el_prod


def generic_sampling(input_dict, results_dict, function):
    r"""
    n-dimensional full sampling, storing as xarray.
    
    Parameters
    ----------
    input_dict : OrderedDict
        Ordered dictionary containing the ranges of the
        dimensions.
    
    results_dict : OrderedDict
        Ordered dictionary containing the dimensions and 
        coordinates of the results of the function.
        
    function : function
        Function to be sampled.
    
    Returns
    -------
    results : xarray.DataArray
    
    sampling : np.array
    
    indices : 
    """
    import itertools as it
    join_dicts = OrderedDict(list(input_dict.items()) + list(results_dict.items()))
    dims = join_dicts.keys()
    coords = join_dicts.values()
    results = xr.DataArray(np.empty([len(v) for v in join_dicts.values()]),
                           dims=dims,
                           coords=coords)

    sampling = np.array(list(it.product(*input_dict.values())))
    indices = np.array(list(it.product(*[np.arange(len(v)) for v in input_dict.values()])))
    
    for i in range(len(sampling)):
        print(sampling[i])
        result = function(sampling[i])
        results[tuple(indices[i])] = result
        
    return results, sampling, indices


def xarray_to_interactive_dispatch_plot(results, tune, producer, time):
    """
    Creates a tunable dispatch plot from an xarray.
    
    Parameters
    ----------
    results : 
    
    tune_dims
    
    producer
    
    time

    Returns
    -------
    dispatch_hmap : HoloMap
    """    
    tune_coords = {k: results.coords[k].data for k in tune}
    tune_sample = it.product(*tune_coords.values())
    producer_coord = results.coords[producer]
    time_coord = results.coords[time]

    dispatch_hmap = hv.HoloMap({t: 
                        hv.Area.stack(
                            hv.Overlay([hv.Area(results.loc[dict(zip(tune_coords.keys(), t))].loc[{producer: s}]) 
                                        for s in producer_coord]
                                      ))
                                for t in tune_sample},
                                kdims=list(tune_coords.keys()))\
                        .options(width=500, height=200)
    
    ## https://github.com/ioam/holoviews/issues/1819
    renderer = hv.renderer('bokeh')

    # Using renderer save
    renderer.save(dispatch_hmap, 'example_sampling_and_plotting')
    

input_dict = {'n_vals_wind': [30, 50, 70],
              'n_vals_solar': [30, 50]}
results_dict = {'times': datetimeindex,
                'producer': [0,1,2,3,4]}
data_dispatch_2 = generic_sampling(input_dict, results_dict, run_basic_energysystem)[0]

tune = ['n_vals_wind', 'n_vals_solar']
producer = 'producer'
times = 'times'
xarray_to_interactive_dispatch_plot(data_dispatch_2, tune, producer, times)
