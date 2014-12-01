import sys
import soundcloud
import networkx as nx
from requests.exceptions import ConnectionError, HTTPError
from sys import getrecursionlimit, setrecursionlimit

import traceback

client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

id2username_cache = {}

def id2username(artist):
  global id2username_dict
  try:
    username = id2username_cache.get(artist, None)
    if not username:
      username = str(client.get('/users/%s' % artist).username.encode('utf-8'))
      id2username_cache[artist] = username
    return username
  except ConnectionError:
    print "id2username(%s): could not make a connection" % artist
  except HTTPError:
    print "id2username(%s): received an HTTPError" % artist
  except UnicodeError:
    print "id2username(%s): unicode error in encoding username" % artist
  except Exception as e:
    print "Unexpected error:", sys.exec_info()[0]
    raise

def getFollowings(artist):
		# get list of users who the artist is following.
	# consider we may not want to always analyze the first 100, although it works since it should be
	# the hundred most frequent
	try:
		followings = client.get('/users/' + str(artist) + '/followings', limit=100)

		try:
			print "getFollowings: Analyzing " + id2username(artist) + "\'s " + str(len(followings)) + " followings..."
		except UnicodeError:
			print "getFollowings: Unicode Error, using artist ID: " + str(artist)
                        raise
		except NameError:
			print "getFollowings: Name error, using artist ID: " + str(artist)
                        raise
		except:
			print "getFollowings: Unexpected error:", sys.exc_info()[0]
                        raise

		return [user.id for user in followings]

	except ConnectionError, e:
		print e
		getFollowings(artist)

	except TypeError:
		print "getFollowings: Artist was not there!"
		return []

	except RuntimeError, e:
		return []

	except Exception, e:
		print 'getFollowings: Error: %s, Status Code: %d' % (e.message, e.response.status_code)
                raise

def getFollowers(artist):
	try:
		followers = client.get('/users/' + str(artist) + '/followers', limit=100)

		try:
			print "getFollowers: Analyzing " + id2username(artist) + "\'s " + str(len(followers)) + " followers..."
		except UnicodeError:
			print "getFollowers: Unicode Error, using artist ID: " + str(artist)
		except NameError:
			print "getFollowers: Name error, using artist ID: " + str(artist)
		except:
			print "getFollowers: Unexpected error:", sys.exc_info()[0]
                        raise

		return [user.id for user in followers]

	except ConnectionError, e:
		print e
		getFollowers(artist)

	except TypeError:
		print "getFollowers: Artist was not there!"
		return []

	except RuntimeError, e:
		print e
		return []

	except Exception, e:
		print 'getFollowers: Error: %s, Status Code: %d' % (e.message, e.response.status_code)
                raise


def getFavorites(artist):
	try:
		favorites = client.get('/users/' + str(artist) + '/favorites', limit=100)
		try:
			print "getFavorites: Analyzing " + id2username(artist) + "\'s " + str(len(favorites)) + " favorites..."
		except UnicodeError:
			print "getFavorites: Unicode Error, using artist ID: " + str(artist)
		except NameError:
			print "getFavorites: Name error, using artist ID: " + str(artist)
		except:
			print "getFavorites: Unexpected error:", sys.exc_info()[0]
                        raise

		return [user.id for user in favorites]

	except ConnectionError, e:
		print e
		getFavorites(artist)

	except TypeError:
		print "getFavorites: Artist was not there!"
		return []

	except RuntimeError, e:
		print e
		return []

	except Exception, e:
		print 'getFavorites: Error: %s, Status Code: %d' % (e.message, e.response.status_code)
                raise


def getComments(artist):
	try:
		comments = client.get('/users/' + str(artist) + '/comments', limit=100)
		try:
			print "getComments: Analyzing " + id2username(artist)  + "\'s " + str(len(comments)) + " comments..."
		except UnicodeError:
			print "getComments: Unicode Error, using artist ID: " + str(artist)
		except NameError:
			print "getComments: Name error, using artist ID: " + str(artist)
                        traceback.print_exc()
		except:
			print "getComments: Unexpected error:", sys.exc_info()[0]
                        raise

		return [user.id for user in comments]

	except ConnectionError, e:
		print e
		getComments(artist)

	except TypeError:
		print "getComments: Artist was not there!"
		return []

	except RuntimeError, e:
		print e
		return []

	except Exception, e:
		print 'getComments: Error: %s, Status Code: %d' % (e.message, e.response.status_code)
                raise

def getTracks(artist):
	try:
		tracks = client.get('/users/' + str(artist) + '/tracks', limit=100)

		try:
			print "getTracks: Analyzing " + id2username(artist) + "\'s " + str(len(tracks)) + " tracks..."
		except UnicodeError:
			print "getTracks: Unicode Error, using artist ID: " + str(artist)
		except NameError:
			print "getTracks: Name error, using artist ID: " + str(artist)
		except:
			print "getTracks: Unexpected error:", sys.exc_info()[0]

		return [track.id for track in tracks]

	except ConnectionError, e:
		print e
		getTracks(artist)

	except TypeError:
		print "getTracks: Artist was not there!"
		return []

	except RuntimeError, e:
		print e
		return []

	except Exception, e:
		print 'getTracks: Error: %s, Status Code: %d' % (e.message, e.response.status_code)
	 	return []

def addFollowings(artist, followings, artistGraph):
	for user in followings:
		artistGraph.add_edge(artist, user, key = 'fol_weight', weight = 1)
		print "User %s successfully added to artistGraph!" % id2username(user)


def addFollowers(artist, followers, artistGraph):
	for user in followers:
		artistGraph.add_edge(user, artist, key = 'fol_weight', weight = 1)
		print "User %s successfully added to artistGraph!" % id2username(user)

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

