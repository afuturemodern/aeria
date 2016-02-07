import soundcloud

# let's return tracks via a generator instead...
def get_tracks(client, page_size=100):
    def get_results(next_href=None):
        if next_href is None: return None
        else: return client.get(next_href)

    def yield_results():
        # start results
        results = client.get('/tracks', order='created_at', limit=page_size, linked_partitioning=1)
        while results is not None:
            for result in getattr(results, 'collection', []):
                yield result
            results = get_results(getattr(results, 'next_href', None))

    return yield_results()

# create a client object with your app credentials
client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

i = 0
for track in get_tracks(client):
    print i, track.title
    i += 1
    if i == 100: break

