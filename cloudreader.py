import sys
import networkx as nx
import soundcloud
import sc_api_calls as scac


def read_graph(G, gfile):
    print "Reading in artist graph..."
    try:
        G = nx.read_pajek(gfile)
        print "Read successfully!"
        print "The artist graph currently contains " + str(len(G)) + " artists."
        print "The artist graph currently contains " + str(nx.number_strongly_connected_components(G)) + " strongly connected components."
    except IOError:
        print "Could not find artistGraph"

def write_graph(G, gfile):
    try:
        print "Writing out new artists..."
        nx.write_pajek(G, gfile)
        print "New artists written successfully!"
        print "The artist graph currently contains " + str(len(G)) + " artists."
        print "The artist graph currently contains " + str(nx.number_strongly_connected_components(G)) + " strongly connected components."
    except IOError:
        print "New artists could not be written..."

def print_graph(G):
    for artist in G.nodes():
	if artist:
	    try:
		username = scac.id2username(artist)
		followings = G.successors(artist)
		followers = G.predecessors(artist)
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

# artistGraph = nx.MultiDiGraph()
# read_graph(artistGraph, 'artistGraph.net')
# print_graph(artistGraph)
