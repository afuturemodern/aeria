import sys
import soundcloud
import networkx as nx 

client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

def getFollowings(artist):
		# get list of users who the artist is following.
	# consider we may not want to always analyze the first 100, although it works since it should be
	# the hundred most frequent
	try: 
		followings = client.get('/users/' + str(artist) + '/followings', limit=100)
		a_dat = client.get('/users/' + str(artist))

		try:
			print "Analyzing " + str(a_dat.username) + "\'s " + str(len(followings)) + " followings..."
		except:
			print "Unicode Error, using artist ID: " + str(artist)	
		
	except:
		print "Unexpected error:", sys.exc_info()[0]

	return [user.id for user in followings]	

def getFollowers(artist):
	try:
		followers = client.get('/users/' + str(artist) + '/followers', limit=100)
		
		try:
			print "Analyzing " + str(a_dat.username) + "\'s " + str(len(followers)) + " followers..."
		except:
			print "Unicode Error, using artist ID: " + str(artist)	
	
	except:
		print "Unexpected error:", sys.exc_info()[0]

	return [user.id for user in followers]	

def getFavorites(artist):
	try:
		favorites = client.get('/users/' + str(artist) + '/favorites', limit=100)
		try:
			print "Analyzing " + str(a_dat.username) + "\'s " + str(len(favorites)) + " favorites..."
		except:
			print "Unicode Error, using artist ID: " + str(artist)	

	except:
		print "Unexpected error:", sys.exc_info()[0]

	return [user.id for user in favorites]		

def getComments(artist):
	try:
		comments = client.get('/users/' + str(artist) + '/comments', limit=100)
		try:
			print "Analyzing " + str(a_dat.username)  + "\'s " + str(len(comments)) + " comments..."
		except:
			print "Unicode Error, using artist ID: " + str(artist)

	except:
		print "Unexpected error:", sys.exc_info()[0]

	return [user.id for user in comments]		

def getTracks(artist):
	try:
		tracks = client.get('/users/' + str(artist) + '/tracks', limit=100)
	
		try:
			print "Analyzing " + str(a_dat.username) + "\'s " + str(len(tracks)) + " tracks..."
		except:
			print "Unicode Error, using artist ID: " + str(artist)
	except:
	 	print "Unexpected error:", sys.exc_info()[0]
	 	
	return [track.id for track in tracks] 

def addFollowings(artist, followings, artistGraph):
	for user in followings:
		artistGraph.add_edge(artist, user, key = 'fol_weight', weight = 1)
		print "User successfully added to artistGraph!"


def addFollowers(artist, followers, artistGraph):
	for user in followers:
		artistGraph.add_edge(user, artist, key = 'fol_weight', weight = 1)
		print "User successfully added to artistGraph!"

def addFavorites(artist, favorites, artistGraph):
	for user in favorites:
			if artistGraph.has_edge(artist, user, 'fol_weight'):
				if artistGraph.has_edge(artist, user, 'fav_weight'):
					artistGraph.add_edge(artist, user, key = 'fav_weight', 
						weight = artistGraph.get_edge_data(artist, user, key = 'fav_weight')['weight'] + 1)
				else:
					artistGraph.add_edge(artist, user, key = 'fav_weight', weight = 1)	

def addComments(artist, comments, artistGraph):
	for user in comments:
			if artistGraph.has_edge(artist, user, 'fol_weight'):
				if artistGraph.has_edge(artist, user, 'com_weight'):
					artistGraph.add_edge(artist, user, key = 'com_weight', 
						weight = artistGraph.get_edge_data(artist, user, key = 'com_weight')['weight'] + 1)
				else:
					artistGraph.add_edge(artist, user, key = 'com_weight', weight = 1)

def addTracks(artist, tracks, artistGraph):
	for track in tracks:

			# get list of users who have favorited this users track
			try:
	 			favoriters = client.get('/tracks/' + str(track) + '/favoriters')
	 			for user in favoriters:
	 				if artistGraph.has_edge(user, artist, 'fol_weight'):
						if artistGraph.has_edge(user, artist, 'fav_weight'):
							artistGraph.add_edge(user, artist, key = 'fav_weight', 
								weight = artistGraph.get_edge_data(user, artist, key = 'fav_weight')['weight'] + 1)
						else:
							artistGraph.add_edge(user, artist, key = 'fav_weight', weight = 1)
	 		except:
	 			print "Unexpected error:", sys.exc_info()[0]

	 		try:
	 			commenters = client.get('/tracks/' + str(track) + '/comments')
	 			for user in commenters:
					if artistGraph.has_edge(user, artist, 'fol_weight'):
						if artistGraph.has_edge(user, artist, 'com_weight'):
							artistGraph.add_edge(user, artist, key = 'com_weight', 
								weight = artistGraph.get_edge_data(user, artist, key = 'com_weight')['weight'] + 1)
						else:
							artistGraph.add_edge(user, artist, key = 'com_weight', weight = 1)	
	 		except:
	 			print "Unexpected error:", sys.exc_info()[0]			
				