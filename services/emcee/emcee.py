#! /usr/bin/python

from docstore import connect as docstore_connect
from installer import install_docstore
from json import loads
from pubsub import connect as pubsub_connect
from sys import argv

def start_game(game_info, docstore_url):
    name, id = game_info['name'], game_info['id']
    sources = ['/games/%s' % (name,),
               '/services/emcee/run_components',
               '/libraries']
    install_docstore('run_components.%s' % (id,), sources,
                     [id, name, docstore_url], docstore_url)

docstore_url = argv[1]
docstore = docstore_connect(docstore_url)
pubsub_url = docstore.wait_and_get('/services/pubsub')
if pubsub_url is None:
    print 'No pubsub data on docstore, exiting'
    exit(1)
pubsub = pubsub_connect(pubsub_url, 'emcee', unmarshal=loads)
pubsub.consume_topic('game.wanted', lambda m: start_game(m, docstore_url))
