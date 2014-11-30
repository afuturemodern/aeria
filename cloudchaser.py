import sys
import soundcloud
from sc_pagerank import getNeighbors, computePR, initializePR
import networkx as nx 

import multiprocessing

class Consumer(multiprocessing.Process):
  def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
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
            self.result_queue.put([str(next_task),answer])
        return

class Task(object):
    def __init__(self, artist):
        self.artist = artist
    def __call__(self):
        neighbors = getArtists(self.artist)
        if neighbors:
            return neighbors
        return []
    def __str__(self):
        return '%s' % self.artist


# A global artist graph used to iterate through the various algorithms.
# Each node is artist id, with edges weighted by activity between then.
artistGraph = nx.MultiDiGraph()

client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

raw_name = raw_input("Enter a soundcloud artist to analyze: ")

# Artist of interest[
search = client.get('/users/', q = raw_name)[0]

# Establish communication queues
tasks = multiprocessing.Queue()
results = multiprocessing.Queue()

artistGraph.add_node(search.id, marked = 0, currPR = 0, newPR = 0)

print("Artist interpreted as: " + search.username)
# need to compute all neighbors in given graph selection before we can compute the 
# pr of each node. 

neighbors = getNeighbors(search.id)

depth = 2
i = 0
num_consumers = multiprocessing.cpu_count()
for t in range(depth):
	print "Iteration " + str(t)
	for artist in artistGraph.nodes():
                consumers = [Consumer(tasks, results) for i in xrange(num_consumers)]
                for w in consumers:
                  w.start()

                num_jobs = 0
		print "Artist " + str(i) + " of " + str(len(artistGraph.nodes()))
		if artistGraph.node[artist]['marked'] == 0:
                        newArtists = list(set(getArtists(artist)))
			# getNeighbors(artist, artistGraph)
                        for newArtist in newArtists:
                          tasks.put(Task(newArtist))
                          num_jobs += 1.0
                newArtists = list()
                # poison pill
                for i in xrange(num_consumers):
                  task.put(None)

                while num_jobs:
                  curr_results = results.get()
                  if curr_results:
                    for newArtist in curr_results:
                      getNeighbors(artist, artistGraph)
                    num_jobs -= 1
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
