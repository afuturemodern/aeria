import sys
import networkx as nx
import soundcloud

from geoff import get_geoff
# import py2neo as ptn
# import py2neo.ext.geoff as ptn
from py2neo.ext.geoff import GeoffLoader

from cloudreader import read_graph


def post_to_cloud(G):
    geoff_string = get_geoff(G)
    print(geoff_string)
    GeoffLoader.load(geoff_string)

# artistGraph = nx.MultiDiGraph()
# read_graph(artistGraph, 'artistGraph.net')
# post_to_cloud(artistGraph)
    



