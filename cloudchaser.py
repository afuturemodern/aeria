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
#profileGraph = nx.MultiDiGraph()

client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

raw_name = raw_input("Enter a soundcloud artist to analyze: ")


# Artist of interest
search = client.get('/users/', q = raw_name)[0]

# Establish communication queues
tasks = mp.Queue()
results = mp.Queue()

print "Artist interpreted as: %s" % scac.getUsername(search)
# need to compute all neighbors in given graph selection before we can compute the
# pr of each node.
print "="*20

# initialize the task queue
artists_to_enqueue = [search]

depth = 4
i = 0

# number of processes basically
num_consumers = mp.cpu_count()

# list of artists we could not query
unavailable_artists = []

# let's make sure we handle accidental exits and clean up stuff
import signal
import atexit
def exit_handler():
    # kill all child processes we've spawned
    import psutil, os
    def kill_proc_tree(pid, including_parent=True):
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
        psutil.wait_procs(children, timeout=5)
        if including_parent:
            parent.kill()
            parent.wait(5)
    kill_proc_tree(os.getpid())

atexit.register(exit_handler)
signal.signal(signal.SIGINT, lambda signal, frame: exit_handler())

for t in range(depth):

    print "Iteration " + str(t)
    consumers = [Consumer(tasks, results) for i in xrange(num_consumers)]
    for w in consumers:
        w.start()

    # enqueue jobs
    num_jobs = 0
    artists_to_enqueue = list(set(artists_to_enqueue))

    for artist in artists_to_enqueue:
        try:
            print "\t", "Enqueueing: %s (%s)" % (scac.getUsername(artist), scac.getUserid(artist))
            scac.addNode(artist)
#           profileGraph.add_node(scac.getUserid(artist))
            num_jobs += bookTasks(tasks, artist)
        except:
            print "\t", "Item is problematic?", artist
            unavailable_artists.append(artist)

    print "\t", "--%d jobs enqueued" % num_jobs

    artists_to_enqueue = []

    # poison pill to kill off all workers when we finish
    for i in xrange(num_consumers):
        tasks.put(None)

    while num_jobs:
        artist, action, newArtist = results.get()
        #print artist, action, newArtist, num_jobs
        if newArtist is not None:
            actions = {"followings": scac.addFollowings,
                        "followers": scac.addFollowers,
                        "favorites": scac.addFavorites,
                        "comments": scac.addComments,
                        "tracks": scac.addTracks}
            # this is most likely a useless check as artist is already in the graph from above
            #if profileGraph.__contains__(scac.getUserid(artist)):
                # eg: addFollowings(artist, newArtist)
                actions[action](artist, [newArtist]) #, profileGraph)
                artists_to_enqueue.append(newArtist)
        else:
            # poison pill to finished that given job
            num_jobs -= 1
    print "\t", "--Finished all jobs!"

    # if we reach here, we've finished processing all artist tasks

#print "The artist graph currently contains " + str(len(profileGraph)) + " artists."
#
#print "The artist graph currently contains " + str(nx.number_strongly_connected_components(profileGraph)) + " strongly connected components."
#
#my_component = profileGraph
#
#for component in nx.strongly_connected_component_subgraphs(profileGraph):
#    if search.id in component:
#        my_component = component
#
#print "This artist's clique currently contains " + str(len(profileGraph)) + " artists."
#
# Go through the graph and compute each PR until it converges.
#iterations = 10
#print "Computing PageRank on your searched artist..."
#computePR(my_component , 0.85, iterations)
#
#prList = []
#
#for artist in my_component.nodes():
#    prList.append((artist, my_component.node[artist]['currPR']))
#
#prList.sort(key = lambda tup: tup[1]) # Sort the list in place
#
#prList.reverse() # order by descending PR
#
#print ("Here are some artists similar to " + str(search.username) )
#
#for item in prList[0:10]:
#    artist = scac.id2username(item[0])
#    print artist, item[1]
