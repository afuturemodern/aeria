import sys
import networkx as nx
import sqlite3
import random

import soundcloud
from .sc_pagerank import computePR, initializePR
import sc_api_calls as scac

import multiprocessing as mp
from cc_mp_classes import Consumer, Task, bookTasks

# A global artist graph used to iterate through the various algorithms.
# Each node is artist id, with edges weighted by activity between then.
artistGraph = nx.MultiDiGraph()

tasks = mp.Queue()
results = mp.Queue()

try:
    print("Reading in artist graph...")
    artistGraph = nx.read_pajek("artistGraph.net")
    print("Read successfully!")
    print("The artist graph currently contains " + str(len(artistGraph)) + " artists.")
    print(
        "The artist graph currently contains "
        + str(nx.number_strongly_connected_components(artistGraph))
        + " strongly connected components."
    )
except IOError:
    print("Could not find artistGraph")


def my_shuffle(A):
    random.shuffle(A)
    return A


rartists = my_shuffle(artistGraph.nodes())

for artist_id in rartists:

    # initialize the task queue
    artists_to_enqueue = [artist_id]

    depth = 3
    i = 0

    # number of processes basically
    num_consumers = mp.cpu_count()

    # list of artists we could not query
    unavailable_artists = []

    for t in range(depth):

        print("Iteration " + str(t))
        consumers = [Consumer(tasks, results) for i in range(num_consumers)]
        for w in consumers:
            w.start()

        # enqueue jobs
        num_jobs = 0
        artists_to_enqueue = list(set(artists_to_enqueue))

        for artist in artists_to_enqueue:
            username = scac.id2username(artist)
            try:
                print("\t", "Enqueueing: %s (%s)" % (username, artist))
                artistGraph.add_node(artist)
                bookTasks(tasks, artist)
                num_jobs += 1
            except UnicodeDecodeError:
                print("\t", "Artist ID %s is not query-able" % artist)
                unavailable_artists.append(artist)

        print("\t", "--%d jobs enqueued" % num_jobs)

        artists_to_enqueue = []

        # poison pill to kill off all workers when we finish
        for i in range(num_consumers):
            tasks.put(None)

        while num_jobs:
            artist, action, newArtists = results.get()
            if newArtists:
                actions = {
                    "followings": scac.addFollowings,
                    "followers": scac.addFollowers,
                    "favorites": scac.addFavorites,
                    "comments": scac.addComments,
                    "tracks": scac.addTracks,
                }
                # this is most likely a useless check as artist is already in the graph from above
                if artistGraph.__contains__(artist):
                    # eg: addFollowings(artist, newArtists)
                    actions[action](artist, newArtists, artistGraph)
                    artists_to_enqueue.extend(newArtists)
                num_jobs -= 1

        print("\t", "--Finished all jobs!")

        # if we reach here, we've finished processing all artist tasks

print("The artist graph currently contains " + str(len(artistGraph)) + " artists.")

print(
    "The artist graph currently contains "
    + str(nx.number_strongly_connected_components(artistGraph))
    + " strongly connected components."
)
