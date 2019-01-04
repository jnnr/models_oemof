from __future__ import division
from pyomo.environ import *
from pyomo import opt

# create the model
model = ConcreteModel()
model.x = Var()
model.p = Param(mutable=True) # allows the parameter value to be updated
model.o = Objective(expr= model.x)
model.c = Constraint(expr= model.x >= model.p)

# create a solver
solver = opt.SolverFactory('cbc')

# set the initial parameter value
model.p.value = 2.0

model.pprint()

# solve the model (the solution is loaded automatically)
results = solver.solve(model)

# print the solver termination condition
print(results.solver.termination_condition)

# update the parameter value
model.p.value = 3.0

model.pprint()

# solve the model again
results = solver.solve(model)

# print the solver termination condition
print(results.solver.termination_condition)