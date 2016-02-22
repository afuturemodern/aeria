import sys
import soundcloud
import networkx as nx
from py2neo import Graph
from requests.exceptions import ConnectionError, HTTPError

client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

id2username_cache = {}
artistGraph = Graph()

def id2username(profile, kind='users'):
	global id2username_dict
	try:
		username = id2username_cache.get(profile, None)
		while not username:
			result = client.get('/%s/%s' % (kind, str(profile)))
                        if kind == 'comments':
                            username = result.user['username']
                        elif kind == 'tracks':
                            username = result.title
                        else:
                            username = result.username
                        # encode it correctly
                        username = str(username.encode('utf-8'))
			id2username_cache[profile] = username
		return username
	except ConnectionError:
		print "\t"*2, "id2username(%s): could not make a connection" % profile
		return None
	except HTTPError, e:
		print "\t"*2, "id2username(%s): received an HTTPError" % profile
                print str(e)
                return None
	except UnicodeError:
		print "\t"*2, "id2username(%s): unicode error in encoding username" % profile
		return None

# let's return tracks via a generator instead...
def get_results(client, url, page_size=100):
    
    def get_next_results(results=None):
        if results is None:
            return client.get(url, order='created_at', limit=page_size, linked_partitioning=1)
        next_href = getattr(results, 'next_href', None)
        if next_href is None: 
            return None
        else: 
            return client.get(next_href)

    def yield_results():
        # start results
        results = get_next_results(None)
        while results is not None:
            for result in getattr(results, 'collection', []):
                yield result
            results = get_next_results(results)

    return yield_results()

def getFollowings(profile):
	# get list of users who the artist is following.
	try:
               followings = get_results(client, '/users/' + str(profile) + '/followings/')
               print "\t", "getFollowings: Analyzing " + id2username(profile) + "\'s " + str(len(followings)) + " followings..."
               return followings 

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
                followers = get_results(client, '/users/' + str(profile) + '/followers/')
		print "\t", "getFollowers: Analyzing " + id2username(profile) + "\'s " + str(len(followers)) + " followers..."
		return followers
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
		favorites = get_results('/users/' + str(profile) + '/favorites')
		print "\t", "getFavorites: Analyzing " + id2username(profile) + "\'s " + str(len(favorites)) + " favorites..."
		return favorites 
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
		comments = get_results('/users/' + str(profile) + '/comments')
		print "\t", "getComments: Analyzing " + id2username(profile)  + "\'s " + str(len(comments)) + " comments..."
		return [comment.user['id'] for comment in comments]
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
		tracks = get_results('/users/' + str(profile) + '/tracks')
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
                raise
		print "\t"*2, 'getTracks(%s): Error: %s, Status Code: %d' % (profile, e.message, e.response.status_code)
	 	return []

def getWeight(profile, neighbor, artistNet, attr):
        if artistNet.has_edge(profile, neighbor, key=attr):
                return artistNet.get_edge_data(profile, neighbor, key=attr)['weight'] + 1
        else:
          return 1

def addWeight(profile, neighbor, artistNet, attr):
	new_weight = getWeight(profile, neighbor, artistNet, attr)
	artistNet.add_edge(profile, neighbor, key=attr, weight=new_weight)
	print "\t", "%s --> %s" % (id2username(profile), id2username(neighbor))
        return new_weight

def addAction(action, profile, neighbor, weight):
        query = '(profile {username: {username} } ) - [interaction : {action} { weight: [ {weight} ] } ] -> (neighbor {username: {neighbor} } )' 
        artistGraph.cypher.execute(query, {'username': id2username(profile), 'action': action, 'neighbor': id2username(neighbor), 'weight': weight})

def addFollowings(artist, followings, artistNet):
	print "Adding followings for %s" % (id2username(artist))
	for user in followings:
                addAction(follows, artist, user, addWeight(artist, user, artistNet, 'fol_weight'))

def addFollowers(artist, followers, artistNet):
	print "Adding followers for %s" % (id2username(artist))
	for user in followers:
                addAction(follows, user, artist, addWeight(user, artist, artistNet, 'fol_weight'))

def addFavorites(artist, favorites, artistNet):
	print "Adding favorites for %s" % (id2username(artist))
	for user in favorites:
		addAction(favorites, artist, user, addWeight(artist, user, artistNet, 'fav_weight'))

def addComments(artist, comments, artistNet):
	print "Adding comments for %s" % (id2username(artist))
	for user in comments:
		addAction(comments, artist, user, addWeight(artist, user, artistNet, 'com_weight'))

def addTracks(artist, tracks, artistNet):
	for track in tracks:
	# get list of users who have favorited this user's track
		favoriters = get_results('/tracks/' + str(track) + '/favoriters')
		print "Adding favoriters for %s" % (id2username(artist))
		for user in favoriters:
			addAction(favorites, user.id, artist, addWeight(user.id, artist, artistNet, 'fav_weight'))

	# get list of users who have commented on this user's track
		commenters = get_results('/tracks/' + str(track) + '/comments')
		print "Adding commenters for %s" % (id2username(artist))
		for comment in commenters:
			addAction(comments, comment.user['id'], artist, addWeight(comment.user['id'], artist, artistNet, 'com_weight'))

