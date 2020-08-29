import sys
import soundcloud

client = soundcloud.Client(client_id="454aeaee30d3533d6d8f448556b50f23")


def initializePR(artistGraph):
    """ Sets the initial PR value of every artist in the dictionary to 1/num_artists."""
    artists = artistGraph.nodes()
    for artist in artists:
        artistGraph.node[artist]["currPR"] = 1.0 / len(artists)
        artistGraph.node[artist]["newPR"] = 0
    return artists


def computePR(artistGraph, damping, iterations):
    """Given an artist object, damping factor, and iteration number,
    the computePR function computes the Page Rank value for that
    artist and sets the attribute."""
    artists = initializePR(artistGraph)
    i = 0
    while i < iterations:
        for artist in artists:
            for nartist in artists:
                artistGraph.node[artist]["newPR"] += (
                    artistGraph.node[nartist]["currPR"] * (1 - damping) / len(artists)
                )
                if nartist in artistGraph.predecessors(artist):
                    artistGraph.node[artist]["newPR"] += (
                        damping
                        * artistGraph.node[nartist]["currPR"]
                        / artistGraph.out_degree(nartist)
                    )
        for artist in artists:
            artistGraph.node[artist]["currPR"] = artistGraph.node[artist]["newPR"]
            artistGraph.node[artist]["newPR"] = 0
        i += 1
