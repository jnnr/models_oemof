from oemof.tools import economics
import itertools as it
import numpy as np

epc_storage = economics.annuity(capex=1000, n=20, wacc=0.05)
epc_wind = economics.annuity(capex=1000, n=20, wacc=0.05)
epc_pv = economics.annuity(capex=1000, n=20, wacc=0.05)

params = {'rgas_nom_val': 2000000,
          'wind_nom_val': 1000000,
          'pv_nom_val': 582000,
          'epc_storage': epc_storage,
          'epc_wind': epc_wind,
          'epc_pv': epc_pv}

param_min_max = {'rgas_nom_val': [1000000, 2000000],
                 'wind_nom_val': [1000000, 1200000],
                 'pv_nom_val': [582000, 6002000],
                 'epc_storage': epc_storage,
                 'epc_wind': epc_wind,
                 'epc_pv': epc_pv}


def get_range(dictio, steps):
    for (key, value) in dictio.items():
        print(value)
    value = dictio['rgas_nom_val']
    liste = [1, 10]
    range = np.arange(liste[0], liste[1], abs(liste[0] - liste[1])/steps)

    return range


print(get_range(param_min_max, 3))


rgas_nom_val = [1.1, 2, 3, 4]
wind_nom_val = [1, 3, 5, 7, 9]
pv_nom_val = [0, 1]
epc_storage = [42]
epc_wind = [1]
epc_pv = [1]

print('---')
print([(key,value) for (key, value) in param_min_max.items()])

# para_combs = list(it.product(pa, ra, me, ters))
# print('here', para_combs[2])

# initialize structure of the model
# set values for parameters
# run, get results, store them
# iterate model experiments according to parameter lists
