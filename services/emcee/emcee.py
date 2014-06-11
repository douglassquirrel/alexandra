#! /usr/bin/python

from json import loads, dumps
from os import getenv
from pubsub import connect as pubsub_connect
from sys import argv

def start_game(game_info, pubsub_url):
    name, id = game_info['name'], game_info['id']
    sources = ['/games/%s' % (name,),
               '/services/emcee/run_components',
               '/libraries']
    pubsub = pubsub_connect(pubsub_url, 'process', marshal=dumps)

    install_message = {'name': 'run_components.%s' % (id,),
                       'sources': sources,
                       'options': [id, name]}
    pubsub.publish('install', install_message)

pubsub_url = getenv('ALEXANDRA_PUBSUB')
pubsub = pubsub_connect(pubsub_url, 'emcee', unmarshal=loads)
pubsub.consume_topic('game.wanted', lambda m: start_game(m, pubsub_url))
