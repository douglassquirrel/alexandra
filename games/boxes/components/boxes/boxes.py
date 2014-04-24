#! /usr/bin/python

from alexandra import Alexandra
from json import dumps
from sys import argv

NAME = 'box'
INDEX = 0
WIDTH = 20
HEIGHT = 20
COLOUR = [25, 170, 0]
DELTAS = [(-20, 0), (20, 0), (0, 20), (0, 20)]

def init(alex):
    alex.enter_in_library(dumps({'width': WIDTH, 'height': HEIGHT,
                                 'colour': COLOUR}),
                          '/box/box.json',
                          'application/json')

def move(world, alex):
    if NAME not in world['entities']:
        position = (alex.config['player_start_x'] + 19,
                    alex.config['player_start_y'] - 1)
        send_movement(position, position, world['tick'], alex)
        return

def send_movement(from_position, to_position, tick, alex):
    movement = {'tick': tick,
                'entity': 'box', 'index': INDEX,
                'from': from_position, 'to': to_position}
    alex.publish('movement.box', movement)

alex = Alexandra()
init(alex)
alex.consume('world', move)
