#! /usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from json import dumps
from re import match, sub
from sys import argv

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
        m = match(r"(.*)/index.(\w*)$", path)
        if m is not None:
            return self._index_response(m.group(1), m.group(2))
        else:
            return None

    def _index_response(self, root, protocol):
        paths = self._paths_in(root)
        if protocol == 'html':
            content_type = 'text/html'
            content = self._html_index(root, paths)
        elif protocol == 'json':
            content_type = 'application/json'
            content = dumps(paths)
        else:
            return None
        return {'content_type': content_type, 'content': content}

    def _all_paths(self):
        return self.resources.keys()

    def _paths_in(self, root):
        return sorted(filter(lambda p: p.startswith(root), self._all_paths()))

    def _html_index(self, root, paths):
        links = [LINK_TEMPLATE % (p,p) for p in paths]
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

host, port = argv[1], int(argv[2])
run_server(host, port, Resources())
