import sys
import soundcloud
import networkx as nx
from requests.exceptions import ConnectionError
from sys import getrecursionlimit, setrecursionlimit

client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

def getFollowings(artist):
		# get list of users who the artist is following.
	# consider we may not want to always analyze the first 100, although it works since it should be
	# the hundred most frequent
	try: 
		followings = client.get('/users/' + str(artist) + '/followings', limit=100)
		a_dat = client.get('/users/' + str(artist))

		try:
			print "Analyzing " + str(a_dat.username.encode('utf-8')) + "\'s " + str(len(followings)) + " followings..."
		except UnicodeError:
			print "Unicode Error, using artist ID: " + str(artist)
		except NameError:
			print "Name error, using artist ID: " + str(artist)	
		except:
			print "Unexpected error:", sys.exc_info()[0]	

		return [user.id for user in followings]
		
	except ConnectionError, e:
		print e
		getFollowings(artist)

	except TypeError:
		print "Artist was not there!"
		return []

	except RuntimeError, e:
		print e
		return []

	except Exception, e:
		print 'Error: %s, Status Code: %d' % (e.message, e.response.status_code)
		getFollowings(artist)

	except:
		print "Unexpected error:", sys.exc_info()[0]
		return []

def getFollowers(artist):
	try:
		followers = client.get('/users/' + str(artist) + '/followers', limit=100)
		a_dat = client.get('/users/' + str(artist))
		
		try:
			print "Analyzing " + str(a_dat.username.encode('utf-8')) + "\'s " + str(len(followers)) + " followers..."
		except UnicodeError:
			print "Unicode Error, using artist ID: " + str(artist)
		except NameError:
			print "Name error, using artist ID: " + str(artist)	
		except:
			print "Unexpected error:", sys.exc_info()[0]	
		return [user.id for user in followers]

	except ConnectionError, e:
		print e	
		getFollowers(artist)

	except TypeError:
		print "Artist was not there!"
		return []

	except RuntimeError, e:
		print e
		return []

	except Exception, e:
		print 'Error: %s, Status Code: %d' % (e.message, e.response.status_code)
		getFollowers(artist) 
		
	except: 	
		print "Unexpected error:", sys.exc_info()[0]
		return []

def getFavorites(artist):
	try:
		favorites = client.get('/users/' + str(artist) + '/favorites', limit=100)
		try:
			print "Analyzing " + str(a_dat.username.encode('utf-8')) + "\'s " + str(len(favorites)) + " favorites..."
		except UnicodeError:
			print "Unicode Error, using artist ID: " + str(artist)
		except NameError:
			print "Name error, using artist ID: " + str(artist)	
		except: 		
			print "Unexpected error:", sys.exc_info()[0]

		return [user.id for user in favorites]

	except ConnectionError, e:
		print e	
		getFavorites(artist)

	except TypeError:
		print "Artist was not there!"
		return []

	except RuntimeError, e:
		print e
		return []

	except Exception, e:
		print 'Error: %s, Status Code: %d' % (e.message, e.response.status_code)
		getFavorites(artist)

	except:
		print "Unexpected error:", sys.exc_info()[0]
		return []

def getComments(artist):
	try:
		comments = client.get('/users/' + str(artist) + '/comments', limit=100)
		try:
			print "Analyzing " + str(a_dat.username.encode('utf-8'))  + "\'s " + str(len(comments)) + " comments..."
		except UnicodeError:
			print "Unicode Error, using artist ID: " + str(artist)
		except NameError:
			print "Name error, using artist ID: " + str(artist)	
		except:
			print "Unexpected error:", sys.exc_info()[0]	

		return [user.id for user in comments]

	except ConnectionError, e:
		print e
		getComments(artist)	

	except TypeError:
		print "Artist was not there!"
		return []

	except RuntimeError, e:
		print e
		return []

	except Exception, e:
		print 'Error: %s, Status Code: %d' % (e.message, e.response.status_code)
		getComments(artist)

	except:
		print "Unexpected error:", sys.exc_info()[0]
		return []

def getTracks(artist):
	try:
		tracks = client.get('/users/' + str(artist) + '/tracks', limit=100)
	
		try:
			print "Analyzing " + str(a_dat.username.encode('utf-8')) + "\'s " + str(len(tracks)) + " tracks..."
		except UnicodeError:
			print "Unicode Error, using artist ID: " + str(artist)
		except NameError:
			print "Name error, using artist ID: " + str(artist)	
		except:
			print "Unexpected error:", sys.exc_info()[0]	

		return [track.id for track in tracks]

	except ConnectionError, e:
		print e	
		getTracks(artist)

	except TypeError:
		print "Artist was not there!"
		return []

	except RuntimeError, e:
		print e
		return []

	except Exception, e:
		print 'Error: %s, Status Code: %d' % (e.message, e.response.status_code)
		getTracks(artist)
	
	except:
	 	print "Unexpected error:", sys.exc_info()[0]
	 	return []

def addFollowings(artist, followings, artistGraph):
	for user in followings:
		artistGraph.add_edge(artist, user, key = 'fol_weight', weight = 1)
		print "User %s successfully added to artistGraph!" % str(client.get('/users/' + str(user)).username.encode('utf-8'))


def addFollowers(artist, followers, artistGraph):
	for user in followers:
		artistGraph.add_edge(user, artist, key = 'fol_weight', weight = 1)
		print "User %s successfully added to artistGraph!" % str(client.get('/users/' + str(user)).username.encode('utf-8'))

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
				