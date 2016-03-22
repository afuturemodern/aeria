import sys
import soundcloud
import networkx as nx
from py2neo import authenticate, Graph
from py2neo.packages.httpstream.http import SocketError
from requests.exceptions import ConnectionError, HTTPError
from utils import get_results, handle_http_errors
from functools import partial

client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

id2username_cache = {}

# need to navigate and set the password to "pass" for first time
authenticate("localhost:7474", "neo4j", "pass")
artistGraph = Graph("http://localhost:7474/db/data")

def getUserAttr(resource, attr):
    if hasattr(resource, 'user'): return resource.user[attr]
    if hasattr(resource, attr): return getattr(resource, attr)
    return None

getUsername = partial(getUserAttr, attr='username')
getUserid = partial(getUserAttr, attr='id')

@handle_http_errors
def id2username(profile, kind='users'):
    global id2username_dict
    username = id2username_cache.get(profile, None)
    if username is not None: return username

    # username is none, we don't have it in cache
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

@handle_http_errors
def getFollowings(profile):
    # get list of users who the artist is following.
    followings = get_results(client, '/users/{0:s}/followings/'.format(str(profile)))
    return followings

@handle_http_errors
def getFollowers(profile):
    followers = get_results(client, '/users/{0:s}/followers/'.format(str(profile)))
    return followers

@handle_http_errors
def getFavorites(profile):
    favorites = get_results(client, '/users/{0:s}/favorites/'.format(str(profile)))
    return favorites

@handle_http_errors
def getComments(profile):
    comments = get_results(client, '/users/{0:s}/comments/'.format(str(profile)))
    return comments

@handle_http_errors
def getTracks(profile):
    tracks = get_results(client, '/users/{0:s}/tracks/'.format(str(profile)))
    return tracks

def getWeight(profile, neighbor, artistNet, attr):
        if artistNet.has_edge(profile, neighbor, key=attr):
                return artistNet.get_edge_data(profile, neighbor, key=attr)['weight'] + 1
        else:
          return 1

def addWeight(action, profile, neighbor, artistNet, attr):
    new_weight = getWeight(profile, neighbor, artistNet, attr)
    artistNet.add_edge(profile, neighbor, key=attr, weight=new_weight)
    print "\t", u"{0:>15s}: {1:s} --> {2:s}".format(action, getUsername(profile), getUsername(neighbor))
    return new_weight

def addAction(action, profile, neighbor, weight):
    # relationship types cannot be dynamic (parameterized)
    query = 'CREATE (profile:Person {profile}) - [interaction:%s {weight: [{weight}]}] -> (neighbor:Person {neighbor})' % action.upper()
    try:
        artistGraph.cypher.execute(query, {'profile': {'id': getUserid(profile), 'username': getUsername(profile)}, 'weight': weight, 'neighbor': {'id': getUserid(neighbor), 'username': getUsername(neighbor)}})
    except SocketError:
        print "\t\t\t", "----Cannot connect to cypher db. Assume the query was executed successfully.----"
    return True

def addFollowings(artist, followings, artistNet):
    for user in followings:
        addAction('follows', artist, user, addWeight('follows', artist, user, artistNet, 'fol_weight'))

def addFollowers(artist, followers, artistNet):
    for user in followers:
        addAction('follows', user, artist, addWeight('follows', user, artist, artistNet, 'fol_weight'))

def addFavorites(artist, favorites, artistNet):
    for user in favorites:
        addAction('favorites', artist, user, addWeight('favorites', artist, user, artistNet, 'fav_weight'))

def addComments(artist, comments, artistNet):
    for user in comments:
        addAction('comments', artist, user, addWeight('comments', artist, user, artistNet, 'com_weight'))

def addTracks(artist, tracks, artistNet):
    for track in tracks:
    # get list of users who have favorited this user's track
        favoriters = get_results(client, '/tracks/' + str(track.id) + '/favoriters')
        for user in favoriters:
            addAction('favorites', user, artist, addWeight('favorites', user, artist, artistNet, 'fav_weight'))

    # get list of users who have commented on this user's track
        commenters = get_results(client, '/tracks/' + str(track.id) + '/comments')
        for comment in commenters:
            addAction('comments', comment, artist, addWeight('favorites', comment, artist, artistNet, 'com_weight'))
