import soundcloud

# create a client object with your app credentials
client = soundcloud.Client(client_id='454aeaee30d3533d6d8f448556b50f23')

page_size = 100

results = client.get('/tracks', order='created_at', limit=page_size, linked_partitioning=1)
i = 0
page = 0
while True:
    for track in results.collection:
        print "\t", i, track.title
        i += 1

    print "Finished page {0:d}".format(page)

    if getattr(results, 'next_href', None) is None:
        break

    page += 1
    # start paging through results, 100 at a time
    results = client.get(results.next_href)

print "Finished!"
