#! /usr/bin/python

from os.path import abspath, join as pathjoin
from sys import path
path.insert(0, abspath(pathjoin('..', 'libraries')))

from docstore import connect as docstore_connect
from json import load
from os import listdir
from shepherd import Herd
from shutil import copy
from subprocess import Popen
from sys import exit
from tempfile import mkdtemp

install_dir = mkdtemp(prefix='emcee.')
print 'Installing services in %s' % (install_dir,)

services_dir = abspath(pathjoin('..', 'services'))
games_dir = abspath(pathjoin('..', 'games'))
libraries_dir = abspath(pathjoin('..', 'libraries'))

def full_path_listdir(d):
    return [pathjoin(d, name) for name in listdir(d)]

map(lambda f: copy(f, install_dir), full_path_listdir(services_dir))
map(lambda f: copy(f, install_dir), full_path_listdir(libraries_dir))

with open(pathjoin(services_dir, 'services.json'), 'r') as config_file:
    config = load(config_file)
docstore_host = config['docstore_host']
docstore_port = str(config['docstore_port'])
docstore_url = 'http://%s:%s' % (docstore_host, docstore_port)
pubsub_host = config['pubsub_host']
pubsub_port = str(config['pubsub_port'])
pubsub_url = config['pubsub_url']

def add_service(herd, executable, options):
    herd.add(pathjoin(install_dir, executable), options, install_dir)

options = {'emcee.py':                [games_dir, libraries_dir, docstore_url],
           'docstore_server_http.py': [docstore_host, docstore_port],
           'pubsub_ws.py':            [pubsub_host, pubsub_port, docstore_url]}

herd = Herd()
map(lambda (e, o): add_service(herd, e, o), options.items())
herd.start()

docstore = docstore_connect(docstore_url)
if docstore.wait_until_up() is False:
    print 'Could not start docstore'
    exit(1)
docstore.put(pubsub_url, '/services/pubsub', 'text/plain')

print 'Now running'
raw_input('Press Enter to stop\n')
herd.stop()
