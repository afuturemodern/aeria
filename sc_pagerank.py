import sys
import soundcloud
import networkx as nx 


client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

def getNeighbors(artist, artistGraph):
	""" Given an artist id, this functions populates the social network centered around the artist"""

	# The following three lists are gathered to compute the outNeighbors list.
	# A soundcloud user is considered an outNeighbor if they are followed by,
	# have a track favorited by, or a track commented on by the given artist.
	try:

		# get list of users who the artist is following.
		# consider we may not want to always analyze the first 100, although it works since it should be
		# the hundred most frequent 
		followings = client.get('/users/' + str(artist) + '/followings', limit=100)
		print "Analyzing " + str(artist) + "\'s " + str(len(followings)) + " followings..."
		for user in followings:
			if not artistGraph.__contains__(user.id):
				try:
					artistGraph.add_node(user.id)
					artistGraph.node[user.id]['currPR'] = 0
					artistGraph.node[user.id]['newPR'] = 0
					artistGraph.node[user.id]['marked'] = 0
					artistGraph.add_edge(artist, user.id, key = fol_weight, weight = 1)
				except:
					print "Unexpected error:", sys.exc_info()[0]	

		# get list of songs the artist favorites.
		favorites = client.get('/users/' + str(artist) + '/favorites', limit=100)
		print "Analyzing " + str(artist) + "\'s " + str(len(favorites)) + " favorites..."
		for user in favorites:
			if artistGraph.has_edge(artist, user.id, fol_weight):
				if artistGraph.has_edge(artist, user.id, fav_weight):
					artistGraph.add_edge(artist, user.id, key = fav_weight, 
						weight = artistGraph.get_edge_data(artist, user.id, key = fav_weight) + 1)
				else:
					artistGraph.add_edge(artist, user.id, key = fav_weight, weight = 1)	

		# get list comments the artist has made.
		comments = client.get('/users/' + str(artist) + '/comments', limit=100)
		print "Analyzing " + str(artist)  + "\'s " + str(len(comments)) + " comments..."
		for user in comments:
			if artistGraph.has_edge(artist, user.id, fol_weight):
				if artistGraph.has_edge(artist, user.id, com_weight):
					artistGraph.add_edge(artist, user.id, key = com_weight, 
						weight = artistGraph.get_edge_data(artist, user.id, key = com_weight) + 1)
				else:
					artistGraph.add_edge(artist, user.id, key = com_weight, weight = 1)	
		# The following two lists are gathered to compute the inNeighbors list.
		# A soundcloud user is considered an inNeighbor if they follow,
		# favorite, or have commented on a track by the given artist.

		# get list of who follows the artist
		followers = client.get('/users/' + str(artist) + '/followers', limit=100)
		print "Analyzing " + str(artist) + "\'s " + str(len(followers)) + " followers..."
		for user in followers:
			if not artistGraph.__contains__(user.id):
				try:
					artistGraph.add_node(user.id)
					artistGraph.node[user.id]['currPR'] = 0
					artistGraph.node[user.id]['newPR'] = 0
					artistGraph.node[user.id]['marked'] = 0
					artistGraph.add_edge(user.id, artist, key = fol_weight, weight = 1)
				except:
					print "Unexpected error:", sys.exc_info()[0]

		# get a list of tracks by the user in order to list the users
		# having favorited, commented these tracks
		artist_tracks = client.get('/users/' + str(artist) + '/tracks', limit=100)
		print "Analyzing " + str(artist) + "\'s " + str(len(artist_tracks)) + " tracks..."
		for track in artist_tracks:
			try:
			# get list of users who have favorited this users track 
		 		favoriters = client.get('/tracks/' + str(track.id) + '/favoriters')
		 		if artistGraph.has_edge(user.id, artist, fol_weight):
					if artistGraph.has_edge(user.id, artist, fav_weight):
						artistGraph.add_edge(user.id, artist, key = fav_weight, 
							weight = artistGraph.get_edge_data(artist, user.id, key = fav_weight) + 1)
				else:
					artistGraph.add_edge(user.id, artist, key = fav_weight, weight = 1)

				track_comments = client.get('/tracks/' + str(track.id) + '/comments')
				if artistGraph.has_edge(user.id, artist.id, fol_weight):
					if artistGraph.has_edge(user.id, artist.id, com_weight):
						artistGraph.add_edge(user.id, artist, key = com_weight, 
							weight = artistGraph.get_edge_data(artist, user.id, key = com_weight) + 1)
				else:
					artistGraph.add_edge(user.id, artist, key = com_weight, weight = 1)
			except:
				print "Unexpected error:", sys.exc_info()[0]
		artistGraph.node[artist]['marked'] = 1			
	
	except:
		print "Unexpected error:", sys.exc_info()[0]

def initializePR(artistGraph):
	""" Sets the initial PR value of every artist in the dictionary to 1/num_artists."""
	artists = artistGraph.nodes()
	for artist in artists:
			artistGraph.node[artist]['currPR'] = 1.0 / len(artists)
	return artists		

def computePR(artistGraph, damping, iterations):
	""" Given an artist object, damping factor, and iteration number, 
	    the computePR function computes the Page Rank value for that
	    artist and sets the attribute. """
	artists = initializePR(artistGraph)  
	i = 0
	while i < iterations:
		for artist in artists:
				for nartist in artists:
					artistGraph.node[artist]['newPR'] += artistGraph.node[nartist]['currPR'] * (1 - damping) / len(artists)
					if nartist in artistGraph.predecessors(artist):
						artistGraph.node[artist]['newPR'] += damping * artistGraph.node[nartist]['currPR'] / artistGraph.out_degree(nartist)
		for artist in artists:	
			artistGraph.node[artist]['currPR'] = artistGraph.node[artist]['newPR']
			artistGraph.node[artist]['newPR'] = 0
		i += 1





