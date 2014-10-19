import sys
import soundcloud

client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

def getNeighbors(artist):
	""" Given an artist object, this functions populates the in neighbors and out
		neighbors attributes of the object. """

	# The following three lists are gathered to compute the outNeighbors list.
	# A soundcloud user is considered an outNeighbor if they are followed by,
	# have a track favorited by, or a track commented on by the given artist.
	try:
		# get list of users who the artist is following.
		# consider we may not want to always analyze the first 100, although it works since it should be
		# the hundred most frequent 
		followings = client.get('/users/' + str(artist.id) + '/followings', limit=100)
		# get list of songs the artist favorites.
		favorites = client.get('/users/' + str(artist.id) + '/favorites', limit=100)
		# get list comments the artist has made.
		comments = client.get('/users/' + str(artist.id) + '/comments', limit=100)

		# The following two lists are gathered to compute the inNeighbors list.
		# A soundcloud user is considered an inNeighbor if they follow,
		# favorite, or have commented on a track by the given artist.

		# get list of who follows the artist
		followers = client.get('/users/' + str(artist.id) + '/followers', limit=100)
		# get a list of tracks by the user in order to list the users
		# having favorited these tracks
		artist_tracks = client.get('/users/' + str(artist.id) + '/tracks', limit=100)

		# Populate the outNeighbor list with unique artist id's.
		print "Analyzing " + str(artist.id) + "\'s " + str(len(followings)) + " followings..."
		for user in followings:
			try:
				if user.id not in artist.outNeighbors:
					artist.addOutNeighbor(user.id)
			except:
				print "Unexpected error:", sys.exc_info()[0]

		print "Analyzing " + str(artist.id) + "\'s " + str(len(favorites)) + " favorites..."
		for track in favorites:
			try:
				track_artist = track.user["id"]
				if track_artist not in artist.outNeighbors:
					artist.addOutNeighbor(track_artist)
			except:
				print "Unexpected error:", sys.exc_info()[0]

		print "Analyzing " + str(artist.id)  + "\'s " + str(len(comments)) + " comments..."
		for comment in comments:
			try:
				track_info = client.get('/tracks/' + str(comment.track_id))
				track_artist = track_info.user["id"]
				if track_artist not in artist.outNeighbors:
						artist.addOutNeighbor(track_artist)
			except:
				print "Unexpected error:", sys.exc_info()[0]

		# Populate the inNeighbor list with unique artist id's.
		print "Analyzing " + str(artist.id) + "\'s " + str(len(followers)) + " followers..."
		for user in followers:
			try:
				if user.id not in artist.inNeighbors:
					artist.addInNeighbor(user.id)
			except:
				print "Unexpected error:", sys.exc_info()[0]

		# print "Analyzing " + str(artist.id) + "\'s " + str(len(artist_tracks)) + " tracks..."
		# for track in artist_tracks:
		# 	try:
		# 		# get list of users who have favorited this users track and
		# 		# add to inNeighbors 
		# 		favoriters = client.get('/tracks/' + str(track.id) + '/favoriters')
		# 		for user in favoriters:
		# 			if user.id not in artist.inNeighbors:
		# 				artist.addInNeighbor(user.id)

		# 		# get list of users who have commented on this users track and
		# 		# add to inNeighbors 
		# 		track_comments = client.get('/tracks/' + str(track.id) + '/comments')
		# 		for comment in track_comments:
		# 			if comment.user_id not in artist.inNeighbors:
		# 				artist.addInNeighbor(comment.user_id)
		# 	except:
		# 		print "Unexpected error:", sys.exc_info()[0]

	except:
		print "Unexpected error:", sys.exc_info()[0]



def removeDangling(cleanDict, danglingDict):
	""" Takes the artist dictionary as input and recursively removes dangling 
	    nodes until there are no more dangling nodes. The results are returned
	    as two new separated dictionaries"""
	newDangling = {}

	for artist_id in cleanDict.copy():
		if len(cleanDict[artist_id].outNeighbors) == 0:
			newDangling[artist_id] = cleanDict.pop(artist_id)

	if len(newDangling) == 0:
		return cleanDict, danglingDict
	else:
		danglingDict = dict(newDangling.items() + danglingDict.items())
		return removeDangling(cleanDict, danglingDict)


def computePR(artistDict, damping, iterations):
	""" Given an artist object, damping factor, and iteration number, 
	    the computePR function computes the Page Rank value for that
	    artist and sets the attribute. """

	# Set the initial values of all PR's
	initializePR(artistDict)
	
	cleanedDict, danglingDict = removeDangling(artistDict.copy(), {})

	i = 0
	while i < iterations:
		# prSum = 0

		# for artist_id in danglingDict:
		#	artist = artistDict.get(artist_id)
		#	prSum += damping * artist.pr[i - 1] / len(artistDict)

		for artist_id in artistDict:
			artist = artistDict.get(artist_id)
			# artist.pr.append((1 - damping) / len(artistDict) + prSum)
			for artist_id in artistDict:
				nartist = artistDict.get(artist_id)
				artist.nextPR += nartist.currPR * (1 - damping) / len(artistDict)
			# for neighbor in artist.inNeighbors:
			# 	if neighbor not in danglingDict:
			#		neighbor_artist = artistDict.get(neighbor)
			#		artist.pr[i] += damping * neighbor_artist.pr[i - 1] / len(neighbor_artist.outNeighbors)
				if nartist in artist.inNeighbors:
					artist.nextPR += damping * nartist.currPR / len(nartist.outNeighbors)
		for artist_id in artistDict:
			artist = artistDict.get(artist_id)			
			artist.currPR =	artist.nextPR
			artist.nextPR = 0
		i += 1


def initializePR(artistDict):
	""" Sets the initial PR value of every artist in the dictionary to 1/num_artists."""

	for artist in artistDict.values():
	#	artist.pr.append(1.0 / len(artistDict))
	artist.currPR = 1.0 / len(artistDict)




