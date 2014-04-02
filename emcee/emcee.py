#! /usr/bin/python

from json import loads
from pubsub import Connection
from sys import argv

def start_game(message):
    game_info = loads(message)
    name, id = game_info['name'], game_info['id']
    print 'Starting game %s with id %s' % (name, id)

connection = Connection('emcee')
queue = connection.subscribe('game.wanted')
connection.consume(queue, start_game)
