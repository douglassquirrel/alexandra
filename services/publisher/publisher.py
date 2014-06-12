#! /usr/bin/env python

from docstore import connect as docstore_connect
from os import getenv
from pubsub import firehose
from sys import argv

def publish(context, topic, message, docstore):
    docstore.put(message, '/%s/%s' % (context, topic))

docstore_url = argv[1]
docstore = docstore_connect(docstore_url)
pubsub_url = getenv('ALEXANDRA_PUBSUB')
pubsub = firehose(pubsub_url)
pubsub.consume_all(lambda c,t,m: publish(c, t, m, docstore))
