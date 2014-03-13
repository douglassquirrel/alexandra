from json import dumps, load, loads
from pubsub import create_channel, publish, subscribe, unsubscribe, \
                   get_message, get_all_messages, get_message_block
from time import sleep
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
        self._library_files = {}
        self.config = self._get_config()
        self._subscribe_world = subscribe_world
        self._world_queue = None
        self.world = None
        if self._subscribe_world is True:
            self.next_tick()

    def each_tick(self, f):
        while True:
            self.next_tick()
            f(self)

    def monitor(self, queue, f):
        while True:
            message = queue.next()
            if message is not None:
                f(message, self)
            sleep(self.config['tick_seconds']/5)

    def enter_in_library(self, data, path, content_type):
        opener = build_opener(HTTPHandler)
        request = Request(self._library_url + path, data)
        request.add_header('Content-Type', content_type)
        request.get_method = lambda: 'PUT'
        opener.open(request)

    def get_library_file(self, path):
        if path not in self._library_files:
            url = self._library_url + path
            self._library_files[path] = {'data': urlopen(url).read()}
        return self._library_files[path]['data']

    def publish(self, topic, message):
        publish(self._channel, topic, dumps(message))

    def subscribe(self, topic):
        return Queue(self._channel, topic, self._subscribe_world, self)

    def next_tick(self):
        if self._world_queue is None:
            self._init_world_queue()
        self.world = loads(get_message_block(self._channel, self._world_queue))

    def update_world(self):
        new_world = get_message(self._channel, self._world_queue)
        if new_world is not None:
            self.world = loads(new_world)

    def _init_world_queue(self):
        self._world_queue = subscribe(self._channel, 'world')

    def _get_library_url(self):
        library_url_queue = subscribe(self._channel, 'library_url')
        library_url = get_message_block(self._channel, library_url_queue)
        unsubscribe(self._channel, library_url_queue, 'library_url')
        return library_url

    def _get_config(self):
        return loads(self.get_library_file('/config.json'))
