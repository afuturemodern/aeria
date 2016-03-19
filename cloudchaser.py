import sys
import networkx as nx
import sqlite3

import soundcloud
from sc_pagerank import computePR, initializePR
import sc_api_calls as scac

import multiprocessing as mp
from cc_mp_classes import Consumer, Task, bookTasks

# A global artist graph used to iterate through the various algorithms.
# Each node is artist id, with edges weighted by activity between then.
artistGraph = nx.MultiDiGraph()

client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

raw_name = raw_input("Enter a soundcloud artist to analyze: ")


# Artist of interest
search = client.get('/users/', q = raw_name)[0]

# Establish communication queues
tasks = mp.Queue()
results = mp.Queue()

print "Artist interpreted as: %s" % search.username
# need to compute all neighbors in given graph selection before we can compute the
# pr of each node.
print "="*20

# initialize the task queue
artists_to_enqueue = [search.id]

depth = 4
i = 0

# number of processes basically
num_consumers = mp.cpu_count()

# list of artists we could not query
unavailable_artists = []

for t in range(depth):

    print "Iteration " + str(t)
    consumers = [Consumer(tasks, results) for i in xrange(num_consumers)]
    for w in consumers:
        w.start()

    # enqueue jobs
    num_jobs = 0
    artists_to_enqueue = list(set(artists_to_enqueue))

    for artist in artists_to_enqueue:
        username = scac.id2username(artist)
        if username:
            print "\t", "Enqueueing: %s (%s)" % (username, artist)
            artistGraph.add_node(artist)
            num_jobs += bookTasks(tasks, artist)
        else:
            print "\t", "Artist ID %s is not query-able" % artist
            unavailable_artists.append(artist)

    print "\t", "--%d jobs enqueued" % num_jobs

    artists_to_enqueue = []

    # poison pill to kill off all workers when we finish
    for i in xrange(num_consumers):
        tasks.put(None)

    while num_jobs:
        artist, action, newArtists = results.get()
        #print artist, action, newArtists, num_jobs
        if newArtists:
            actions = {"followings": scac.addFollowings,
                        "followers": scac.addFollowers,
                        "favorites": scac.addFavorites,
                        "comments": scac.addComments,
                        "tracks": scac.addTracks}
            # this is most likely a useless check as artist is already in the graph from above
            if artistGraph.__contains__(artist):
                # eg: addFollowings(artist, newArtists)
                actions[action](artist, newArtists, artistGraph)
                artists_to_enqueue.extend(newArtists)
        num_jobs -= 1

    print "\t", "--Finished all jobs!"

    # if we reach here, we've finished processing all artist tasks

print "The artist graph currently contains " + str(len(artistGraph)) + " artists."

print "The artist graph currently contains " + str(nx.number_strongly_connected_components(artistGraph)) + " strongly connected components."

my_component = artistGraph

for component in nx.strongly_connected_component_subgraphs(artistGraph):
    if search.id in component:
        my_component = component

print "This artist's clique currently contains " + str(len(artistGraph)) + " artists."

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
