#! /usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from json import load
from os.path import join as pathjoin
from pubsub import connect
from re import match
from SocketServer import ForkingMixIn
from sys import argv

def wrong_verb(expected, got):
    return {'code': 405,
            'content': 'Expected method %s, got %s' % (expected, got)}

def root_handler(verb, headers, content):
    if verb != 'GET':
        return wrong_verb(expected='GET', got=verb)
    with open('pubsub_ws_doc.html', 'r') as f:
        doc_html = f.read()
    return {'code': 200, 'content': doc_html, 'type': 'text/html'}

def topic_handler(verb, headers, content, exchange, topic):
    if verb == 'POST':
        connection = connect('amqp://localhost', exchange)
        connection.publish(topic, content)
        return {'code': 200, 'content': ''}
    elif verb == 'GET':
        connection = Connection(exchange)
        queue = connection.subscribe(topic)
        return {'code': 200, 'content': queue}
    else:
        return wrong_verb(expected='GET or POST', got=verb)

def get_message_range(connection, queue, timeout, range_value):
    if range_value == 'head':
        return connection.get_message_block(queue, timeout)
    elif range_value == 'all':
        return '\n'.join(connection.get_all_messages(queue))

def queue_handler(verb, headers, content, exchange, queue):
    if verb == 'GET':
        connection = Connection(exchange)
        range_header = headers.get('Range', 'head')
        timeout = float(headers.get('Patience', 0))
        message = get_message_range(connection, queue, timeout, range_header)
        if message is None:
            message = ''
        return {'code': 200, 'content': message}
    elif verb == 'DELETE':
        connection = Connection(exchange)
        connection.unsubscribe(queue)
        return {'code': 200, 'content': ''}
    else:
        return wrong_verb(expected='DELETE or GET', got=verb)

handlers = [('/$',                                 root_handler),
            ('/exchanges/([^/]+)/([^/]+)$',        topic_handler),
            ('/exchanges/([^/]+)/queues/([^/]+)$', queue_handler)]

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
            return lambda v, h, c: handler(v, h, c, *params)

    def do_GET(self):
        self._do_request('GET')

    def do_POST(self):
        self._do_request('POST')

    def do_DELETE(self):
        self._do_request('DELETE')

    def _do_request(self, verb):
        handler = self._parse_path()
        if handler is None:
            self.send_error(404)
            return
        length = int(self.headers.get('Content-Length', 0))
        content = self.rfile.read(length)
        response = handler(verb, self.headers, content)
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

class ForkingHTTPServer(ForkingMixIn, HTTPServer):
    pass

def run_server(host, port):
    server = ForkingHTTPServer((host, port), PubSubHandler)
    server.serve_forever()

config_dir = argv[1]
config_file_path = pathjoin(config_dir, 'infra.json')
with open(config_file_path, 'r') as config_file:
    config = load(config_file)
host, port = config['pubsub_host'], config['pubsub_port']
run_server(host, port)
