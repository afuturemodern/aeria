import sys
from requests.exceptions import ConnectionError, HTTPError

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

def handle_http_errors(fn):
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ConnectionError:
            print "\t"*2, "{0:s}: Connection Error".format(fn.__name__)
            return []
        except HTTPError, e:
            return []
        except TypeError:
            print "\t"*2, "{0:s}: Type Error".format(fn.__name__)
            return []
        except RuntimeError, e:
            print "\t", "{0:s}: Runtime Error".format(fn.__name__)
            return []
        except Exception, e:
            if hasattr(e, 'response'):
                print "\t"*2, "{0:s}: Status Code ({1:d}) for uncaught error: {2:s}".format(fn.__name__, e.response.status_code, e.message)
            else:
                print "\t"*2, "{0:s}: Uncaught error: {1:s}".format(fn.__name__, e.message)
            return []
    return wrapped

def wrap_error(fn):
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception, e:
            et, ei, tb = sys.exc_info()
            raise et, ei, tb
    return wrapped
