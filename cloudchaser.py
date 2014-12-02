import sys
import soundcloud
from sc_pagerank import computePR, initializePR
import sc_api_calls as scac 
import networkx as nx 

import multiprocessing as mp 

class Consumer(mp.Process):
	def __init__(self, task_queue, result_queue):
		mp.Process.__init__(self)
		self.task_queue = task_queue
		self.result_queue = result_queue

	def run(self):
		proc_name = self.name
		while True:
			next_task = self.task_queue.get()
			if next_task is None:
                                print "%s is dying!" % proc_name
				# Poison pill means we should exit
				break
			answer = next_task()
			self.result_queue.put([next_task.artist, next_task.action, answer])
		return

class Task(object):
	def __init__(self, artist, action):
		self.artist = artist
		self.action = action
	def __call__(self):
		actions = {"followings": scac.getFollowings,
                           "followers": scac.getFollowers,
                           "favorites": scac.getFavorites,
                           "comments": scac.getComments,
                           "tracks": scac.getTracks}
		if self.artist:		
			results = list(set(actions[self.action](self.artist)))
			if results and results is not None:
				return results
		return []
	def __str__(self):
		return 'Get %s: %s' % (self.action, self.artist)

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

# Establish communication queues
tasks = mp.Queue()
results = mp.Queue()

def bookTasks(tasksQueue, artist):
	actions = ["followings",
                   "followers",
                   "favorites",
                   "comments",
                   "tracks"]
	for action in actions:
		tasksQueue.put(Task(artist, action))

print "Artist interpreted as: %s" % search.username
# need to compute all neighbors in given graph selection before we can compute the 
# pr of each node. 
print "="*20

# initialize the task queue
artists_to_enqueue = [search.id]

depth = 2
i = 0

# number of processes basically
num_consumers = mp.cpu_count()

# list of artists we could not query
unavailable_artists = []

for t in range(depth):

	num_jobs = 0
  	print "Iteration " + str(t)
	consumers = [Consumer(tasks, results) for i in xrange(num_consumers)]
	for w in consumers:
		w.start()

	# enqueue jobs
	num_jobs = 0
	artists_to_enqueue = list(set(artists_to_enqueue))

	for artist in artists_to_enqueue:
                username = scac.id2username(artist)
                # must not be in the graph and must exist
                if username and not artistGraph.__contains__(artist):
                  print "\t", "Enqueueing: %s (%s)" % (username, artist)
                  artistGraph.add_node(artist)
                  bookTasks(tasks, artist)
                  num_jobs += 1
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
                          artists_to_enqueue += newArtists
			num_jobs -= 1
        print "\t", "--Finished all jobs!"

	# if we reach here, we've finished processing all artist tasks

print "The artist graph currently contains " + str(len(artistGraph.nodes())) + " artists."
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
