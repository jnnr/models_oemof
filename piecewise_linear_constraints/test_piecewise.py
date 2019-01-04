from __future__ import division, print_function, unicode_literals

from pyomo.environ import ConcreteModel
from pyomo.environ import Constraint
from pyomo.environ import Objective
from pyomo.environ import Piecewise
from pyomo.environ import Var
from pyomo.environ import value
from pyomo.opt import SolverFactory
from pyomo.version import version
from subprocess import PIPE
from subprocess import check_output

def pw(x):
    return min(max(x, 0), 1)

def create_model(pw_repn, a):
    min_x, max_x = -10, 10
    m = ConcreteModel()
    m.c = Var()
    m.x = Var(bounds=(min_x, max_x))
    m.y = Var()
    m.pw = Piecewise(m.y, m.x, pw_repn=pw_repn, pw_constr_type='EQ', pw_pts=[min_x, 0, 1, max_x], f_rule=lambda m,x: pw(x))
    m.constr1 = Constraint(expr=m.x == a)
    m.constr2 = Constraint(expr=m.c == 23)
    m.o = Objective(expr=m.c)
    return m

def solve(solver_name, pw_repn, a):
    model = create_model(pw_repn, a)
    solver = SolverFactory(solver_name)
    results = solver.solve(model, keepfiles=False, tee=False)
    c = value(model.c)
    x = value(model.x)
    y = value(model.y)
    return c, x, y

def test_solver(solver_name, pw_repn):
    print('')
    print('solver={solver_name} pw_repn={pw_repn}'.format(**locals()))
    oks = []
    for i in range(-5, 15 + 1):
        a = i * 0.1
        c, x, y = solve(solver_name, pw_repn, a)
        expected_y = pw(a)
        ok = abs(expected_y - y) < 1e-3
        result = 'OK' if ok else 'FAIL'
        print('  c={c:>4.1f}  x={x:>5.2f}  expected_y={expected_y:>3.1f}  y={y:>6.4f} ... {result}'.format(**locals()))
        oks.append(ok)
    return all(oks)

def get_versions():
    return [
        ('cbc', check_output(['cbc', '-'], stdin=PIPE)),#.split('\n')[1].strip()),
        ('pyomo', version),
    ]

def main():
    solver_names = [
        'cbc'
    ]
    pw_repns = [
        'BIGM_BIN',
        'BIGM_SOS1',
        'CC',
        'DCC',
        'INC',
        'MC',
        'SOS2',
    ]
    unsupported_solver_repns = [
        ('cbc', 'BIGM_SOS1'),
        ('cbc', 'SOS2'),
        ('glpk', 'BIGM_SOS1'),
        ('glpk', 'SOS2'),
    ]
    summary = []
    print('Versions:')
    for name, version in get_versions():
        print('  {name:<5} = {version}'.format(**locals()))
    for solver_name in solver_names:
        for pw_repn in pw_repns:
            if (solver_name, pw_repn) not in unsupported_solver_repns:
                all_ok = test_solver(solver_name, pw_repn)
                summary.append((solver_name, pw_repn, all_ok))
    print('')
    print('Summary:')
    for solver_name, pw_repn, all_ok in summary:
        result = 'OK' if all_ok else 'FAIL'
        print('  solver_name={solver_name:<5}  pw_repn={pw_repn:<9} ... {result}'.format(**locals()))

if __name__ == '__main__':
    main()
