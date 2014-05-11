from json import dumps, load, loads
from pubsub import connect
from sys import argv
from urllib2 import build_opener, HTTPHandler, Request, URLError, urlopen

def request_game(game_name, game_id, pubsub_url='amqp://localhost'):
    connection = connect(pubsub_url, 'emcee')
    game_info = {'name': game_name, 'id': game_id}
    connection.publish('game.wanted', dumps(game_info))

class Alexandra:
    def __init__(self, game_id=None, fetch_game_config=True,
                 pubsub_url='amqp://localhost'):
        if game_id is None:
            game_id = argv[2]
        self.pubsub = connect(pubsub_url, game_id,
                              marshal=dumps, unmarshal=loads)
        self._library_url = self._get_library_url()
        self._library_files = {}
        if fetch_game_config is True:
            self._wait_for_game_config()

    def enter_in_library(self, data, path, content_type):
        opener = build_opener(HTTPHandler)
        request = Request(self._library_url + path, data)
        request.add_header('Content-Type', content_type)
        request.get_method = lambda: 'PUT'
        opener.open(request)

    def get_library_file(self, path):
        if path not in self._library_files:
            self._fetch_library_file_to_cache(path)
            if path not in self._library_files:
                return None
        return self._library_files[path]['data']

    def _fetch_library_file_to_cache(self, path):
        url = self._library_url + path
        try:
            f = urlopen(url)
        except URLError:
            return
        self._library_files[path] = {'data': f.read()}

    def is_in_library(self, path):
        return self.get_library_file(path) is not None

    def _get_library_url(self):
        library_url_queue = self.pubsub.subscribe('library_url')
        library_url = self.pubsub.get_message_block(library_url_queue)
        self.pubsub.unsubscribe(library_url_queue)
        return library_url

    def _wait_for_game_config(self):
        config_file = None
        while config_file is None:
            config_file = self.get_library_file('/game.json')
        self.config = loads(config_file)
