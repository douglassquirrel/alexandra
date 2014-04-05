#! /usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from json import load
from os.path import join as pathjoin
from pubsub import Connection
from re import match
from sys import argv

def wrong_verb(expected, got):
    return {'code': 405,
            'content': 'Expected method %s, got %s' % (expected, got)}

def root_handler(verb, content, pubsub_data):
    if verb != 'GET':
        return wrong_verb(expected='GET', got=verb)
    with open('pubsub_ws_doc.html', 'r') as f:
        doc_html = f.read()
    return {'code': 200, 'content': doc_html, 'type': 'text/html'}

def topic_handler(verb, content, pubsub_data, exchange, topic):
    if verb == 'POST':
        connection = pubsub_data.connection_for_exchange(exchange)
        connection.publish(topic, content)
        return {'code': 200, 'content': ''}
    elif verb == 'GET':
        connection = pubsub_data.connection_for_exchange(exchange)
        queue = connection.subscribe(topic)
        pubsub_data.register_queue(queue, exchange)
        return {'code': 200, 'content': queue}
    else:
        return wrong_verb(expected='GET or POST', got=verb)

def queue_handler(verb, content, pubsub_data, queue):
    if verb == 'GET':
        connection = pubsub_data.connection_for_queue(queue)
        message = connection.get_message(queue)
        if message is None:
            message = ''
        return {'code': 200, 'content': message}
    else:
        return wrong_verb(expected='DELETE, GET, or POST', got=verb)

handlers = [('/$',                          root_handler),
            ('/exchanges/([^/]+)/([^/]+)$', topic_handler),
            ('/queues/([^/]+)$',            queue_handler)]

class PubSubData:
    def __init__(self):
        self._connections = {}
        self._queues = {}

    def connection_for_exchange(self, exchange):
        if exchange not in self._connections:
            self._connections[exchange] = Connection(exchange)
        return self._connections[exchange]

    def register_queue(self, queue, exchange):
        self._queues[queue] = exchange

    def connection_for_queue(self, queue):
        exchange = self._queues[queue]
        return self.connection_for_exchange(exchange)

class PubSubHandler(BaseHTTPRequestHandler):
    def _parse_path(self):
        match_results = map(lambda(r, h): (match(r, self.path), h), handlers)
        matches = filter(lambda(m, h): m is not None, match_results)
        if len(matches) == 0:
            return None
        else:
            matched = matches[0]
            params = matched[0].groups()
            handler = matched[1]
            return lambda v, c, ps: handler(v, c, ps, *params)

    def do_GET(self):
        self._do_request('GET')

    def do_POST(self):
        self._do_request('POST')

    def do_DELETE(self):
        self._do_request('DELETE')

    def _do_request(self, verb):
        if not hasattr(self.server, 'pubsub_data'):
            self.server.pubsub_data = PubSubData()
        handler = self._parse_path()
        if handler is None:
            self.send_error(404)
            return
        length = int(self.headers.get('Content-Length', 0))
        content = self.rfile.read(length)
        response = handler(verb, content, self.server.pubsub_data)
        self._do_response(response)

    def _do_response(self, response):
        code, content = response['code'], response['content']
        content_type = response.get('type', 'application/json')
        if code >= 400:
            self.send_error(code, content)
            return

        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format, *args):
        pass

def run_server(host, port):
    server = HTTPServer((host, port), PubSubHandler)
    server.serve_forever()

config_dir = argv[1]
config_file_path = pathjoin(config_dir, 'infra.json')
with open(config_file_path, 'r') as config_file:
    config = load(config_file)
host, port = config['pubsub_host'], config['pubsub_port']
run_server(host, port)
