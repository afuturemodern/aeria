import sys
import networkx as nx
import soundcloud
import sc_api_calls as scac


def print_graph(G):
    for artist in G.nodes():
        if artist:
            try:
                username = scac.id2username(artist)
                followings = G.successors(artist)
                followers = G.predecessors(artist)
                try:
                    print(
                        "\t", username + " has " + str(len(followings)) + " followings"
                    )
                    print(
                        "\t",
                        username
                        + " follows "
                        + ", ".join([scac.id2username(x) for x in followings]),
                    )
                except TypeError:
                    print("No followings home!")
                try:
                    print("\t", username + " has " + str(len(followers)) + " followers")
                    print(
                        "\t",
                        username
                        + " is followed by "
                        + ", ".join([scac.id2username(x) for x in followers]),
                    )
                except TypeError:
                    print("No followers home!")
                    print("-" * 40)
            except UnicodeError:
                print("Artist's username not found")
