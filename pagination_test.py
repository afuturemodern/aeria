import soundcloud

# create a client object with your app credentials
client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

page_size = 100

# get first 100 tracks
results = client.get('/tracks', order='created_at', limit=page_size)

i = 0
page = 0
while True:
    tracks = getattr(results, 'collection', results)
    for track in tracks:
        print "\t", i, track.title
        i += 1

    print "Finished page {0:d}".format(page)

    page += 1
    # start paging through results, 100 at a time
    results = client.get('/tracks', order='created_at', limit=page_size,
                        linked_partitioning=page)
