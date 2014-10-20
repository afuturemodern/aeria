import sys
import soundcloud
from sc_pagerank import getNeighbors, computePR, initializePR
import networkx as nx 

# A global artist graph used to iterate through the various algorithms.
# Each node is artist id, with edges weighted by activity between then.
artistGraph = nx.MultiDiGraph()

client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

raw_name = raw_input("Enter a soundcloud artist to analyze: ")

# Artist of interest[
search = client.get('/users/', q = raw_name)[0]

artistGraph.add_node(search.id, currPR = 0, newPR = 0)

print("Artist interpreted as: " + search.username)
# need to compute all neighbors in given graph selection before we can compute the 
# pr of each node. 

depth = 2
i = 0
for t in range(depth):
	print "Iteration " + str(t)
	for artist in artistGraph.nodes():
		print "Artist " + str(i) + " of " + str(len(artistGraph.nodes()))
		getNeighbors(artist, artistGraph)
		i += 1

# Go through the graph and compute each PR until it converges.
iterations = 10
computePR(artistGraph, 0.85, iterations)

prList = []

for artist in artistGraph.nodes():
	prList.append((artist, artistGraph.node[artist]['currPR']))

prList.sort(key = lambda tup: tup[1]) # Sort the list in palce

prList.reverse() # order by descending PR

print ("Here are some artists similar to " + str(search.username) )
try:
	for item in prList[0:10]:
		artist = client.get('/users/' + str(item[0]));
		try:
			print str(artist.username), item[1]
		except UnicodeEncodeError as e:
			print "Unicode Error, using artist ID: " + str(artist.id) + str(item[1])
except: 
	print "Unexpected error:", sys.exc_info()[0]
