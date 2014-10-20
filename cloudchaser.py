import sys
import soundcloud
from sc_pagerank import getNeighbors, computePR, initializePR, removeDangling

# A global artist dictionary used to iterate through the pagerank algorithm.
# it stores each artist object with it's id as a key.
artistDict = {}

# Artist class hold the id, inNeighbors, OutNeighbors, and pagerank probability
# for a given artist. The initialization of an artist also adds the artist ID to 
# the global artist list.
class Artist:
	def __init__(self, artist_id, artistDict):
		self.id = artist_id
		self.inNeighbors = []
		self.outNeighbors = []
		# self.pr = []
		self.currPR = 0
		self.newPR = 0
		if artist_id not in artistDict:
			artistDict[self.id] = self
	def addOutNeighbor(self, artist_id):
		self.outNeighbors.append(artist_id)
		if artist_id not in artistDict:
			Artist(artist_id, artistDict)
	def addInNeighbor(self, artist_id):
		self.inNeighbors.append(artist_id)
		if artist_id not in artistDict:
			Artist(artist_id, artistDict)


client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

raw_name = raw_input("Enter a soundcloud artist to analyze: ")

# Artist of interest
aoi = client.get('/users/', q = raw_name)

print("Artist interpreted as: " + aoi[0].username)

aoi = Artist(aoi[0].id, artistDict)

# need to compute all neighbors in given graph selection before we can compute the 
# pr of each node. 

depth = 2
i = 0
for t in range(depth):
	print "Iteration " + str(t)
	current_artists = artistDict.values()
	for artist in current_artists:
		print "Artist " + str(i) + " of " + str(len(current_artists))
		getNeighbors(artist)
		i += 1

# Go through the graph and compute each PR until it converges.
iterations = 10
computePR(artistDict, 0.85, iterations)

prList = []

for artist in artistDict.values():
	prList.append((artist.id, artist.currPR))

prList.sort(key = lambda tup: tup[1]) # Sort the list in palce

prList.reverse() # order by descending PR

print ("Here are some artists that " + str(aoi.id) + " is interested in:")
try:
	print aoi.inNeighbors
	print aoi.outNeighbors
	print "The PR of this artist is: " + str(aoi.currPR)
	print "The artists with the top 10 PR from the group of " + str(len(prList)) + " artists are: " 
	for item in prList[0:10]:
		artist = client.get('/users/' + str(item[0]));
		try:
			print str(artist.username), item[1]
		except UnicodeEncodeError as e:
			print "Unicode Error, using artist ID: " + str(artist.id) + str(item[1])
except: 
	print "Unexpected error:", sys.exc_info()[0]
