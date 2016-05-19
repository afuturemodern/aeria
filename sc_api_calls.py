import sys
import soundcloud
import networkx as nx
from py2neo import authenticate, Node, Relationship, Graph
from py2neo.packages.httpstream.http import SocketError
from requests.exceptions import ConnectionError, HTTPError
from utils import get_results, handle_http_errors
from functools import partial

client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

id2username_cache = {}

# need to navigate and set the password to "pass" for first time
authenticate("localhost:7474", "neo4j", "cloudchaser")
userGraph = Graph()

userGraph.delete_all()

def getUserAttr(resource, attr):
#   if hasattr(resource, 'user'): return resource.user[attr]
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

def getTrackInfo(track):
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

def getUserFavInfo(fav):
    info = ['id', #as 'track_id',
            'user_id',
            'last_modified'
#           'user'
           ]
    return {i: getUserAttr(fav, i) for i in info}

def getTrackFavInfo(fav):
    info = ['id', # as 'user_id',
            'username',
            'last_modified'
           ]
    return {i: getUserAttr(fav, i) for i in info}

def getUserCommInfo(comm):
    info = ['id',
            'user_id',
            'track_id',
            'timestamp'
        ]
    return {i: getUserAttr(comm, i) for i in info}

def getTrackCommInfo(comm):
    info = ['id',
            'user_id',
            'track_id',
            'timestamp'
#           'user'
          ]
    return {i: getUserAttr(comm, i) for i in info}

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

def addNode(profile):
    query = ('MERGE (profile:soundcloud {id: {profile}.id}) \
            ON CREATE SET profile={profile} ')
    try:
        userGraph.cypher.execute(query, {'profile': getUserInfo(profile)})
    except SocketError:
        print "\t\t\t", "----Cannot connect to cypher db. Assume the query was executed successfully.----"
    return True


def addPair(profile, neighbor):
    try:
        addNode(profile)
        addNode(neighbor)
    except:
        print "\t\t\t", "----Cannot connect to cypher db. Assume the query was executed successfully.----"
    return True

def addFollow(profile, neighbor):
    query = ('MERGE (profile:soundcloud {id: {profile}.id}) \
            ON CREATE SET profile={profile} '
            'MERGE (neighbor:soundcloud {id: {neighbor}.id}) \
            ON CREATE SET neighbor={neighbor} '
            'MERGE (profile)-[r:follows]->(neighbor)')
    if profile is not None and neighbor is not None:
        profile_info = getUserInfo(profile)
        neighbor_info = getUserInfo(neighbor)
        try:
            userGraph.cypher.execute(query, {'profile': profile_info,
                                        'neighbor': neighbor_info})
            if profile_info['username'] and neighbor_info['username']:
                print profile_info['username'] + " follows " + neighbor_info['username']
        except SocketError:
            print "\t\t\t", "----Cannot connect to cypher db. Assume the query was executed successfully.----"
    if profile is None:
        print "Profile not found."
    if neighbor is None:
        print "Neighbor not found."
    return True

def addUserFav(profile, favorite):#, track):
    query = ('MERGE (profile:soundcloud {id: {profile}.id}) \
            ON CREATE SET profile={profile} '
            'MERGE (favorite:soundcloud {id: {favorite}.user_id}) \
            ON CREATE SET favorite={favorite} '   
            'MERGE (profile)-[r:favorites]->(favorite)')
            # Create new favorite relationship if it dne
            # If so, append the new track to the relationship property
       #     'MERGE (profile)-[r:favorites]->(neighbor) ON CREATE SET r.track_ids  = [{track}] \
       #     ON MATCH SET r.track_ids  = \
       #     CASE WHEN {track} NOT IN r.track_ids \
       #         THEN r.track_ids + [{track}] \
       #         ELSE r.track_ids \
       #     END')
    if profile is not None and favorite is not None:
        profile_info = getUserInfo(profile)
        fav_info = getUserFavInfo(favorite)
        try:
            userGraph.cypher.execute(query, {'profile': profile_info,
    #                                   'track': track,
                                        'favorite': fav_info})
        #    if Relationship.exists(profile, "favorites", neighbor):
        #        Relationship(profile, "favorites", neighbor)['track_ids'] += [track]
        #    else:
        #        userGraph.create_unique(Relationship(profile, "favorites", neighbor, track_ids = [track]))
            if profile_info['username'] and fav_info['user_id']:
                try:
                    print profile_info['username'] + " favorites " + id2username(fav_info['user_id'])
                except UnicodeDecodeError:
                    print profile_info['username'] + " favorites " + str(fav_info['user_id'])
                except TypeError:
                    print "User favorite not printed due to Type Error."
        except SocketError:
            print "\t\t\t", "----Cannot connect to cypher db. Assume the query was executed successfully.----"
    if profile is None:
        print "Profile not found"
    if favorite is None:
        print "Favorite not found"
    return True
    #Use SET to update properties

def addUserComm(profile, comment):#, comment):
    query = ('MERGE (profile:soundcloud {id: {profile}.id}) \
            ON CREATE SET profile={profile} '
            'MERGE (comment:soundcloud {id: {comment}.user_id}) \
            ON CREATE SET comment={comment} '   
            'MERGE (profile)-[r:comments]->(comment)')
            # Create new comment relationship if it dne
            # Append new comment to property if relationship already exists
       #     'MERGE (profile)-[r:comments]->(comment) ON CREATE SET r.comment_ids = [{comment}] \
       #     ON MATCH SET r.coment_ids = \
       #     CASE WHEN {comment} NOT IN r.comment_ids \
       #         THEN r.comment_ids + [{comment}] \
       #         ELSE r.comment_ids \
       #     END')
    if profile is not None and comment is not None:
        profile_info = getUserInfo(profile)
        comm_info = getUserCommInfo(comment)
        try:
            userGraph.cypher.execute(query, {'profile': profile_info,
                                            #'track': track,
                                            'comment': comm_info})
           # if Relationship.exists(profile, "comments", neighbor):
           #     Relationship(profile, "comments", neighbor)['comment_ids'] += [comment]
           # else:
           #     userGraph.create_unique(Relationship(profile, "comments", neighbor, track_ids = [track]))
            if profile_info['username'] and comm_info['user_id']:
                try:
                    print profile_info['username'] + " comments " + id2username(comm_info['user_id'])
                except UnicodeDecodeError or TypeError:
                    print profile_info['username'] + " favorites " + str(comm_info['user_id'])
        except SocketError:
            print "\t\t\t", "----Cannot connect to cypher db. Assume the query was executed successfully.----"
    if profile is None:
        print "Profile not found"
    if comment is None:
        print "Comment not found"
    return True

def addTrackFav(favoriter, profile):#, track):
    query = ('MERGE (profile:soundcloud {id: {profile}.id}) \
            ON CREATE SET profile={profile} '
            'MERGE (favoriter:soundcloud {id: {favoriter}.id}) \
            ON CREATE SET favoriter={favoriter} '    
            'MERGE (favoriter)-[r:favorites]->(profile)')
            # Create new favorite relationship if it dne
            # If so, append the new track to the relationship property
       #     'MERGE (profile)-[r:favorites]->(neighbor) ON CREATE SET r.track_ids  = [{track}] \
       #     ON MATCH SET r.track_ids  = \
       #     CASE WHEN {track} NOT IN r.track_ids \
       #         THEN r.track_ids + [{track}] \
       #         ELSE r.track_ids \
       #     END')
    if favoriter is not None and profile is not None:
        profile_info = getUserInfo(profile)
        fav_info = getTrackFavInfo(favoriter)
        try:
            userGraph.cypher.execute(query, {'profile': profile_info,
        #                                   'track': track,
                                            'favoriter': fav_info})
        #    if Relationship.exists(profile, "favorites", neighbor):
        #        Relationship(profile, "favorites", neighbor)['track_ids'] += [track]
        #    else:
        #        userGraph.create_unique(Relationship(profile, "favorites", neighbor, track_ids = [track]))
            if profile_info['username'] and fav_info['username']:
                print fav_info['username'] + " favorites " + profile_info['username']
        except SocketError:
            print "\t\t\t", "----Cannot connect to cypher db. Assume the query was executed successfully.----"
        except AttributeError:  
            print "Track favorite add failed due to semantic error."
    if favoriter is None:
        print "Favoriter not found"
    if profile is None:
        print "Profile not found"
    return True
    #Use SET to update properties

def addTrackComm(commenter, profile):#, comment):
    query = ('MERGE (profile:soundcloud {id: {profile}.id}) \
            ON CREATE SET profile={profile} '
            'MERGE (commenter:soundcloud {id: {commenter}.user_id}) \
            ON CREATE SET commenter={commenter} '   
            'MERGE (commenter)-[r:comments]->(profile)')
            # Create new comment relationship if it dne
            # Append new comment to property if relationship already exists
       #     'MERGE (profile)-[r:comment]->(neighbor) ON CREATE SET r.comment_ids = [{comment}] \
       #     ON MATCH SET r.coment_ids = \
       #     CASE WHEN {comment} NOT IN r.comment_ids \
       #         THEN r.comment_ids + [{comment}] \
       #         ELSE r.comment_ids \
       #     END')
    if commenter is not None and profile is not None:
        profile_info = getUserInfo(profile)
        comm_info = getTrackCommInfo(commenter)
        try:
            userGraph.cypher.execute(query, {'profile': profile_info,
                                            #'track': track,
                                            'commenter': comm_info})
           # if Relationship.exists(profile, "comments", neighbor):
           #    Relationship(profile, "comments", neighbor)['comment_ids'] += [comment]
           # else:
           #    userGraph.create_unique(Relationship(profile, "comments", neighbor, track_ids = [track]))
            if profile_info['username'] and comm_info['user_id']:
                try:
                    print id2username(comm_info['user_id']) + " comments  " + profile_info['username']
                except UnicodeDecodeError or TypeError:
                    print str(comm_info['user_id']) + " comments  " + profile_info['username']
        except SocketError:
            print "\t\t\t", "----Cannot connect to cypher db. Assume the query was executed successfully.----"
        except AttributeError:  
            print "Track comment add failed due to semantic error."
    if commenter is None:
        print "Commenter not found"
    if profile is None:
        print "Profile not found"
    return True

def addFollowings(profile, followings): #, profileGraph):
    for follow in followings:
        addFollow(profile, follow)
#       addAction('follows', artist, user, addWeight('follows', artist, user, profileGraph, 'fol_weight'))

def addFollowers(profile, followers): #, profileGraph):
    for follow in followers:
        addFollow(follow, profile)
#       addAction('follows', user, artist, addWeight('follows', user, artist, profileGraph, 'fol_weight'))

def addFavorites(profile, favorites): #, profileGraph):
    for favorite in favorites:
        addUserFav(profile, favorite) #, favorite.id)
#       addAction('favorites', artist, user, addWeight('favorites', artist, user, profileGraph, 'fav_weight'))

def addComments(profile, comments): #, profileGraph):
    for comment in comments:
        addUserComm(profile, comment) #, comment.id)
#       addAction('comments', artist, user, addWeight('comments', artist, user, profileGraph, 'com_weight'))

def addTracks(profile, tracks): #, profileGraph):
    for track in tracks:
    # get list of users who have favorited this user's track
        try:
            favoriters = get_results(client, '/tracks/' + str(track.id) + '/favoriters')
            for favoriter in favoriters:
                addTrackFav(favoriter, profile) #, track.id)
#               addAction('favorites', user, artist, addWeight('favorites', user, artist, profileGraph, 'fav_weight'))

        # get list of users who have commented on this user's track
            commenters = get_results(client, '/tracks/' + str(track.id) + '/comments')
            for commenter in commenters:
                addTrackComm(commenter, profile) #, commenter.id)
#               addAction('comments', user, artist, addWeight('comments', comment, artist, profileGraph, 'com_weight'))
        except HTTPError:
            print "Track not processed due to HTTP error."
