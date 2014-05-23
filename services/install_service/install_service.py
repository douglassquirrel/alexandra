#! /usr/bin/python

from docstore import connect as docstore_connect
from installer import install_docstore
from json import loads
from pubsub import connect as pubsub_connect
from sys import argv

def install(process_info, docstore_url):
    name         = process_info['name']
    sources      = process_info['sources']
    options      = process_info['options']
    group        = process_info.get('group', None)
    copies       = process_info.get('copies', 1)
    install_docstore(name, sources, options, docstore_url, group, copies)

docstore_url = argv[1]
docstore = docstore_connect(docstore_url)
pubsub_url = docstore.wait_and_get('/services/pubsub')
if pubsub_url is None:
    print 'No pubsub data on docstore, exiting'
    exit(1)
pubsub = pubsub_connect(pubsub_url, 'process', unmarshal=loads)
pubsub.consume_topic('install', lambda m: install(m, docstore_url))
