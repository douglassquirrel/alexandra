from time import sleep, time as now
from urllib2 import build_opener, HTTPHandler, Request, URLError, urlopen

class Docstore:
    def __init__(self, url):
        self._url = url
        self._cache = {}

    def wait_until_up(self, timeout=5):
        return self.wait_and_get('/index.html', timeout) is not None

    def wait_and_get(self, path, timeout=5):
        give_up = now() + timeout
        while now() < give_up:
            doc = self.get(path)
            if doc is not None:
                return doc
            sleep(0.1)
        return None

    def put(self, data, path, content_type):
        opener = build_opener(HTTPHandler)
        request = Request(self._url + path, data)
        request.add_header('Content-Type', content_type)
        request.get_method = lambda: 'PUT'
        opener.open(request)

    def get(self, path):
        if path not in self._cache:
            self._fill_cache(path)
            if path not in self._cache:
                return None
        return self._cache[path]['data']

    def _fill_cache(self, path):
        url = self._url + path
        try:
            f = urlopen(url)
        except URLError:
            return
        self._cache[path] = {'data': f.read()}

def connect(url):
    return Docstore(url)
