for artist in artistGraph.nodes():
	if artist:
		try:
			username = scac.id2username(artist)
			followings = artistGraph.successors(artist)
			followers = artistGraph.predecessors(artist)
			try:	
				print "\t", username + " has " + str(len(followings)) + " followings"
				print "\t", username + " follows " + ", ".join(map(lambda x: scac.id2username(x), followings))
			except TypeError: 
				print "No followings home!"	
			try:	
				print "\t", username + " has " + str(len(followers)) + " followers"
				print "\t", username + " is followed by " + ", ".join(map(lambda x: scac.id2username(x), followers))
			except TypeError:
				print "No followers home!"
			print "-"*40
		except UnicodeError:
			print "Artist's username not found"	