#! /usr/bin/python

from alexandra import Alexandra
from json import dumps
from random import choice as randomchoice
from sys import argv

WIDTH = 15
HEIGHT = 15
CELL_DIM = 20
DISPLACEMENT = 5
COLOUR = [25, 170, 0]
DELTAS = [(-20, 0), (20, 0), (0, 20), (0, 20)]

def init(alex):
    alex.docstore.put(dumps({'width': WIDTH, 'height': HEIGHT,
                             'colour': COLOUR}),
                      '/box/box.json',
                      'application/json')
    initial_positions = set()
    while len(initial_positions) < alex.config['number_boxes']:
        initial_positions.add(random_start_position(alex))
    return list(initial_positions)

def random_start_position(alex):
    grid_width = alex.config['field_width'] / CELL_DIM
    grid_height = alex.config['field_height'] / CELL_DIM
    return (randomchoice(range(grid_width)) * CELL_DIM + DISPLACEMENT,
            randomchoice(range(grid_height)) * CELL_DIM + DISPLACEMENT)

def place(world, alex, initial_positions):
    for index in range(0, alex.config['number_boxes']):
        place_box(index, world, alex, initial_positions)

def place_box(index, world, alex, initial_positions):
    name = 'box_%d' % (index,)
    if name not in world['entities']:
        position = initial_positions[index]
        send_movement(index, position, position, world['tick'], alex)

def send_movement(index, from_position, to_position, tick, alex):
    movement = {'tick': tick,
                'entity': 'box', 'index': index,
                'from': from_position, 'to': to_position}
    alex.pubsub.publish('movement.box', movement)

alex = Alexandra(argv[1], argv[2])
initial_positions = init(alex)
alex.pubsub.consume_topic('world', lambda w: place(w, alex, initial_positions))
