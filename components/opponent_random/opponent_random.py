#! /usr/bin/python

from alexandra import Alexandra
from json import dumps
from random import choice as randomchoice
from sys import argv

INDEX = int(argv[2])
NAME = 'opponent_random_%d' % (INDEX,)
WIDTH = 20
HEIGHT = 20
COLOUR = [255, 0, 0]
DELTAS = [(-5, 0), (5, 0), (0, -5), (0, 5)]

def init(alex):
    alex.enter_in_library(dumps({'width': WIDTH, 'height': HEIGHT,
                                 'colour': COLOUR}),
                          '/opponent_random/opponent_random.json',
                          'application/json')

def move(alex):
    if NAME not in alex.world['entities']:
        position = (alex.config['player_start_x'] + 80 * (INDEX + 1),
                    alex.config['player_start_y'])
        send_movement(position, position, alex)
        return

    if NAME not in alex.world['movements']:
        delta = randomchoice(DELTAS)
    else:
        movement = alex.world['movements'][NAME]
        delta = (movement['to'][0] - movement['from'][0],
                 movement['to'][1] - movement['from'][1])
        if delta[0] == 0 and delta[1] == 0:
            delta = randomchoice(DELTAS)

    position = alex.world['entities'][NAME]['position']
    new_position = (position[0] + delta[0], position[1] + delta[1])
    send_movement(position, new_position, alex)

def send_movement(from_position, to_position, alex):
    movement = {'entity': 'opponent_random', 'index': INDEX,
                'from': from_position, 'to': to_position}
    alex.publish('movement.player', movement)

alex = Alexandra(subscribe_world=True)
init(alex)
alex.wait_for_start()
alex.on_each_tick(move)
alex.wait()
