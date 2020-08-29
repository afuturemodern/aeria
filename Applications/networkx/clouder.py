from .geoff import get_geoff

# import py2neo as ptn
# import py2neo.ext.geoff as ptn
from py2neo.ext.geoff import GeoffLoader


def post_to_cloud(G):
    geoff_string = get_geoff(G)
    print(geoff_string)
    GeoffLoader.load(geoff_string)


# artistGraph = nx.MultiDiGraph()
# read_graph(artistGraph, 'artistGraph.net')
# post_to_cloud(artistGraph)
