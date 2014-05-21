#! /usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from docstore import connect as docstore_connect
from pubsub import connect as pubsub_connect
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

def topic_handler(verb, headers, content, docstore_url, exchange, topic):
    if verb == 'POST':
        pubsub_url = docstore_connect(docstore_url).get('/services/pubsub')
        pubsub = pubsub_connect(pubsub_url, exchange)
        pubsub.publish(topic, content)
        return {'code': 200, 'content': ''}
    elif verb == 'GET':
        pubsub_url = docstore_connect(docstore_url).get('/services/pubsub')
        pubsub = pubsub_connect(pubsub_url, exchange)
        queue = pubsub.subscribe(topic)
        return {'code': 200, 'content': queue}
    else:
        return wrong_verb(expected='GET or POST', got=verb)

def get_message_range(pubsub, queue, timeout, range_value):
    if range_value == 'head':
        return pubsub.get_message_block(queue, timeout)
    elif range_value == 'all':
        return '\n'.join(pubsub.get_all_messages(queue))

def queue_handler(verb, headers, content, docstore_url, exchange, queue):
    if verb == 'GET':
        pubsub_url = docstore_connect(docstore_url).get('/services/pubsub')
        pubsub = pubsub_connect(pubsub_url, exchange)
        range_header = headers.get('Range', 'head')
        timeout = float(headers.get('Patience', 0))
        message = get_message_range(pubsub, queue, timeout, range_header)
        if message is None:
            message = ''
        return {'code': 200, 'content': message}
    elif verb == 'DELETE':
        pubsub_url = docstore_connect(docstore_url).get('/services/pubsub')
        pubsub = pubsub_connect(pubsub_url, exchange)
        pubsub.unsubscribe(queue)
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
            docstore_url = self.server.docstore_url
            return lambda v, h, c, d: handler(v, h, c, docstore_url, *params)

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

host, port = argv[1], int(argv[2])
server = ForkingHTTPServer((host, port), PubSubHandler)
server.docstore_url = argv[3]
server.serve_forever()
