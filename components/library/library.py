#! /usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from json import dumps, loads
from os import fork
from pubsub import create_channel, publish
from re import sub
from signal import SIGKILL, signal
from time import sleep
from urllib2 import URLError, urlopen

CONFIG_FILE = 'config.json'
INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Contents of %s</title>
  </head>
  <body>
    <h2>Contents of %s</h2>
    <ul>
      %s
    </ul>
  </body>
</html>
'''
LINK_TEMPLATE = '<li><a href="%s">%s</a></li>'

class Resources:
    def __init__(self):
        self.resources = {}

    def add(self, path, content_type, content):
        self.resources[path] = {'content_type': content_type,
                                'content': content}

    def get(self, path):
        if path in self.resources:
            return self.resources[path]
        if path.endswith('index.html'):
            return {'content_type': 'text/html',
                    'content': html_index(sub('index\.html$', '', path))}
        return None

    def all_paths(self):
        return self.resources.keys()

def html_index(root):
    paths = sorted(resources.all_paths())
    links = [LINK_TEMPLATE % (p,p) for p in paths if p.startswith(root)]
    return INDEX_TEMPLATE % (root, root, '\n'.join(links))

class HTTPServerWithResources(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, resources):
        HTTPServer.__init__(self, server_address, RequestHandlerClass)
        self.resources = resources

class LibraryHandler(BaseHTTPRequestHandler):
    def do_PUT(self):
        if not self._check_put_headers(self.headers):
            self.send_error(400)
            return

        content_type = self.headers['Content-Type']
        length = int(self.headers['Content-Length'])
        content = self.rfile.read(length)
        self.server.resources.add(self.path, content_type, content)

        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        resource = self.server.resources.get(self.path)
        if resource is None:
            self.send_error(404)
            return

        self.send_response(200)
        self.send_header('Content-Type', resource['content_type'])
        self.send_header('Content-Length', len(resource['content']))
        self.end_headers()
        self.wfile.write(resource['content'])

    def log_message(self, format, *args):
        pass

    def _check_put_headers(self, headers):
        required_put_headers = ['content-type', 'content-length']
        return set(required_put_headers).issubset(set(headers.keys()))

def run_server(host, port, resources):
    server = HTTPServerWithResources((host, port), LibraryHandler, resources)
    server.serve_forever()

def is_responsive(url):
    try:
        urlopen(url).read()
        return True
    except URLError:
        return False

def publish_url(host, port):
    channel = create_channel()
    url = 'http://%s:%d' % (host, port)

    while is_responsive(url + '/index.html'):
        publish(channel=channel, label='library_url', message=url)
        sleep(1)

resources = Resources()
with open(CONFIG_FILE) as config_file:
    config_string = config_file.read()
config = loads(config_string)
host, port = config['library_host'], config['library_port']
resources.add(path='/config.json',
              content_type='application/json',
              content=config_string)
pid = fork()
if pid > 0:
    run_server(host, port, resources)
else:
    publish_url(host, port)
