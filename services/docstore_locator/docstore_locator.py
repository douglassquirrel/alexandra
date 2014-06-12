#! /usr/bin/env python

from pubsub import connect as pubsub_connect
from sys import argv

def locate(message, pubsub, docstore_url):
    pubsub.publish('location', docstore_url)

docstore_url, pubsub_url = argv[1:3]
pubsub = pubsub_connect(pubsub_url, 'docstore')
pubsub.consume_topic('locate', lambda m: locate(m, pubsub, docstore_url))
