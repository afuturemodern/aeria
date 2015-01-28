import sys
import networkx as nx 
import soundcloud
from sc_pagerank import computePR, initializePR
import sc_api_calls as scac 

# A global artist graph used to iterate through the various algorithms.
# Each node is artist id, with edges weighted by activity between then.
artistGraph = nx.MultiDiGraph()

try:
	print "Reading in artist graph..."
	artistGraph = nx.read_graphml('artistGraph.graphml')
	print "Read successfully!"
except IOError:
	print "Could not find artistGraph.graphml"

client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

raw_name = raw_input("Enter a soundcloud artist to analyze: ")

# Artist of interest
search = client.get('/users/', q = raw_name)[0]

print "Artist interpreted as: %s" % search.username
# need to compute all neighbors in given graph selection before we can compute the 
# pr of each node. 
print "="*20

# initialize the task queue
artists_to_enqueue = [search.id]

depth = 2
i = 0

# list of artists we could not query
unavailable_artists = []

for t in range(depth):

	print "Iteration " + str(t)

	artists_to_enqueue = list(set(artists_to_enqueue))

	for artist in artists_to_enqueue:
		username = scac.id2username(artist)
		if username:
			print "\t", "Enqueueing: %s (%s)" % (username, artist)
                        artistGraph.add_node(artist)

			newFollowings = scac.getFollowings(artist)
			print "New followings: " + ", ".join([scac.id2username(user) for user in newFollowings])
			scac.addFollowings(artist, newFollowings, artistGraph)
			artists_to_enqueue.extend(newFollowings)

			newFollowers = scac.getFollowers(artist)
			print "New followers: " + ", ".join([scac.id2username(user) for user in newFollowers])
			scac.addFollowers(artist, newFollowers, artistGraph)
			artists_to_enqueue.extend(newFollowers)

			newFavorites = scac.getFavorites(artist)
			print "New Favorites: " + ", ".join([scac.id2username(user) for user in newFavorites])
			scac.addFavorites(artist, newFavorites, artistGraph)
			artists_to_enqueue.extend(newFavorites)

			newComments = scac.getComments(artist)
			print "New Comments: " + ", ".join([scac.id2username(user) for user in newComments])
			scac.addComments(artist, newComments, artistGraph)
			artists_to_enqueue.extend(newComments)	

			newTracks = scac.getTracks(artist)
			print "New Tracks: " + ", ".join([scac.id2username(user) for user in newTracks])
			scac.addTracks(artist, newTracks, artistGraph)
			artists_to_enqueue.extend(newTracks)	

		else:
			print "\t", "Artist ID %s is not query-able" % artist
			unavailable_artists.append(artist)

print "The artist graph currently contains " + str(len(artistGraph.nodes())) + " artists."

print "Here are their connections."

for artist in artistGraph.nodes():
	if artist:
		username = scac.id2username(artist)
		followings = artistGraph.successors(artist)
		followers = artistGraph.predecessors(artist)	
		print "\t", username + " has " + str(len(followings)) + " followings"
		print "\t", username + " follows " + ", ".join(map(lambda x: scac.id2username(x), followings))
		print "\t", username + " has " + str(len(followers)) + " followers"
		print "\t", username + " is followed by " + ", ".join(map(lambda x: scac.id2username(x), followers))
                print "-"*40

print "The artist graph currently contains " + str(nx.number_strongly_connected_components(artistGraph)) + " strongly connected components."

nx.write_graphml(artistGraph, 'artistGraph.graphml')

# Go through the graph and compute each PR until it converges.
iterations = 10
print "Computing PageRank on our artistGraph..."
computePR(artistGraph, 0.85, iterations)

prList = []

for artist in artistGraph.nodes():
	prList.append((artist, artistGraph.node[artist]['currPR']))

prList.sort(key = lambda tup: tup[1]) # Sort the list in place

prList.reverse() # order by descending PR

print ("Here are some artists similar to " + str(search.username) )

for item in prList[0:10]:
        artist = scac.id2username(item[0])
        print artist, item[1]
