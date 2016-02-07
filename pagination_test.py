import soundcloud

# let's return tracks via a generator instead...
def get_results(client, url, page_size=100):
    def get_next_results(results=None):
        if results is None:
            return client.get(url, order='created_at', limit=page_size, linked_partitioning=1)
        next_href = getattr(results, 'next_href', None)
        if next_href is None: return None
        else: return client.get(next_href)

    def yield_results():
        # start results
        results = get_next_results(None)
        while results is not None:
            for result in getattr(results, 'collection', []):
                yield result
            results = get_next_results(results)

    return yield_results()

# create a client object with your app credentials
client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

i = 0
for track in get_results(client, '/tracks'):
    print i, track.title
    i += 1
    if i == 100: break

i = 0
for user in get_results(client, '/users'):
    print i, user.first_name, user.last_name
    i+= 1
    if i == 100: break
