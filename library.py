from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from os import fork
from pika import BlockingConnection, ConnectionParameters
from sys import argv
from time import sleep

resources = {}

class LibraryHandler(BaseHTTPRequestHandler):
    def do_PUT(self):
        try:
            content_type = self.headers['Content-Type']
            length = int(self.headers['Content-Length'])
            content = self.rfile.read(length)
            resources[self.path] = {'content_type': content_type,
                                    'content': content}
        except KeyError:
            self.send_error(400)
            return

        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        try:
            resource = resources[self.path]
            content_type = resource['content_type']
            content = resource['content']
            length = len(content)
        except KeyError:
            self.send_error(404)
            return

        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', length)
        self.end_headers()
        self.wfile.write(content)

def run_server(host, port):
    server = HTTPServer((host, port), LibraryHandler)
    server.serve_forever()

def publish(host, port):
    connection = BlockingConnection(ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='library_url')
    url = 'http://%s:%d' % (host, port)

    while True:
        channel.basic_publish(exchange='',
                              routing_key='library_url',
                              body=url)
        sleep(1)

host, port = argv[1], int(argv[2])
if len(argv) >= 4:
    config_file = argv[3]
    resources['/' + config_file] = {'content_type': 'application/json',
                                    'content': open(config_file).read()}
pid = fork()
if pid > 0:
    run_server(host, port)
else:
    publish(host, port)
