from json import dumps, load, loads
from pubsub import Connection, QueueMonitor
from sys import argv
from urllib2 import build_opener, HTTPHandler, Request, URLError, urlopen

class Queue:
    def __init__(self, connection, topic, alex):
        self._connection = connection
        self._q = self._connection.subscribe(topic)
        self._alex = alex

    def next(self):
        message = self._connection.get_message(self._q)
        if message is not None:
            return loads(message)
        else:
            return None

    def fetch_all(self):
        return map(loads, self._connection.get_all_messages(self._q))

    def consume(self, f):
        def callback(message):
            return f(loads(message), self._alex)
        self._connection.consume(self._q, callback)

class TopicMonitor:
    def __init__(self, connection, topic):
        queue = connection.subscribe(topic)
        self._monitor = QueueMonitor(connection, queue)

    def latest(self):
        return loads(self._monitor.latest())

def request_game(game_name, game_id):
    connection = Connection('emcee')
    game_info = {'name': game_name, 'id': game_id}
    connection.publish('game.wanted', dumps(game_info))

class Alexandra:
    def __init__(self, game_id=None, fetch_game_config=True):
        if game_id is None:
            game_id = argv[2]
        self._connection = Connection(game_id)
        self._library_url = self._get_library_url()
        self._library_files = {}
        if fetch_game_config is True:
            self._wait_for_game_config()

    def topic_monitor(self, topic):
        return TopicMonitor(self._connection, topic)

    def consume(self, topic, f):
        queue = Queue(self._connection, topic, self)
        queue.consume(f)

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

    def publish(self, topic, message):
        main_topic = topic.split('.')[0]
        if self.is_in_library('/messages/%s.json' % main_topic):
            self._connection.publish(topic, dumps(message))
        else:
            print "Refused to publish %s, no documentation" % topic

    def subscribe(self, topic):
        return Queue(self._connection, topic, self)

    def _get_library_url(self):
        library_url_queue = self._connection.subscribe('library_url')
        library_url = self._connection.get_message_block(library_url_queue)
        self._connection.unsubscribe(library_url_queue, 'library_url')
        return library_url

    def _wait_for_game_config(self):
        config_file = None
        while config_file is None:
            config_file = self.get_library_file('/game.json')
        self.config = loads(config_file)
