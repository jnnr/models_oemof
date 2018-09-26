import networkx as nx
from math import sqrt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

G = nx.DiGraph()
G.add_edges_from(
    [(0, 1), (0, 2), (2, 3), (2, 4), (4, 5),
     (1, 6), (2, 4), (0, 7), (7, 8)])


A = nx.incidence_matrix(G, oriented=True).todense()
m = np.array([1,2,1,2.1,5,2,1,0,1])
m = np.array([0,1,1,1,1,1,1,1,1])
m[0] = - 2*np.sum(m[1:])
print(A.shape)
print(m.shape)
print(A)
print(m)
x = np.linalg.lstsq(A,m)[0]
print('x', x)


# Specify the edges you want to be red
red_edges = []
edge_colours = ['black' if not edge in red_edges else 'red'
                for edge in G.edges()]
black_edges = [edge for edge in G.edges() if edge not in red_edges]

# Need to create a layout when doing
# separate calls to draw nodes and edges
pos = nx.circular_layout(G)
pos = nx.spring_layout(G)
pos = nx.fruchterman_reingold_layout(G)
nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'), 
                       node_color = 'green', node_size = 100*m)
nx.draw_networkx_labels(G, pos)
nx.draw_networkx_edges(G, pos, edgelist=black_edges, width=abs(x), edge_color='r', arrows=True)
plt.show()


