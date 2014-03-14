from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from json import dumps, loads
from os import fork
from pubsub import create_channel, publish
from time import sleep

CONFIG_FILE = 'config.json'

class Resources:
    def __init__(self):
        self.resources = {}

    def add(self, path, content_type, content):
        self.resources[path] = {'content_type': content_type,
                                'content': content}
    def get(self, path):
        if path == '/':
            return {'content_type': 'application/json',
                    'content': dumps(self.resources.keys())}
        else:
            try:
                return self.resources[path]
            except KeyError:
                return None

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

def publish_url(host, port):
    channel = create_channel()
    url = 'http://%s:%d' % (host, port)

    while True:
        publish(channel=channel, label='library_url', message=url)
        sleep(1)

resources = Resources()
config_string = open(CONFIG_FILE).read()
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
