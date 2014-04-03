#! /usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from json import load
from os.path import join as pathjoin
from re import match
from sys import argv

def root(path, verb):
    print 'root_doc %s %s' % (path, verb)
    return {'code': 200, 'content': '"OK"'}
def exchanges(path, verb):
    print 'exchanges %s %s' % (path, verb)
    return {'code': 200, 'content': '"OK"'}
def exchange(path, verb):
    print 'exchange %s %s' % (path, verb)
    return {'code': 200, 'content': '"OK"'}
def topic(path, verb):
    print 'topic %s %s' % (path, verb)
    return {'code': 200, 'content': '"OK"'}
def queues(path, verb):
    print 'queues %s %s' % (path, verb)
    return {'code': 200, 'content': '"OK"'}
def queue(path, verb):
    print 'queue %s %s' % (path, verb)
    return {'code': 200, 'content': '"OK"'}

handlers = [('/$',                      root),
            ('/exchanges$',             exchanges),
            ('/exchanges/$',            exchanges),
            ('/exchanges/[^/]*$',       exchange),
            ('/exchanges/[^/]+/$',      exchange),
            ('/exchanges/[^/]+/[^/]+$', topic),
            ('/queues$',                queues),
            ('/queues/$',               queues),
            ('/queues/[^/]+$',          queue)]


class PubSubHandler(BaseHTTPRequestHandler):
    def _find_handler(self):
        matches = filter(lambda(r, h): match(r, self.path), handlers)
        if len(matches) == 0:
            return None
        else:
            return matches[0][1]

    def do_GET(self):
        self._do_request('GET')

    def do_POST(self):
        self._do_request('POST')

    def do_DELETE(self):
        self._do_request('DELETE')

    def _do_request(self, verb):
        handler = self._find_handler()
        if handler is None:
            self.send_error(404)
            return
        response = handler(self.path, verb)
        code, content = response['code'], response['content']
        if code >= 400:
            self.send_error(code)
            return

        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
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
