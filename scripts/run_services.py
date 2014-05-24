#! /usr/bin/python

from os.path import abspath, join as pathjoin
from sys import path
path.insert(0, abspath(pathjoin('..', 'libraries')))
path.insert(0, abspath(pathjoin('..', 'infralib')))

from docstore import connect as docstore_connect
from installer import install_dir, install_docstore
from json import load, loads, dumps
from publish_dir import publish_dir
from pubsub import connect as pubsub_connect
from sys import exit
from time import sleep     

services_dir = abspath(pathjoin('..', 'services'))
libraries_dir = abspath(pathjoin('..', 'libraries'))

with open(pathjoin(services_dir, 'services.json'), 'r') as config_file:
    config = load(config_file)
docstore_host = str(config['docstore_host'])
docstore_port = str(config['docstore_port'])
docstore_url = 'http://%s:%s' % (docstore_host, docstore_port)
pubsub_url = str(config['pubsub_url'])
pubsub = pubsub_connect(pubsub_url, 'process', marshal=dumps)

docstore_dir = abspath(pathjoin(services_dir, 'docstore_server_http'))
install_dir('docstore_server_http', [docstore_dir, libraries_dir],
            [docstore_host, docstore_port], docstore_url, 'services')

docstore = docstore_connect(docstore_url)
if docstore.wait_until_up() is False:
    print 'Could not start docstore'
    exit(1)
docstore.put(pubsub_url, '/services/pubsub')
docstore_alex = docstore_connect(docstore_url + '/alexandra')
root = abspath('..')
publish_dir(root, root, docstore_alex)

install_docstore('install_service',
                 ['/services/install_service', '/libraries', '/infralib'],
                 [docstore_url], docstore_url, 'services')
sleep(1)

for name in ['emcee', 'pubsub_ws', 'executioner']:
    install_message = {'name': name,
                       'sources': ['/services/%s' % (name,), '/libraries'],
                       'options': [docstore_url],
                       'group': 'services'}
    pubsub.publish('install', install_message)

print 'Now running'
raw_input('Press Enter to stop\n')

pubsub.publish('kill', '/services')
