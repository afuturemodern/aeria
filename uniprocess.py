			newFollowings = scac.getFollowings(artist)
			print "New followings: " + ", ".join([scac.id2username(user) for user in newFollowings])
			scac.addFollowings(artist, newFollowings, artistGraph)
			artists_to_enqueue.extend(newFollowings)

			newFollowers = scac.getFollowers(artist)
			print "New followers: " + ", ".join([scac.id2username(user) for user in newFollowers])
			scac.addFollowers(artist, newFollowers, artistGraph)
			artists_to_enqueue.extend(newFollowers)

			newFavorites = scac.getFavorites(artist)
			print "New Favorites: " + ", ".join([scac.id2username(user) for user in newFavorites])
			scac.addFavorites(artist, newFavorites, artistGraph)
			artists_to_enqueue.extend(newFavorites)

			newComments = scac.getComments(artist)
			print "New Comments: " + ", ".join([scac.id2username(user) for user in newComments])
			scac.addComments(artist, newComments, artistGraph)
			artists_to_enqueue.extend(newComments)	

			newTracks = scac.getTracks(artist)
			print "New Tracks: " + ", ".join([scac.id2username(user) for user in newTracks])
			scac.addTracks(artist, newTracks, artistGraph)
			artists_to_enqueue.extend(newTracks)	

			else:
				print "\t", "Artist ID %s is not query-able" % artist
				unavailable_artists.append(artist)


