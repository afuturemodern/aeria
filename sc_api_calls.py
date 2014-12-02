import sys
import soundcloud
import networkx as nx
from requests.exceptions import ConnectionError, HTTPError
from sys import getrecursionlimit, setrecursionlimit

client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

id2username_cache = {}

def id2username(artist):
	global id2username_dict
	try:
		username = id2username_cache.get(artist, None)
		if not username:
			username = str(client.get('/users/%s' % str(artist)).username.encode('utf-8'))
			id2username_cache[artist] = username
		return username
	except ConnectionError:
		print "\t"*2, "id2username(%s): could not make a connection" % artist
		return None
	except HTTPError:
		print "\t"*2, "id2username(%s): received an HTTPError" % artist
		return None
	except UnicodeError:
		print "\t"*2, "id2username(%s): unicode error in encoding username" % artist
		return None

def getFollowings(artist):
		# get list of users who the artist is following.
	# consider we may not want to always analyze the first 100, although it works since it should be
	# the hundred most frequent
	try:
		followings = client.get('/users/' + str(artist) + '/followings', limit=100)
		print "\t", "getFollowings: Analyzing " + id2username(artist) + "\'s " + str(len(followings)) + " followings..."
		return [user.id for user in followings]
	except ConnectionError, e:
		print "\t"*2, "getFollowings(%s): Connection Error" % artist
		return []
	except TypeError:
		print "\t"*2, "getFollowings(%s): Artist was not there!" % artist
		return []
	except RuntimeError, e:
		print "\t", "getFollowings(%s): Runtime Error" % artist
		return []
	except Exception, e:
		print "\t"*2, 'getFollowings(%s): Error: %s, Status Code: %d' % (artist, e.message, e.response.status_code)
		return []

def getFollowers(artist):
	try:
		followers = client.get('/users/' + str(artist) + '/followers', limit=100)
		print "\t", "getFollowers: Analyzing " + id2username(artist) + "\'s " + str(len(followers)) + " followers..."
		return [user.id for user in followers]

	except ConnectionError, e:
		print "\t"*2, "getFollowers(%s): Connection Error" % artist
		return []
	except TypeError:
		print "\t"*2, "getFollowers(%s): Artist was not there!" % artist
		return []
	except RuntimeError, e:
		print "\t"*2, "getFollowers(%s): Runtime Error" % artist
		return []
	except Exception, e:
		print "\t"*2, 'getFollowers(%s): Error: %s, Status Code: %d' % (artist, e.message, e.response.status_code)
		return []

def getFavorites(artist):
	try:
		favorites = client.get('/users/' + str(artist) + '/favorites', limit=100)
		print "\t", "getFavorites: Analyzing " + id2username(artist) + "\'s " + str(len(favorites)) + " favorites..."
		return [user.id for user in favorites]

	except ConnectionError, e:
		print "\t"*2, "getFavorites(%s): Connection Error" % artist
		return []
	except TypeError:
		print "\t"*2, "getFavorites(%s): Artist was not there!" % artist
		return []
	except RuntimeError, e:
                print "\t"*2, "getFavorites(%s): Runtime Error" % artist
		return []
	except Exception, e:
		print "\t"*2, 'getFavorites(%s): Error: %s, Status Code: %d' % (artist, e.message, e.response.status_code)
		return []

def getComments(artist):
	try:
		comments = client.get('/users/' + str(artist) + '/comments', limit=100)
		print "\t", "getComments: Analyzing " + id2username(artist)  + "\'s " + str(len(comments)) + " comments..."
		return [user.id for user in comments]

	except ConnectionError, e:
		print "\t"*2, "getComments(%s): Connection Error" % artist
		return []
	except TypeError:
		print "\t"*2, "getComments(%s): Artist was not there!" % artist
		return []
	except RuntimeError, e:
		print "\t"*2, "getComments(%s): Runtime Error" % artist
		return []
	except Exception, e:
		print "\t"*2, 'getComments(%s): Error: %s, Status Code: %d' % (artist, e.message, e.response.status_code)
		return []

def getTracks(artist):
	try:
		tracks = client.get('/users/' + str(artist) + '/tracks', limit=100)
                print "\t", "getTracks: Analyzing " + id2username(artist) + "\'s " + str(len(tracks)) + " tracks..."
		return [track.id for track in tracks]

	except ConnectionError, e:
                print "\t"*2, "getTracks(%s): Connection Error" % artist
                return []
	except TypeError:
		print "\t"*2, "getTracks(%s): Artist was not there!" % artist
		return []
	except RuntimeError, e:
                print "\t"*2, "getTracks(%s): Runtime Error" % artist
		return []
	except Exception, e:
		print "\t"*2, 'getTracks(%s): Error: %s, Status Code: %d' % (artist, e.message, e.response.status_code)
	 	return []

def addFollowings(artist, followings, artistGraph):
	for user in followings:
		artistGraph.add_edge(artist, user, key = 'fol_weight', weight = 1)
		print "Link from " + id2username(artist) + " to " + id2username(user) +" successfully added to artistGraph!" 


def addFollowers(artist, followers, artistGraph):
	for user in followers:
		artistGraph.add_edge(user, artist, key = 'fol_weight', weight = 1)
		print "Link from " + id2username(user) + " to " + id2username(artist) + " successfully added to artistGraph!"  

def addFavorites(artist, favorites, artistGraph):
	for user in favorites:
		if artistGraph.has_edge(artist, user, 'fol_weight'):
			if artistGraph.has_edge(artist, user, 'fav_weight'):
				artistGraph.add_edge(artist, user, key = 'fav_weight',
					weight = artistGraph.get_edge_data(artist, user, key = 'fav_weight')['weight'] + 1)
				print id2username(artist) + "'s favorites of " + id2username(user) + " updated in artistGraph!"
			else:
				artistGraph.add_edge(artist, user, key = 'fav_weight', weight = 1)
				print id2username(artist) + "'s favorited of " + id2username(user) + " added to artistGraph!"

def addComments(artist, comments, artistGraph):
	for user in comments:
		if artistGraph.has_edge(artist, user, 'fol_weight'):
			if artistGraph.has_edge(artist, user, 'com_weight'):
				artistGraph.add_edge(artist, user, key = 'com_weight',
					weight = artistGraph.get_edge_data(artist, user, key = 'com_weight')['weight'] + 1)
				print id2username(artist) + "'s comments to " + id2username(user) + " updated in artistGraph!"
			else:
				artistGraph.add_edge(artist, user, key = 'com_weight', weight = 1)
				print id2username(artist) + "'s comment to " + id2username(user) + " added to artistGraph!"


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
						print id2username(artist) + "'s favoriter " + id2username(user) + " updated in artistGraph!"
					else:
						artistGraph.add_edge(user, artist, key = 'fav_weight', weight = 1)
						print id2username(artist) + "'s favoriter " + id2username(user) + " added to artistGraph!"
 		except:
 			print "\t"*2, "addTracks: Unexpected error:", sys.exc_info()[0]

 		try:
 			commenters = client.get('/tracks/' + str(track) + '/comments')
 			for user in commenters:
				if artistGraph.has_edge(user, artist, 'fol_weight'):
					if artistGraph.has_edge(user, artist, 'com_weight'):
						artistGraph.add_edge(user, artist, key = 'com_weight',
							weight = artistGraph.get_edge_data(user, artist, key = 'com_weight')['weight'] + 1)
						print id2username(artist) + "'s commenter " + id2username(user) + " updated in artistGraph!"
					else:
						artistGraph.add_edge(user, artist, key = 'com_weight', weight = 1)
						print id2username(artist) + "'s commenter " + id2username(user) + " added to artistGraph!"
 		except:
 			print "\t"*2, "addTracks: Unexpected error:", sys.exc_info()[0]

