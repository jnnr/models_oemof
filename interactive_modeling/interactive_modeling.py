import numpy as np
import holoviews as hv

# Farben, plotgröße, richtiges datenformat für bars

# %%opts Bars [height=200 width=300]
# %%opts Area [height=200 width=600]



def create_interactive_plot(data_dispatch, data_bars):
    """

    """
    dispatch_hmap = hv.HoloMap({(i, k): hv.Area.stack(hv.Overlay([hv.Area(data_dispatch[k, i, :, j]) for j in range(n_stack)]))
                       for i in range(n_i) for k in range(n_k)}, kdims=['price pv', 'price wind'])

    bar_hmap = hv.HoloMap({(i, k): hv.Bars(data_bars, hv.Dimension('Technology'), 'Installed capacity')
                       for i in range(n_i) for k in range(n_k)}, kdims=['price pv', 'price wind'])

    layout = hv.Layout(dispatch_hmap + bar_hmap).cols(1)

    ## https://github.com/ioam/holoviews/issues/1819
    renderer = hv.renderer('bokeh')

    # Using renderer save
    renderer.save(dispatch_hmap + bar_hmap, 'interactive_modeling')

n_i = 5
n_k = 5
n_stack = 5
t = 20

values = np.random.rand(n_stack, t, n_i, n_k)
data_dispatch = (values/values.sum(axis=0)).T*100
data_bars = [('one',8),('two', 10), ('three', 16), ('four', 8), ('five', 4), ('six', 1)]

create_interactive_plot(data_dispatch, data_bars)
