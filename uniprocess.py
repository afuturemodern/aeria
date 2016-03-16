import sys
import networkx as nx
import soundcloud
from sc_pagerank import computePR, initializePR
import sc_api_calls as scac

from cloudprinter import print_graph

# A global profile graph used to iterate through the various algorithms.
# Each node is profile id, with edges weighted by activity between then.
profileGraph = nx.MultiDiGraph()

# read_graph(profileGraph, 'profileGraph.net')
client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

raw_name = raw_input("Enter a soundcloud profile to analyze: ")

# Artist of interest
search = client.get('/users/', q = raw_name)[0]

print "Artist interpreted as: %s" % search.username
# need to compute all neighbors in given graph selection before we can compute the
# pr of each node.
print "="*20

# initialize the task queue
profiles_to_enqueue = [search.id]

depth = 2
i = 0

# list of profiles we could not query
unavailable_profiles = []

for t in range(depth):

	print "Iteration " + str(t)

	profiles_to_enqueue = list(set(profiles_to_enqueue))

	for profile in profiles_to_enqueue:
		username = scac.id2username(profile)
		if username:
			print "\t", "Enqueueing: %s (%s)" % (username, profile)
                        profileGraph.add_node(profile)

			newFollowings = scac.getFollowings(profile)
			print "New followings: " + ", ".join([scac.id2username(user) if isinstance(scac.id2username(user), str) else str(user) for user in newFollowings])
			scac.addFollowings(profile, newFollowings, profileGraph)
			profiles_to_enqueue.extend(newFollowings)

			newFollowers = scac.getFollowers(profile)
			print "New followers: " + ", ".join([scac.id2username(user) if isinstance(scac.id2username(user), str) else str(user) for user in newFollowers])
			scac.addFollowers(profile, newFollowers, profileGraph)
			profiles_to_enqueue.extend(newFollowers)

			newFavorites = scac.getFavorites(profile)
			print "New Favorites: " + ", ".join([scac.id2username(user) if isinstance(scac.id2username(user), str) else str(user) for user in newFavorites])
			scac.addFavorites(profile, newFavorites, profileGraph)
			profiles_to_enqueue.extend(newFavorites)

			newComments = scac.getComments(profile)
			print "New Comments: " + ", ".join([scac.id2username(comment, 'comments') if isinstance(scac.id2username(comment, 'comments'), str) else str(comment) for comment in newComments])
			scac.addComments(profile, newComments, profileGraph)
			profiles_to_enqueue.extend(newComments)

			newTracks = scac.getTracks(profile)
			print "New Tracks: " + ", ".join([scac.id2username(track, 'tracks') if isinstance(scac.id2username(track, 'tracks'), str) else str(track) for track in newTracks])
			scac.addTracks(profile, newTracks, profileGraph)
			profiles_to_enqueue.extend(newTracks)

		else:
			print "\t", "Artist ID %s is not query-able" % profile
			unavailable_profiles.append(profile)

print "The profile graph currently contains " + str(len(profileGraph.nodes())) + " profiles."

print "Here are their connections."

print_graph(profileGraph)

print "The profile graph currently contains " + str(nx.number_strongly_connected_components(profileGraph)) + " strongly connected components."

# Go through the graph and compute each PR until it converges.
iterations = 10
print "Computing PageRank on our profileGraph..."
computePR(profileGraph, 0.85, iterations)

prList = []

for profile in profileGraph.nodes():
	prList.append((profile, profileGraph.node[profile]['currPR']))

prList.sort(key = lambda tup: tup[1]) # Sort the list in place

prList.reverse() # order by descending PR

print ("Here are some profiles similar to " + str(search.username) )

for item in prList[0:10]:
        profile = scac.id2username(item[0])
        print profile, item[1]
