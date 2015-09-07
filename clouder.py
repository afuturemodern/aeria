import sys
import networkx as nx
import soundcloud
from geoff import get_geoff
from py2neo.ext.geoff import GeoffLoader
artistGraph = nx.MultiDiGraph()

def post_to_cloud(G):
    GeoffLoader.load(get_geoff(G))

try:
    print "Reading artist graph..."
    artistGraph = nx.read_pajek('artistGraph.net')
    print "Read successfully!"
    print "The artist graph currently contains " + str(len(artistGraph)) + " artists."
    print "The artist graph currently contains " + str(nx.number_strongly_connected_components(artistGraph)) + " strongly connected components."
except IOError:
    print "Could not find artist graph."

post_to_cloud(artistGraph)
    



