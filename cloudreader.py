import sys
import networkx as nx
import soundcloud
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

for artist in artistGraph.nodes():
	if artist:
		try:
			username = scac.id2username(artist)
			followings = artistGraph.successors(artist)
			followers = artistGraph.predecessors(artist)
			try:	
				print "\t", username + " has " + str(len(followings)) + " followings"
				print "\t", username + " follows " + ", ".join(map(lambda x: scac.id2username(x), followings))
			except TypeError: 
				print "No followings home!"	
			try:	
				print "\t", username + " has " + str(len(followers)) + " followers"
				print "\t", username + " is followed by " + ", ".join(map(lambda x: scac.id2username(x), followers))
			except TypeError:
				print "No followers home!"
			print "-"*40
		except UnicodeError:
			print "Artist's username not found"	
