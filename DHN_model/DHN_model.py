import networkx as nx
from math import sqrt
import matplotlib.pyplot as plt
import pandas as pd

# Reference: Xuezhi Liu Phd 2014 https://orca.cf.ac.uk/57830/1/2014LiuXPhD.pdf

# load incidence matrix
in_mat = pd.read_csv('incidence_matrix.csv', header=0, index_col='pipe_no')
print(in_mat.columns.tolist())

from_to = in_mat[['from_node', 'to_node']]
print(from_to)

from_to.to_csv('from_to.csv', index=False, header=False)

G = nx.DiGraph()
G.add_edges_from(
    [(0, 1), (0, 2), (3, 1), (4, 2), (4, 5),
     (1, 6), (2, 5), (2, 4), (3, 5)])


G = nx.DiGraph()
G = nx.read_edgelist('from_to.csv', delimiter=',', create_using=G)
# G = nx.from_pandas_dataframe(in_mat, 'from_node', 'to_node')

print(G.edges())

# Specify the edges you want to be red
red_edges = [('16', '15'), ('30', '28')]
# red_edges = []
edge_colours = ['black' if not edge in red_edges else 'red'
                for edge in G.edges()]
black_edges = [edge for edge in G.edges() if edge not in red_edges]

# Need to create a layout when doing
# separate calls to draw nodes and edges
pos = nx.circular_layout(G)
pos = nx.spring_layout(G)
pos = nx.fruchterman_reingold_layout(G)
nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'), 
                       node_color = 'green', node_size = 100)
nx.draw_networkx_labels(G, pos)
nx.draw_networkx_edges(G, pos, edgelist=red_edges, edge_color='r', arrows=True)
nx.draw_networkx_edges(G, pos, edgelist=black_edges, arrows=True)
plt.show()

print(nx.incidence_matrix(G, oriented=True).todense())
