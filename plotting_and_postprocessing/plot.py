import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc

from oemof import solph
from oemof.outputlib import views, processing
import oemof_visio as oev

def shape_legend(node, reverse=False, **kwargs):
    handels = kwargs['handles']
    labels = kwargs['labels']
    axes = kwargs['ax']
    parameter = {}

    new_labels = []
    for label in labels:
        label = label.replace('(', '')
        label = label.replace('), flow)', '')
        label = label.replace(node, '')
        label = label.replace(',', '')
        label = label.replace(' ', '')
        new_labels.append(label)
    labels = new_labels

    parameter['bbox_to_anchor'] = kwargs.get('bbox_to_anchor', (1, 0.5))
    parameter['loc'] = kwargs.get('loc', 'center left')
    parameter['ncol'] = kwargs.get('ncol', 1)
    plotshare = kwargs.get('plotshare', 0.9)

    if reverse:
        handels = handels.reverse()
        labels = labels.reverse()

    box = axes.get_position()
    axes.set_position([box.x0, box.y0, box.width * plotshare, box.height])

    parameter['handles'] = handels
    parameter['labels'] = labels
    axes.legend(**parameter)
    return axes


energysystem = solph.EnergySystem()
energysystem.restore(dpath=os.path.dirname(os.path.abspath(__file__)), filename="varation_1")

# Getting results and views
results = energysystem.results['main']
params  =energysystem.results['params']
custom_storage = views.node(results, 'storage')
electricity_bus = views.node(results, 'electricity')

# ***** 2. example ***************************************************
cdict = {
    (('electricity', 'demand'), 'flow'): '#ce4aff',
    (('electricity', 'excess_bel'), 'flow'): '#555555',
    (('electricity', 'storage'), 'flow'): '#42c77a',
    (('pp_gas', 'electricity'), 'flow'): '#636f6b',
    (('pv', 'electricity'), 'flow'): '#ffde32',
    (('storage', 'electricity'), 'flow'): '#42c77a',
    (('wind', 'electricity'), 'flow'): '#5b5bae'}

# ***** 4. example ***************************************************
# Create a plot to show the balance around a bus.
# Order and colors are customisable.

inorder = [(('pv', 'electricity'), 'flow'),
           (('wind', 'electricity'), 'flow'),
           (('storage', 'electricity'), 'flow'),
           (('pp_gas', 'electricity'), 'flow')]

rc('font',**{'family':'sans-serif','sans-serif':['DejaVu Sans'],'size':20})
fig, ax = plt.subplots(figsize=(12,7))
electricity_seq = views.node(results, 'electricity')['sequences']
plot_slice = oev.plot.slice_df(electricity_seq,
                               date_from=pd.datetime(2012, 2, 15))
my_plot = oev.plot.io_plot('electricity', plot_slice, cdict=cdict,
                           inorder=inorder, ax=ax,
                           smooth=False)

ax = shape_legend('electricity', **my_plot)
oev.plot.set_datetime_ticks(ax, plot_slice.index, tick_distance=48,
                            date_format='%d-%m-%H', offset=12)

ax.set_ylabel('Power in MW')
ax.set_xlabel('2012')
ax.set_title("Electricity demand and production")
# ax.tick_params()
ax.get_figure()
fig.savefig('dispatch.png', dpi=100, bbox_inches='tight')



# plot investment
params = {'storage': processing.convert_keys_to_strings(results)[(('storage', 'None'))]['scalars']['invest'],
          'wind': params['wind_nom_val'],
          'pv': params['pv_nom_val']}

cdict = {
    # 'rgas': '#636f6b',
    'pv': '#ffde32',
    'storage': '#42c77a',
    'wind': '#5b5bae'}

# cdict = ['#5b5bae','#ffde32','#636f6b']


# fig = plt.figure(figsize=(17, 4))
# plt.bar(range(len(params)), list(params.values()), align='center', color=cdict.values())
# plt.xticks(range(len(params)), list(params.keys()), fontsize=25)
# plt.yticks(fontsize=25)
# plt.ylabel('Power [MW]', fontsize=25)
# plt.title("Installed capacities", fontsize=25)
# plt.savefig('investment.png', dpi=100)
# # plt.show()


rc('font',**{'family':'sans-serif','sans-serif':['DejaVu Sans'],'size':20})
fig, ax = plt.subplots()
ax.bar(range(len(params)), list(params.values()), align='center', color=cdict.values())
ax.set_xticks(range(len(params)))
ax.set_xticklabels(list(params.keys()))
ax.set_ylabel('Power [MW]')
ax.set_title("Installed capacities")
fig.savefig('investment_2.png', dpi=100)