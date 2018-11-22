# https://pyomo.readthedocs.io/en/latest/library_reference/kernel/piecewise/piecewise.html


#  ___________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright 2017 National Technology and Engineering Solutions of Sandia, LLC
#  Under the terms of Contract DE-NA0003525 with National Technology and
#  Engineering Solutions of Sandia, LLC, the U.S. Government retains certain
#  rights in this software.https://github.com/Pyomo/pyomo.git
#  This software is distributed under the 3-clause BSD License.
#  ___________________________________________________________________________

# A simple example illustrating a piecewise
# representation of the function Z(X)
#
#          / -X+2 , -5 <= X <= 1
#  Z(X) >= |
#          \  X ,  1 <= X <= 5
#

from pyomo.core import *

# Define the function
# Just like in Pyomo constraint rules, a Pyomo model object
# must be the first argument for the function rule
def f(model,x):
    return abs(x-1)+1.0

model = ConcreteModel()

model.X = Var(bounds=(-5,5))
model.Z = Var()

# See documentation on Piecewise component by typing
# help(Piecewise) in a python terminal after importing pyomo.core
model.con = Piecewise(model.Z,model.X, # range and domain variables
                      pw_pts=[-5,1,5] ,
                      pw_constr_type='LB',
                      f_rule=f)

# The default piecewise representation implemented by Piecewise is SOS2.
# Note, however, that no SOS2 variables will be generated since the
# check for convexity within Piecewise automatically simplifies the constraints
# when a lower bounding convex function is supplied. Adding 'force_pw=True'
# to the Piecewise argument list will cause the original piecewise constraints
# to be used even when simplifications can be applied.
model.obj = Objective(expr=model.Z, sense=minimize)


import oemof.solph as solph
import oemof.outputlib as outputlib
import pandas as pd
import pyomo.environ as po
import matplotlib.pyplot as plt

data = pd.read_csv('input_data.csv')
date_time_index = pd.date_range('1/1/2012', periods=24, freq='H')
es = solph.EnergySystem(timeindex=date_time_index)

bgas = solph.Bus(label="natural_gas", balanced=False)
bheat = solph.Bus(label='heat')

es.add(bgas, bheat)

es.add(solph.Sink(label='demand_th',
                 inputs={bheat: solph.Flow(nominal_value=40,
                                     actual_value=data['demand_th'],
                                     fixed=True)}))

es.add(solph.Transformer(label='gas_boiler',
                           inputs={bgas: solph.Flow(variable_costs=35)},
                           outputs={bheat: solph.Flow(
                               nominal_value=100,
                               variable_costs=0)},
                        conversion_factors={bheat: 0.8}))

om = solph.Model(es)

# ----------------------------------------------------------

for s, t in om.flows.keys():
    if s is bgas:
        om.flows[s, t].emission_factor = 0.27  # t/MWh

emission_limit = 6e3
myblock = po.Block()
myblock.MYFLOWS = po.Set(initialize=[k for (k, v) in om.flows.items()
                                     if hasattr(v, 'outflow_share')])
om.add_component('MyBlock', myblock)

def _inflow_share_rule(m, s, e, t):
    """pyomo rule definition: Here we can use all objects from the block or
    the om object, in this case we don't need anything from the block
    except the newly defined set MYFLOWS.
    """
    expr = (om.flow[s, e, t] >= om.flows[s, e].outflow_share[t] *
            sum(om.flow[i, o, t] for (i, o) in om.FLOWS if o == e))
    return expr

myblock.inflow_share = po.Constraint(myblock.MYFLOWS, om.TIMESTEPS,
                                     rule=_inflow_share_rule)


# om.X = Var(bounds=(-5,5))
# om.Z = Var()
# om.con = Piecewise(om.Z,om.X, # range and domain variables
#                       pw_pts=[-5,1,5] ,
#                       pw_constr_type='LB',
#                       f_rule=f)

# ----------------------------------------------------------


om.solve()

results = outputlib.processing.results(om)
string_results = outputlib.processing.convert_keys_to_strings(results)
all_sequences = [value['sequences'].rename(columns={'flow': key}) for (key, value) in string_results.items()]
all_sequences = pd.concat(all_sequences, axis=1)
tuples = [key for (key, value) in string_results.items()]
multi_index = pd.MultiIndex.from_tuples(tuples, names=['from', 'to'])
all_sequences.columns = multi_index
print(all_sequences.head())
all_sequences.plot()
plt.show()