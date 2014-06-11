#! /usr/bin/python

HEARTBEAT_TIMEOUT = 5

from json import load, dumps
from os import getenv
from pubsub import connect as pubsub_connect
from sys import argv

def heart_monitor(game_id, pubsub):
    heartbeat_queue = pubsub.subscribe('heartbeat')
    message = ''
    while message is not None:
        message = pubsub.get_message_block(queue=heartbeat_queue,
                                           timeout=HEARTBEAT_TIMEOUT)

game_id, game_name = argv[1:3]
with open('game.json', 'r') as game_file:
    game_data = load(game_file)
pubsub_url = getenv('ALEXANDRA_PUBSUB')
game_pubsub = pubsub_connect(pubsub_url, 'games/' + game_id, marshal=dumps)
game_pubsub.publish('game.json', game_data)

process_pubsub = pubsub_connect(pubsub_url, 'process', marshal=dumps)
for (comp_name, copies) in game_data['components'].items():
    sources = ['/games/%s/components/%s' % (game_name, comp_name), '/libraries']
    install_message = {'name': comp_name,
                       'sources': sources,
                       'options': [game_id],
                       'group': game_id,
                       'copies': copies}
    process_pubsub.publish('install', install_message)

game_pubsub = pubsub_connect(pubsub_url, 'games/' + game_id)
game_pubsub.publish('game_state', 'running')
print 'Now running game %s' % (game_id,)
heart_monitor(game_id, game_pubsub)

print 'Game %s ending' % (game_id,)
process_pubsub.publish('kill', '/%s' % (game_id,))
