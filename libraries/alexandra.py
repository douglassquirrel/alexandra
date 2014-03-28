from json import dumps, load, loads
from pubsub import create_channel, consume, publish, subscribe, unsubscribe, \
                   get_message, get_all_messages, get_message_block, \
                   QueueMonitor
from time import sleep
from urllib2 import build_opener, HTTPHandler, Request, URLError, urlopen

class Queue:
    def __init__(self, channel, topic, alex, subscribe_world=False):
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

    def consume(self, f):
        def callback(message):
            return f(loads(message), self._alex)
        consume(self._channel, self._q, callback)

class TopicMonitor:
    def __init__(self, channel, topic):
        queue = subscribe(channel, topic)
        self._monitor = QueueMonitor(channel, queue)

    def latest(self):
        return loads(self._monitor.latest())

class Alexandra:
    def __init__(self, subscribe_world=False, fetch_game_config=True):
        self._channel = create_channel()
        self._library_url = self._get_library_url()
        self._library_files = {}
        if fetch_game_config is True:
            self._wait_for_game_config()
        self._subscribe_world = subscribe_world
        self._each_world = []
        self._world_queue = None
        self.world = None
        if self._subscribe_world is True:
            self.next_world()

    def topic_monitor(self, topic):
        return TopicMonitor(self._channel, topic)

    def on_each_world(self, f):
        self._each_world.append(f)

    def wait(self):
        while True:
            self.next_world()

    def monitor(self, queue, f):
        while True:
            message = queue.next()
            if message is not None:
                f(message, self)
            sleep(self.config['tick_seconds']/5)

    def consume(self, topic, f):
        queue = Queue(self._channel, topic, self)
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
            publish(self._channel, topic, dumps(message))
        else:
            print "Refused to publish %s, no documentation" % topic

    def subscribe(self, topic):
        return Queue(self._channel, topic, self, self._subscribe_world)

    def next_world(self):
        if self._world_queue is None:
            self._init_world_queue()
        self.world = loads(get_message_block(self._channel, self._world_queue))
        self._do_each_world()

    def update_world(self):
        new_world = get_message(self._channel, self._world_queue)
        if new_world is not None:
            self.world = loads(new_world)
            self._do_each_world()

    def _do_each_world(self):
        for f in self._each_world:
            f(self)

    def _init_world_queue(self):
        self._world_queue = subscribe(self._channel, 'world')

    def _get_library_url(self):
        library_url_queue = subscribe(self._channel, 'library_url')
        library_url = get_message_block(self._channel, library_url_queue)
        unsubscribe(self._channel, library_url_queue, 'library_url')
        return library_url

    def _wait_for_game_config(self):
        config_file = None
        while config_file is None:
            config_file = self.get_library_file('/game.json')
        self.config = loads(config_file)
