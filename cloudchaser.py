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
            self.result_queue.put([next_task.artist, next_task.action, answer])
        return

class Task(object):
    def __init__(self, artist, action):
        self.artist = artist
        self.action = action
    def __call__(self):
        actions = {"followings": getFollowings,
                   "followers": getFollowers,
                   "favorites": getFavorites,
                   "comments": getComments,
                   "tracks": getTracks}

        results = list(set( actions[action](artist) ))
        if results
            return results
        return []
    def __str__(self):
        return 'Get %s: %s' % (self.action, self.artist)


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

def bookTasks(tasksQueue, artist):
  actions = ["followings",
             "followers",
             "favorites",
             "comments",
             "tracks"]
  for action in actions:
    tasksQueue.put(Task(newArtist, action))

print("Artist interpreted as: " + search.username)
# need to compute all neighbors in given graph selection before we can compute the 
# pr of each node. 


# initialize the task queue
artists_to_enqueue = [search.id]

depth = 2
i = 0
num_consumers = multiprocessing.cpu_count()
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
    print "Artist %s" % artist
      bookTasks(tasks, artist)
      num_jobs += 1
  artists_to_enqueue = []
  # poison pill to kill off all workers when we finish
  for i in xrange(num_consumers):
    task.put(None)

  while num_jobs:
    artist, action, newArtists = results.get()
    if newArtists:
      actions = {"followings": addFollowings,
                 "followers": addFollowers,
                 "favorites": addFavorites,
                 "comments": addComments,
                 "tracks": addTracks}
      # eg: addFollowings(artist, newArtists)
      actions[action](artist, newArtists)
      artists_to_enqueue += newArtists
      num_jobs -= 1
  # if we reach here, we've finished processing all artist tasks

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
