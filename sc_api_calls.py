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
userGraph = Graph("http://localhost:7474/db/data")

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

def getRelationships(profile, client, url): return get_results(client, url)

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

def getUserInfo(profile):
    info = ['id',
            'permalink',
            'username',
            'avatar_url',
            'country',
            'city',
            'website',
            'track_count',
            'followers_count',
            'followings_count'
            ]
    return {i: getUserAttr(profile, i) for i in info}

getTrackInfo(track):
    info = ['id',
            'user_id',
            'created_at',
            'streamabale',
            'downloadable',
            'playback_count',
            'download_count',
            'favoritings_count',
            'comment_count'
            ]
    return {i: getUserAttr(track, i) for i in info}

#def getWeight(profile, neighbor, profileGraph, attr):
#        if profileGraph.has_edge(profile, neighbor, key=attr):
#                return profileGraph.get_edge_data(profile, neighbor, key=attr)['weight'] + 1
#        else:
#          return 1

#def addWeight(action, profile, neighbor, profileGraph, attr):
#    new_weight = getWeight(profile, neighbor, profileGraph, attr)
#    profileGraph.add_edge(profile, neighbor, key=attr, weight=new_weight)
#    print "\t", u"{0:>15s}: {1:s} --> {2:s}".format(action, getUsername(profile), getUsername(neighbor))
#    return new_weight

def addAction(action, profile, neighbor, weight):
    # relationship types cannot be dynamic (parameterized)
    query = ('MERGE (profile:soundcloud  {id: {profile}.id}) 
            ON CREATE SET profile={profile} '
             'MERGE (neighbor:soundcloud {id: {neighbor}.id}) 
            ON CREATE SET neighbor={neighbor} '
             'MERGE (profile)-[r:%s {id: {interaction}.id}]->(neighbor) 
            ON CREATE SET interaction={interaction}' 
            % action.upper())
    try:
        userGraph.cypher.execute(query, {'profile': getUserInfo(profile),
                                           'interaction': {'id': 0, 'weight': weight},
                                           'neighbor': getUserInfo(neighbor)})
    except SocketError:
        print "\t\t\t", "----Cannot connect to cypher db. Assume the query was executed successfully.----"
    return True

def addPair(profile, neighbor):
    query = ('MERGE (profile:soundcloud {id: {profile}.id})
            ON CREATE SET profile={profile} '
            'MERGE (neighbor:soundcloud {id: {neighbor}.id})
            ON CREATE SET neighbor={neighbor} ')
    try:
         artistGraph.cypher.execute(query, {'profile': getUserInfo(profile),'neighbor': getUserInfo(neighbor)})
    except:
        print "\t\t\t", "----Cannot connect to cypher db. Assume the query was executed successfully.----"
    return True

def addFollow(profile, neighbor):
    query = ('MERGE (profile:soundcloud {id: {profile}.id})
            ON CREATE SET profile={profile} '
            'MERGE (neighbor:soundcloud {id: {neighbor}.id})
            ON CREATE SET neighbor={neighbor} '
            'MERGE (profile)-[r:follows]->(neighbor)')
    try:
        artistGraph.cypher.execute(query, {'profile': getUserInfo(profile),
                                        'neighbor': getUserInfo(neighbor)})
    except SocketError:
        print "\t\t\t", "----Cannot connect to cypher db. Assume the query was executed successfully.----"
    return True


def addFav(profile, neighbor, track):
    query = ('MERGE (profile:soundcloud {id: {profile}.id})
            ON CREATE SET profile={profile} '
            'MERGE (neighbor:soundcloud {id: {neighbor}.user_id})
            ON CREATE SET neighbor={neighbor} '
            'MERGE (profile)-[r:favorites]->(neighbor) ON CREATE SET r.track_ids  = [{track}]
            ON MATCH SET r.track_ids  =
            CASE WHEN {track} NOT IN r.track_ids
                THEN r.track_ids + [{track}]
                ELSE r.track_ids
            END')
    try:
        artistGraph.cypher.execute(query, 'profile': getUserInfo(profile),
                                        'track': track,
                                        'neighbor': neighbor)
    except SocketError:
        print "\t\t\t", "----Cannot connect to cypher db. Assume the query was executed successfully.----"
    return True
    #Use SET to update properties

def addComment(profile, neighbor, comment):
    query = ('MERGE (profile:soundcloud {id: {profile}.id})
            ON CREATE SET profile={profile} '
            'MERGE (neighbor:soundcloud {id: {neighbor}.user_id})
            ON CREATE SET neighbor={neighbor} '
            'MERGE (profile)-[r:comment]->(neighbor) ON CREATE SET r.comment_ids = [{comment}]
            ON MATCH SET r.coment_ids =
            CASE WHEN {comment} NOT IN r.comment_ids
                THEN r.comment_ids + [{comment}]
                ELSE r.comment_ids
            END')
    try:
        artistGraph.cypher.execute(query, 'profile': getUserInfo(profile),
                                        'track': track,
                                        'neighbor': neighbor)
    except:
        print "\t\t\t", "----Cannot connect to cypher db. Assume the query was executed successfully.----"    
    return True

def addFollowings(profile, followings) #, profileGraph):
    for follow in followings:
        addFollow(profile, follow)
#       addAction('follows', artist, user, addWeight('follows', artist, user, profileGraph, 'fol_weight'))

def addFollowers(profile, followers) #, profileGraph):
    for follow in followers:
        addFollow(follow, profile)
#       addAction('follows', user, artist, addWeight('follows', user, artist, profileGraph, 'fol_weight'))

def addFavorites(profile, favorites) #, profileGraph):
    for favorite in favorites:
        addFav(profile, favorite, favorite.id)
#       addAction('favorites', artist, user, addWeight('favorites', artist, user, profileGraph, 'fav_weight'))

def addComments(artist, comments) #, profileGraph):
    for comment in comments:
        addComment(artist, comment, comment.id)
#       addAction('comments', artist, user, addWeight('comments', artist, user, profileGraph, 'com_weight'))

def addTracks(profile, tracks) #, profileGraph):
    for track in tracks:
    # get list of users who have favorited this user's track
        favoriters = get_results(client, '/tracks/' + str(track.id) + '/favoriters')
        for favoriter in favoriters:
            addFav(favoriter.user, profile, track.id)
#           addAction('favorites', user, artist, addWeight('favorites', user, artist, profileGraph, 'fav_weight'))

    # get list of users who have commented on this user's track
        commenters = get_results(client, '/tracks/' + str(track.id) + '/comments')
        for commenter in commenters:
            addComment(commenter.user, profile, commenter.id)
#           addAction('comments', user, artist, addWeight('comments', comment, artist, profileGraph, 'com_weight'))
