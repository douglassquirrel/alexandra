#! /usr/bin/python

from os.path import abspath, join as pathjoin
from sys import path
path.insert(0, abspath(pathjoin('..', 'libraries')))

from docstore import connect as docstore_connect
from installer import install
from json import load
from os import listdir
from os.path import abspath, basename, isdir, isfile, join as pathjoin
from pubsub import connect as pubsub_connect
from sys import exit

def install_service(name, options, services_dir, libraries_dir, docstore_url):
    service_dir = abspath(pathjoin(services_dir, name))
    sources = [service_dir, libraries_dir]
    install(name, sources, options, 'services', docstore_url)

def abspath_listdir(d):
    return [abspath(pathjoin(d, name)) for name in listdir(d)]

def publish_file(root, path, docstore):
    url_path = path[len(root):]
    with open(path, 'r') as f:
        data = f.read()
    docstore.put(data, url_path)

def is_valid_file(filename):
    return not basename(filename).startswith('.')

def publish_dir(root, path, docstore):
    contents = filter(is_valid_file, abspath_listdir(path))
    files = filter(isfile, contents)
    dirs = filter(isdir, contents)
    map(lambda f: publish_file(root, f, docstore), files)
    map(lambda d: publish_dir(root, d, docstore), dirs)

services_dir = abspath(pathjoin('..', 'services'))
games_dir = abspath(pathjoin('..', 'games'))
libraries_dir = abspath(pathjoin('..', 'libraries'))

with open(pathjoin(services_dir, 'services.json'), 'r') as config_file:
    config = load(config_file)
docstore_host = str(config['docstore_host'])
docstore_port = str(config['docstore_port'])
docstore_url = 'http://%s:%s' % (docstore_host, docstore_port)
pubsub_host = str(config['pubsub_host'])
pubsub_port = str(config['pubsub_port'])
pubsub_url = str(config['pubsub_url'])

services = [('docstore_server_http', [docstore_host, docstore_port]),
            ('emcee', [games_dir, libraries_dir, docstore_url]),
            ('pubsub_ws', [pubsub_host, pubsub_port, docstore_url]),
            ('executioner', [docstore_url])]

map(lambda (n, o): install_service(n, o, services_dir, libraries_dir,
                                   docstore_url),
    services)

docstore = docstore_connect(docstore_url)
if docstore.wait_until_up() is False:
    print 'Could not start docstore'
    exit(1)
docstore.put(pubsub_url, '/services/pubsub')

docstore_alex = docstore_connect(docstore_url + '/alexandra')
root = abspath('..')
publish_dir(root, root, docstore_alex)

print 'Now running'
raw_input('Press Enter to stop\n')

pubsub = pubsub_connect(pubsub_url, 'executioner')
pubsub.publish('kill', '"/services"')
