#! /usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
from json import dumps
from re import match
from sqlite3 import connect as sqlite_connect
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

CREATE_ITEMS_SQL = '''
CREATE TABLE items
    (id INTEGER PRIMARY KEY,
     path TEXT,
     time TIMESTAMP,
     content_type TEXT,
     content TEXT)
'''
ADD_ITEM_SQL = '''
INSERT INTO items
    (path, content, content_type, time)
    values (?, ?, ?, ?)
'''
GET_LATEST_ITEM_SQL = '''
SELECT content_type, content FROM items
    WHERE path = ?
    ORDER BY time DESC LIMIT 1
'''
GET_ALL_PATHS_SQL = 'SELECT path FROM items WHERE path like ?'

class Resources:
    def __init__(self):
        self._connection = sqlite_connect(':memory:')
        self._connection.execute(CREATE_ITEMS_SQL)

    def add(self, path, content_type, content, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()
        with self._connection:
            self._connection.execute(ADD_ITEM_SQL,
                                     (path, content, content_type, timestamp))

    def get(self, path):
        result = self._connection.execute(GET_LATEST_ITEM_SQL, (path,))
        items = result.fetchall()
        if len(items) > 0:
            return {'content_type': items[0][0], 'content': items[0][1]}
        m = match(r"(.*)/index.(\w*)$", path)
        if m is not None:
            return self._index_response(m.group(1), m.group(2))
        else:
            return None

    def _index_response(self, root, protocol):
        result = self._connection.execute(GET_ALL_PATHS_SQL, (root + '%',))
        paths = [r[0] for r in result.fetchall()]
        if protocol == 'html':
            content_type = 'text/html'
            content = self._html_index(root, paths)
        elif protocol == 'json':
            content_type = 'application/json'
            content = dumps(paths)
        else:
            return None
        return {'content_type': content_type, 'content': content}

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
