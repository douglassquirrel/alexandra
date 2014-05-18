#! /usr/bin/python

HEARTBEAT_TIMEOUT = 5

from docstore import connect as docstore_connect
from installer import install
from json import load, dumps
from os.path import join as pathjoin
from pubsub import connect as pubsub_connect
from sys import argv

def install_component(name, copies, libraries_dir, options):
    sources = [pathjoin('components', name), libraries_dir]
    return install(name, sources, options, copies)

def heart_monitor(game_id, pubsub):
    heartbeat_queue = pubsub.subscribe('heartbeat')
    message = ''
    while message is not None:
        message = pubsub.get_message_block(queue=heartbeat_queue,
                                           timeout=HEARTBEAT_TIMEOUT)

game_id, docstore_url, libraries_dir = argv[1], argv[2], argv[3]
with open('game.json', 'r') as game_file:
    game_data = load(game_file)
docstore = docstore_connect(docstore_url + "/" + game_id)
docstore.put(dumps(game_data), '/game.json', 'application/json')

options = [docstore_url, game_id]
procs = []
for (name, copies) in game_data['components'].items():
    procs += install_component(name, copies, libraries_dir, options)

pubsub_url = docstore_connect(docstore_url).get('/services/pubsub')
pubsub = pubsub_connect(pubsub_url, game_id)
pubsub.publish('game_state', 'running')
print 'Now running game %s' % (game_id,)
heart_monitor(game_id, pubsub)

print 'Game %s ending' % (game_id,)
map(lambda p: p.kill(), procs)
