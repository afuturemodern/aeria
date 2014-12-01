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

		results = list(set(actions[self.action](self.artist)))
		if results:
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

except:
	print "Unexpected error:", sys.exc_info()[0]

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

print("Artist interpreted as: " + search.username)
# need to compute all neighbors in given graph selection before we can compute the 
# pr of each node. 

# initialize the task queue
artists_to_enqueue = [search.id]

depth = 2
i = 0
num_consumers = mp.cpu_count()

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
		try:
			print "Now enqueueing the artist %s" % str(client.get('/users/' + str(artist)).username.encode('utf-8'))
		except:
			print "Unicode Error, using artist ID: " + str(artist)	
		artistGraph.add_node(artist)
		bookTasks(tasks, artist)
		num_jobs += 1

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
			# eg: addFollowings(artist, newArtists)
			actions[action](artist, newArtists, artistGraph)
			artists_to_enqueue += newArtists
			num_jobs -= 1

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

try:
	for item in prList[0:10]:
		artist = client.get('/users/' + str(item[0]))
		try:
			print str(artist.username.encode('utf-8')), item[1]
		except UnicodeEncodeError as e:
				print "Unicode Error, using artist ID: " + str(artist.id) + str(item[1])
except: 
	print "Unexpected error:", sys.exc_info()[0]
