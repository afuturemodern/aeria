import sys
import networkx as nx
import soundcloud


def read_graph(G, gfile):
    print("Reading in artist graph...")
    try:
        G = nx.read_pajek(gfile)
        print("Read successfully!")
        print("The artist graph currently contains " + str(len(G)) + " artists.")
        print(
            "The artist graph currently contains "
            + str(nx.number_strongly_connected_components(G))
            + " strongly connected components."
        )
    except IOError:
        print("Could not find artistGraph")


def write_graph(G, gfile):
    try:
        print("Writing out new artists...")
        nx.write_pajek(G, gfile)
        print("New artists written successfully!")
        print("The artist graph currently contains " + str(len(G)) + " artists.")
        print(
            "The artist graph currently contains "
            + str(nx.number_strongly_connected_components(G))
            + " strongly connected components."
        )
    except IOError:
        print("New artists could not be written...")


# artistGraph = nx.MultiDiGraph()
# read_graph(artistGraph, 'artistGraph.net')
# print_graph(artistGraph)
