#! /usr/bin/python

from docstore import connect as docstore_connect
from installer import install
from json import loads
from os.path import join as pathjoin
from pubsub import connect as pubsub_connect
from subprocess import call
from sys import argv

def start_game(message, games_dir, libraries_dir):
    game_info = loads(message)
    name, id = game_info['name'], game_info['id']
    game_dir = pathjoin(games_dir, name)

    install('run_components.%s' % (id,),
            [game_dir, 'run_components', libraries_dir],
            [id, docstore_url, libraries_dir])

games_dir, libraries_dir, docstore_url = argv[1:4]

docstore = docstore_connect(docstore_url)
pubsub_url = docstore.wait_and_get('/services/pubsub')
if pubsub_url is None:
    print 'No pubsub data on docstore, exiting'
    exit(1)
pubsub = pubsub_connect(pubsub_url, 'emcee')
pubsub.consume_topic('game.wanted', lambda m: start_game(m, games_dir, libraries_dir))
