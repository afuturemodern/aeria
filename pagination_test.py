import soundcloud
from utils import get_results

# create a client object with your app credentials
client = soundcloud.Client(client_id="454aeaee30d3533d6d8f448556b50f23")

i = 0
for track in get_results(client, "/tracks"):
    print(i, track.title)
    i += 1
    if i == 100:
        break

i = 0
for user in get_results(client, "/users"):
    print(i, user.first_name, user.last_name, user.id)
    i += 1
    if i == 100:
        break
