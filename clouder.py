import sys
import networkx as nx
import soundcloud

from geoff import get_geoff
from py2neo.ext.geoff import GeoffLoader

from cloudreader import read_graph


def post_to_cloud(G):
    GeoffLoader.load(get_geoff(G))

# artistGraph = nx.MultiDiGraph()
# read_graph(artistGraph, 'artistGraph.net')
# post_to_cloud(artistGraph)
    



