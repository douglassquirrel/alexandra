#! /usr/bin/python

from alexandra import Alexandra
from json import dumps
from sys import argv

INDEX = int(argv[3])
NAME = 'player_%d' % (INDEX,)
WIDTH = 18
HEIGHT = 18
COLOUR = [0, 255, 255]
DELTAS = {'left': (-20, 0), 'right': (20, 0), 'up': (0, -20), 'down': (0, 20)}
MOVE_DELAY = 5

def init(alex):
    entity_data = {'width': WIDTH, 'height': HEIGHT, 'colour': COLOUR}
    alex.enter_in_library(dumps(entity_data),
                          '/player/player.json', 'application/json')
    return alex.subscribe('commands.player')

def update(world, commands_queue, alex):
    if NAME not in world['entities']:
        position = (alex.config['grid_start_x'] + 1,
                    alex.config['grid_start_y'] + 1)
        send_movement(position, position, world['tick'], alex)
    else:
        commands = commands_queue.fetch_all()
        if len(commands) > 0 and movement_ok(world):
            move(commands[-1], world, alex)

def movement_ok(world):
    if NAME not in world['movements']:
        return True

    last_movement = world['movements'][NAME]
    time_since_last_move = world['tick'] - last_movement['tick']
    return time_since_last_move >= MOVE_DELAY

def move(command, world, alex):
    position = world['entities'][NAME]['position']
    new_position = apply_command(command, position)
    send_movement(position, new_position, world['tick'], alex)

def apply_command(command, position):
    delta = DELTAS.get(command, (0, 0))
    return (position[0] + delta[0], position[1] + delta[1])

def send_movement(from_position, to_position, tick, alex):
    movement = {'tick': tick,
                'entity': 'player', 'index': INDEX,
                'from': from_position, 'to': to_position}
    alex.publish('movement.player', movement)

alex = Alexandra()
commands_queue = init(alex)
alex.consume('world', lambda w, a: update(w, commands_queue, a))
