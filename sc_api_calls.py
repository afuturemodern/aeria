import sys
import soundcloud
import networkx as nx
from requests.exceptions import ConnectionError, HTTPError

# from cloudreader import write_graph
from clouder import post_to_cloud
client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

id2username_cache = {}

def id2username(profile):
	global id2username_dict
	try:
		username = id2username_cache.get(profile, None)
		while not username:
			username = str(client.get('/users/%s' % str(profile)).username.encode('utf-8'))
			id2username_cache[profile] = username
		return username
	except ConnectionError:
		print "\t"*2, "id2username(%s): could not make a connection" % profile
		return None
	except HTTPError, e:
		print "\t"*2, "id2username(%s): received an HTTPError" % profile
		return None
	except UnicodeError:
		print "\t"*2, "id2username(%s): unicode error in encoding username" % profile
		return None

def getFollowings(profile):
	# get list of users who the artist is following.
	# consider we may not want to always analyze the first 100, although it works since it should be
	# the hundred most frequent
	try:
               followings = client.get('/users/' + str(profile) + '/followings/', limit=100)
               print "\t", "getFollowings: Analyzing " + id2username(profile) + "\'s " + str(len(followings)) + " followings..."
               return [user.id for user in followings]
               
	except ConnectionError:
		print "\t"*2, "getFollowings(%s): Connection Error" % profile
		return []
	except HTTPError, e:
		return []	
	except TypeError:
		print "\t"*2, "getFollowings(%s): Artist was not there!" % profile
		return []
	except RuntimeError, e:
		print "\t", "getFollowings(%s): Runtime Error" % profile
		return []
	except Exception, e:
		print "\t"*2, 'getFollowings(%s): Error: %s' % (profile, e.message)
		return []

def getFollowers(profile):
	try:
		followers = client.get('/users/' + str(profile) + '/followers', limit=100)
		print "\t", "getFollowers: Analyzing " + id2username(profile) + "\'s " + str(len(followers)) + " followers..."
		return [user.id for user in followers]
	except ConnectionError:
		print "\t"*2, "getFollowers(%s): Connection Error" % profile
		return []
	except HTTPError, e:
		return []	
	except TypeError:
		print "\t"*2, "getFollowers(%s): Artist was not there!" % profile
		return []
	except RuntimeError, e:
		print "\t"*2, "getFollowers(%s): Runtime Error" % profile
		return []
	except Exception, e:
		print "\t"*2, 'getFollowers(%s): Error: %s, Status Code: %d' % (profile, e.message, e.response.status_code)

		return []

def getFavorites(profile):
	try:
		favorites = client.get('/users/' + str(profile) + '/favorites', limit=100)
		print "\t", "getFavorites: Analyzing " + id2username(profile) + "\'s " + str(len(favorites)) + " favorites..."
		return [user.id for user in favorites]
	except ConnectionError:
		print "\t"*2, "getFavorites(%s): Connection Error" % profile
		return []
	except HTTPError, e:
		return []	
	except TypeError:
		print "\t"*2, "getFavorites(%s): Artist was not there!" % profile 
		return []
	except RuntimeError, e:
                print "\t"*2, "getFavorites(%s): Runtime Error" % profile 
		return []
	except Exception, e:
		print "\t"*2, 'getFavorites(%s): Error: %s, Status Code: %d' % (profile, e.message, e.response.status_code)
		return []

def getComments(profile):
	try:
		comments = client.get('/users/' + str(profile) + '/comments', limit=100)
		print "\t", "getComments: Analyzing " + id2username(profile)  + "\'s " + str(len(comments)) + " comments..."
		return [user.id for user in comments]
	except ConnectionError:
		print "\t"*2, "getComments(%s): Connection Error" % profile
		return []
	except HTTPError, e:
		return []	
	except TypeError:
		print "\t"*2, "getComments(%s): Artist was not there!" % profile
		return []
	except RuntimeError, e:
		print "\t"*2, "getComments(%s): Runtime Error" % profile
		return []
	except Exception, e:
		print "\t"*2, 'getComments(%s): Error: %s, Status Code: %d' % (profile, e.message, e.response.status_code)
		return []

def getTracks(profile):
	try:
		tracks = client.get('/users/' + str(profile) + '/tracks', limit=100)
                print "\t", "getTracks: Analyzing " + id2username(profile) + "\'s " + str(len(tracks)) + " tracks..."
		return [track.id for track in tracks]
	except ConnectionError:
		print "\t"*2, "getTracks(%s): Connection Error" % profile
		return []
	except HTTPError, e:
		return []	
	except TypeError:
		print "\t"*2, "getTracks(%s): Artist was not there!" % profile
		return []
	except RuntimeError, e:
                print "\t"*2, "getTracks(%s): Runtime Error" % profile
		return []
	except Exception, e:
		print "\t"*2, 'getTracks(%s): Error: %s, Status Code: %d' % (profile, e.message, e.response.status_code)
	 	return []

def getWeight(profile, neighbor, artistGraph, attr):
        if artistGraph.has_edge(profile, neighbor, key=attr):
                return artistGraph.get_edge_data(profile, neighbor, key=attr)['weight'] + 1
        else:
          return 1

def addWeight(profile, neighbor, artistGraph, attr):
	new_weight = getWeight(profile, neighbor, artistGraph, attr)
	artistGraph.add_edge(profile, neighbor, key=attr, weight=new_weight)
	print "\t", "%s --> %s" % (id2username(profile), id2username(neighbor)) 

def addFollowings(artist, followings, artistGraph):
	print "Adding followings for %s" % (id2username(artist))
	for user in followings:
		addWeight(artist, user, artistGraph, 'fol_weight')
        # write_graph(artistGraph, 'artistGraph.net')
        # print "Posting artistGraph to cloud."
        # post_to_cloud(artistGraph)
        # print "artistGraph posted!"

def addFollowers(artist, followers, artistGraph):
	print "Adding followers for %s" % (id2username(artist))
	for user in followers:
		addWeight(user, artist, artistGraph, 'fol_weight')
        # write_graph(artistGraph, 'artistGraph.net')
        # print "Posting artistGraph to cloud."
        # post_to_cloud(artistGraph)
        # print "artistGraph posted!"

def addFavorites(artist, favorites, artistGraph):
	print "Adding favorites for %s" % (id2username(artist))
	for user in favorites:
		addWeight(artist, user, artistGraph, 'fav_weight')
        # write_graph(artistGraph, 'artistGraph.net')
        # print "Posting artistGraph to cloud."
        # post_to_cloud(artistGraph)
        # print "artistGraph posted!"

def addComments(artist, comments, artistGraph):
	print "Adding comments for %s" % (id2username(artist))
	for user in comments:
		addWeight(artist, user, artistGraph, 'com_weight')
        # write_graph(artistGraph, 'artistGraph.net')
        # print "Posting artistGraph to cloud."
        # post_to_cloud(artistGraph)
        # print "artistGraph posted!"

def addTracks(artist, tracks, artistGraph):
	for track in tracks:
	# get list of users who have favorited this user's track
		favoriters = client.get('/tracks/' + str(track) + '/favoriters')
		print "Adding favoriters for %s" % (id2username(artist))
		for user in favoriters:
			addWeight(user.id, artist, artistGraph, 'fav_weight')
	
                # write_graph(artistGraph, 'artistGraph.net')
                # print "Posting artistGraph to cloud."
                # post_to_cloud(artistGraph)
                # print "artistGraph posted!"

	# get list of users who have commented on this user's track			
		commenters = client.get('/tracks/' + str(track) + '/comments')
		print "Add Commenters"
		for user in commenters:
			addWeight(user.id, artist, artistGraph, 'com_weight')
                # write_graph(artistGraph, 'artistGraph.net')
                # print "Posting artistGraph to cloud."
                # post_to_cloud(artistGraph)
                # print "artistGraph posted!"

