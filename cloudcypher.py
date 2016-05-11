from py2neo import Graph, Node, Relationship, authenticate

authenticate("localhost:7474", "neo4j", "cloudchaser")
graph = Graph("http://localhost:7474/db/data/")

graph.delete_all()

alice = Node("Person", name="Alice")
bob = Node("Person", name="Bob")
chelsea = Node("Person", name="Chelsea")

graph.create(alice)
graph.create(bob)
graph.create(chelsea)
#bob, likes = graph.create({"name": "Bob"}, (alice, "likes", 0))
#chelsea, likes = graph.create({"name": "Chelsea"}, (alice, "likes", 0))

alice_likes_bob = Relationship(alice, "likes", bob, songs=["goodsong", "nicetune"])
alice_likes_chelsea = Relationship(alice, "likes", chelsea, songs = ['greatsong'])

graph.create_unique(alice_likes_bob)
graph.create_unique(alice_likes_chelsea)

alice_likes_chelsea['songs'] += ['awesometrack']

print alice_likes_chelsea.properties

for rel in graph.match(start_node=alice, rel_type="likes"):
    print rel.end_node["name"]
    print rel.properties
