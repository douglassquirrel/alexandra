from json import dumps, load, loads
from pubsub import create_channel, publish, subscribe, unsubscribe, \
                   get_message, get_all_messages, get_message_block
from StringIO import StringIO
from urllib2 import build_opener, HTTPHandler, Request, urlopen

class Queue:
    def __init__(self, channel, topic, subscribe_world, alex):
        self._channel = channel
        self._q = subscribe(self._channel, topic)
        self._subscribe_world = subscribe_world
        self._alex = alex

    def next(self):
        if self._subscribe_world is True:
            self._alex.update_world()
        message = get_message(self._channel, self._q)
        if message is not None:
            return loads(message)
        else:
            return None

    def fetch_all(self):
        return map(loads, get_all_messages(self._channel, self._q))

class Alexandra:
    def __init__(self, subscribe_world=False):
        self._channel = create_channel()
        self._library_url = self._get_library_url()
        self.config = self._get_config()
        self._subscribe_world = subscribe_world
        self._world_queue = None
        self.world = None
        if self._subscribe_world is True:
            self.next_tick()

    def enter_in_library(self, data, path, content_type):
        opener = build_opener(HTTPHandler)
        request = Request(self._library_url + path, data)
        request.add_header('Content-Type', content_type)
        request.get_method = lambda: 'PUT'
        opener.open(request)

    def subscribe(self, topic):
        return Queue(self._channel, topic, self._subscribe_world, self)

    def publish(self, topic, message):
        publish(self._channel, topic, dumps(message))

    def next_tick(self):
        if self._world_queue is None:
            self._init_world_queue()
        self.world = loads(get_message_block(self._channel, self._world_queue))

    def update_world(self):
        new_world = get_message(self._channel, self._world_queue)
        if new_world is not None:
            self.world = loads(new_world)

    def get_library_file(self, path):
        url = self._library_url + path
        return StringIO(urlopen(url).read())

    def _init_world_queue(self):
        self._world_queue = subscribe(self._channel, 'world')

    def _get_library_url(self):
        library_url_queue = subscribe(self._channel, 'library_url')
        library_url = get_message_block(self._channel, library_url_queue)
        unsubscribe(self._channel, library_url_queue, 'library_url')
        return library_url

    def _get_config(self):
        return load(self.get_library_file('/config.json'))
