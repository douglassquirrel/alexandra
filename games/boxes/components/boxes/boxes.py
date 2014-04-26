#! /usr/bin/python

from alexandra import Alexandra
from json import dumps
from random import choice as randomchoice
from sys import argv

WIDTH = 20
HEIGHT = 20
COLOUR = [25, 170, 0]
DELTAS = [(-20, 0), (20, 0), (0, 20), (0, 20)]

def init(alex):
    alex.enter_in_library(dumps({'width': WIDTH, 'height': HEIGHT,
                                 'colour': COLOUR}),
                          '/box/box.json',
                          'application/json')
    initial_positions = set()
    while len(initial_positions) < alex.config['number_boxes']:
        initial_positions.add(random_start_position(alex))
    return list(initial_positions)

def random_start_position(alex):
    max_width = (alex.config['field_width'] - alex.config['grid_start_x'])
    grid_width = max_width / WIDTH
    max_height = (alex.config['field_height'] - alex.config['grid_start_y'])
    grid_height = max_height / HEIGHT
    return (randomchoice(range(grid_width)) * WIDTH,
            randomchoice(range(grid_height)) * HEIGHT)

def move(world, alex, initial_positions):
    for index in range(0, alex.config['number_boxes']):
        move_box(index, world, alex, initial_positions)

def move_box(index, world, alex, initial_positions):
    name = 'box_%d' % (index,)
    if name not in world['entities']:
        position = initial_positions[index]
        send_movement(index, position, position, world['tick'], alex)
    else:
        pass

def send_movement(index, from_position, to_position, tick, alex):
    movement = {'tick': tick,
                'entity': 'box', 'index': index,
                'from': from_position, 'to': to_position}
    alex.publish('movement.box', movement)

alex = Alexandra()
initial_positions = init(alex)
alex.consume('world', lambda w, a: move(w, a, initial_positions))
