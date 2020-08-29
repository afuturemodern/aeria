from py2neo import Graph, Relationship, authenticate

authenticate("localhost:7474", "neo4j", "cloudchaser")
graph = Graph("http://localhost:7474/db/data/")

graph.delete_all()

alice = graph.merge("Person", "name", "Alice")
bob = graph.merge("Person", "name", "Bob")
chelsea = graph.merge("Person", "name", "Chelsea")

prof = {"name": "Dennis"}

fav = {"name": "Emma"}

query = (
    "MERGE (profile:soundcloud {name: {profile}.name}) \
        ON CREATE SET profile={profile} "
    "MERGE (favorite:soundcloud {name: {favorite}.name}) \
        ON CREATE SET favorite={favorite} "
)

graph.cypher.execute(query, {"profile": prof, "favorite": fav})

dennis = graph.find_one("soundcloud", "name", "Dennis")
emma = graph.find_one("soundcloud", "name", "Emma")

print(dennis.properties, emma.properties)

# graph.create(alice)
# graph.create(bob)
# graph.create(chelsea)
# bob, likes = graph.create({"name": "Bob"}, (alice, "likes", 0))
# chelsea, likes = graph.create({"name": "Chelsea"}, (alice, "likes", 0))

alice_likes_bob = Relationship(alice, "likes", bob, songs=["goodsong", "nicetune"])
alice_likes_chelsea = Relationship(alice, "likes", chelsea, songs=["greatsong"])

graph.create_unique(alice_likes_bob)
graph.create_unique(alice_likes_chelsea)

alice_likes_chelsea["songs"] += ["awesometrack"]

print(alice_likes_chelsea.properties)

for rel in graph.match(start_node=alice, rel_type="likes"):
    print(rel.end_node["name"])
    print(rel.properties)
