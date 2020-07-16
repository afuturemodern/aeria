import sys
import networkx as nx 
import sqlite3 

import soundcloud
from sc_pagerank import computePR, initializePR
import sc_api_calls as scac

artistGraph = nx.MultiDiGraph()

try:
    print "Reading in artist graph..."
    artistGraph = nx.read_pajek('artistGraph.net')
    print "Read successfully!"
    print "The artist graph currently contains " + str(len(artistGraph)) + " artists."
    print "The artist graph currently contains " + str(nx.number_strongly_connected_components(artistGraph)) + " strongly connected components."
except IOError:
    print "Could not find artistGraph"

client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

raw_name = raw_input("Enter a soundcloud artist to analyze: ")


# Artist of interest
search = client.get('/users/', q = raw_name)[0]

print "Artist interpreted as: %s" % search.username
# need to compute all neighbors in given graph selection before we can compute the 
# pr of each node. 
print "="*20

my_component = artistGraph

for component in nx.strongly_connected_component_subgraphs(artistGraph):
    if search.id in component:
        my_component = component

# Go through the graph and compute each PR until it converges.
iterations = 10
print "Computing PageRank on your searched artist..."
computePR(my_component , 0.85, iterations)

prList = []

for artist in my_component.nodes():
    prList.append((artist, my_component.node[artist]['currPR']))

prList.sort(key = lambda tup: tup[1]) # Sort the list in place

prList.reverse() # order by descending PR

print ("Here are some artists similar to " + str(search.username) )

for item in prList[0:10]:
    artist = scac.id2username(item[0])
    print artist, item[1]

        
                
