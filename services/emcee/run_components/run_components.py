#! /usr/bin/python

HEARTBEAT_TIMEOUT = 5

from docstore import connect as docstore_connect
from installer import install
from json import load, dumps
from os.path import join as pathjoin
from pubsub import connect as pubsub_connect
from sys import argv

def install_component(name, game_id, copies,
                      libraries_dir, options, docstore_url):
    sources = [pathjoin('components', name), libraries_dir]
    install(name, sources, options, game_id, docstore_url, copies)

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

for (name, copies) in game_data['components'].items():
    install_component(name, game_id, copies, libraries_dir,
                      [docstore_url, game_id], docstore_url)

pubsub_url = docstore_connect(docstore_url).get('/services/pubsub')
game_pubsub = pubsub_connect(pubsub_url, game_id)
game_pubsub.publish('game_state', 'running')
print 'Now running game %s' % (game_id,)
heart_monitor(game_id, game_pubsub)

print 'Game %s ending' % (game_id,)
executioner_pubsub = pubsub_connect(pubsub_url, 'executioner')
executioner_pubsub.publish('kill', '"/%s"' % (game_id,))
