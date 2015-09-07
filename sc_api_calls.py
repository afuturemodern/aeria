import sys
import soundcloud
import networkx as nx
from requests.exceptions import ConnectionError, HTTPError

from cloudreader import write_graph

client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

id2username_cache = {}

def id2username(artist):
	global id2username_dict
	try:
		username = id2username_cache.get(artist, None)
		while not username:
			username = str(client.get('/users/%s' % str(artist)).username.encode('utf-8'))
			id2username_cache[artist] = username
		return username
	except ConnectionError:
		# print "\t"*2, "id2username(%s): could not make a connection" % artist
		return None
	except HTTPError, e:
		# print "\t"*2, "id2username(%s): received an HTTPError" % artist
		return None
	except UnicodeError:
		# print "\t"*2, "id2username(%s): unicode error in encoding username" % artist
		return None

def getFollowings(artist):
	# get list of users who the artist is following.
	# consider we may not want to always analyze the first 100, although it works since it should be
	# the hundred most frequent
	print "\t", "getFollowings: Analyzing " + id2username(artist) + "\'s followings..."
        following_ids = []
	try:
               followings = client.get('/users/' + str(artist) + '/followings/', limit=100)
               # print "\t", "getFollowings: Analyzing " + id2username(artist) + "\'s " + str(len(followings)) + " followings..."
               return [user.id for user in followings]
               
	except ConnectionError:
		# print "\t"*2, "getFollowings(%s): Connection Error" % artist
		return []
	except HTTPError, e:
		return []	
	except TypeError:
		# print "\t"*2, "getFollowings(%s): Artist was not there!" % artist
		return []
	except RuntimeError, e:
		# print "\t", "getFollowings(%s): Runtime Error" % artist
		return []
	except Exception, e:
		# print "\t"*2, 'getFollowings(%s): Error: %s' % (artist, e.message)
		return []

def getFollowers(artist):
	try:
		followers = client.get('/users/' + str(artist) + '/followers', limit=100)
		# print "\t", "getFollowers: Analyzing " + id2username(artist) + "\'s " + str(len(followers)) + " followers..."
		return [user.id for user in followers]
	except ConnectionError:
		# print "\t"*2, "getFollowers(%s): Connection Error" % artist
		return []
	except HTTPError, e:
		return []	
	except TypeError:
		# print "\t"*2, "getFollowers(%s): Artist was not there!" % artist
		return []
	except RuntimeError, e:
		# print "\t"*2, "getFollowers(%s): Runtime Error" % artist
		return []
	except Exception, e:
		# print "\t"*2, 'getFollowers(%s): Error: %s, Status Code: %d' % (artist, e.message, e.response.status_code)
		return []

def getFavorites(artist):
	try:
		favorites = client.get('/users/' + str(artist) + '/favorites', limit=100)
		# print "\t", "getFavorites: Analyzing " + id2username(artist) + "\'s " + str(len(favorites)) + " favorites..."
		return [user.id for user in favorites]
	except ConnectionError:
		# print "\t"*2, "getFavorites(%s): Connection Error" % artist
		return []
	except HTTPError, e:
		return []	
	except TypeError:
		# print "\t"*2, "getFavorites(%s): Artist was not there!" % artist
		return []
	except RuntimeError, e:
                # print "\t"*2, "getFavorites(%s): Runtime Error" % artist
		return []
	except Exception, e:
		# print "\t"*2, 'getFavorites(%s): Error: %s, Status Code: %d' % (artist, e.message, e.response.status_code)
		return []

def getComments(artist):
	try:
		comments = client.get('/users/' + str(artist) + '/comments', limit=100)
		# print "\t", "getComments: Analyzing " + id2username(artist)  + "\'s " + str(len(comments)) + " comments..."
		return [user.id for user in comments]
	except ConnectionError:
		# print "\t"*2, "getComments(%s): Connection Error" % artist
		return []
	except HTTPError, e:
		return []	
	except TypeError:
		# print "\t"*2, "getComments(%s): Artist was not there!" % artist
		return []
	except RuntimeError, e:
		# print "\t"*2, "getComments(%s): Runtime Error" % artist
		return []
	except Exception, e:
		# print "\t"*2, 'getComments(%s): Error: %s, Status Code: %d' % (artist, e.message, e.response.status_code)
		return []

def getTracks(artist):
	try:
		tracks = client.get('/users/' + str(artist) + '/tracks', limit=100)
                # print "\t", "getTracks: Analyzing " + id2username(artist) + "\'s " + str(len(tracks)) + " tracks..."
		return [track.id for track in tracks]
	except ConnectionError:
		# print "\t"*2, "getTracks(%s): Connection Error" % artist
		return []
	except HTTPError, e:
		return []	
	except TypeError:
		# print "\t"*2, "getTracks(%s): Artist was not there!" % artist
		return []
	except RuntimeError, e:
                # print "\t"*2, "getTracks(%s): Runtime Error" % artist
		return []
	except Exception, e:
		# print "\t"*2, 'getTracks(%s): Error: %s, Status Code: %d' % (artist, e.message, e.response.status_code)
	 	return []

def getWeight(artist, user, artistGraph, attr):
        if artistGraph.has_edge(artist, user, key=attr):
                return artistGraph.get_edge_data(artist, user, key=attr)['weight'] + 1
        else:
          return 1

def addWeight(artist, user, artistGraph, attr):
	new_weight = getWeight(artist, user, artistGraph, attr)
	artistGraph.add_edge(artist, user, key=attr, weight=new_weight)
	print "\t", "%s --> %s" % (id2username(artist), id2username(user)) 

def addFollowings(artist, followings, artistGraph):
	print "Adding followings for %s" % (id2username(artist))
	for user in followings:
		addWeight(user, artist, artistGraph, 'fol_weight')
        # write_graph(artistGraph, 'artistGraph.net')

def addFollowers(artist, followers, artistGraph):
	print "Adding followers for %s" % (id2username(artist))
	for user in followers:
		addWeight(artist, user, artistGraph, 'fol_weight')
        # write_graph(artistGraph, 'artistGraph.net')

def addFavorites(artist, favorites, artistGraph):
	print "Adding favorites for %s" % (id2username(artist))
	for user in favorites:
		addWeight(artist, user, artistGraph, 'fav_weight')
        # write_graph(artistGraph, 'artistGraph.net')

def addComments(artist, comments, artistGraph):
	print "Adding comments for %s" % (id2username(artist))
	for user in comments:
		addWeight(artist, user, artistGraph, 'com_weight')
        # write_graph(artistGraph, 'artistGraph.net')

def addTracks(artist, tracks, artistGraph):
	for track in tracks:
	# get list of users who have favorited this user's track
		favoriters = client.get('/tracks/' + str(track) + '/favoriters')
		print "Adding favoriters for %s" % (id2username(artist))
		for user in favoriters:
			addWeight(user.id, artist, artistGraph, 'fav_weight')
	
                # write_graph(artistGraph, 'artistGraph.net')

	# get list of users who have commented on this user's track			
		commenters = client.get('/tracks/' + str(track) + '/comments')
		print "Add Commenters"
		for user in commenters:
			addWeight(user.user_id, artist, artistGraph, 'com_weight')
                # write_graph(artistGraph, 'artistGraph.net')

