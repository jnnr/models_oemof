# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import cProfile
import basic_example
import pstats

# example_path = 'basic_example/basic_example.py'
# full_path = '/home/jaan/Desktop/oemof_playground/oemof_examples/examples/oemof_0.2/'+example_path
# cProfile.run('basic_example.py', 'results/profile_file')

# cProfile.run('basic_example.main()', 'results/stats.profile')


p = pstats.Stats('results/stats.profile')
#p.strip_dirs().sort_stats(-1).print_stats()

p.sort_stats('cumulative').print_stats(10)
