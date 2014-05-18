#! /usr/bin/python

from os.path import abspath, join as pathjoin
from sys import path
path.insert(0, abspath(pathjoin('..', 'libraries')))

from docstore import connect as docstore_connect
from installer import install
from json import load
from sys import exit

def install_service(name, options, services_dir, libraries_dir):
    service_dir = abspath(pathjoin(services_dir, name))
    return install(name, [service_dir, libraries_dir], options)[0]

services_dir = abspath(pathjoin('..', 'services'))
games_dir = abspath(pathjoin('..', 'games'))
libraries_dir = abspath(pathjoin('..', 'libraries'))

with open(pathjoin(services_dir, 'services.json'), 'r') as config_file:
    config = load(config_file)
docstore_host = config['docstore_host']
docstore_port = str(config['docstore_port'])
docstore_url = 'http://%s:%s' % (docstore_host, docstore_port)
pubsub_host = config['pubsub_host']
pubsub_port = str(config['pubsub_port'])
pubsub_url = config['pubsub_url']

services = [('docstore_server_http', [docstore_host, docstore_port]),
           ('emcee', [games_dir, libraries_dir, docstore_url]),
           ('pubsub_ws', [pubsub_host, pubsub_port, docstore_url])]

procs = map(lambda (n, o): install_service(n, o, services_dir, libraries_dir),
            services)

docstore = docstore_connect(docstore_url)
if docstore.wait_until_up() is False:
    print 'Could not start docstore'
    exit(1)
docstore.put(pubsub_url, '/services/pubsub', 'text/plain')

print 'Now running'
raw_input('Press Enter to stop\n')
map(lambda p: p.kill(), procs)
