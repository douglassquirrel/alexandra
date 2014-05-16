#! /usr/bin/python

from alexandra import Alexandra
from json import dumps
from sys import argv

def box_collisions(movement):
    return filter(lambda c: c['entity'] == 'box', movement['collisions'])

def check_movement(movement, alex):
    map(lambda c: do_collision_movement(movement, c, alex),
        box_collisions(movement))

def do_collision_movement(movement, collision, alex):
    index, from_position = collision['index'], collision['position']
    collider_from, collider_to = movement['from'], movement['to']
    delta = (collider_to[0] - collider_from[0],
             collider_to[1] - collider_from[1])
    if delta[0] == 0 and delta[1] == 0:
        return
    to_position = (from_position[0] + delta[0],
                   from_position[1] + delta[1])
    box_movement = {'tick': movement['tick'],
                    'entity': 'box', 'index': index,
                    'from': from_position, 'to': to_position}
    alex.pubsub.publish('movement.box', box_movement)

alex = Alexandra(argv[1], argv[2])
alex.pubsub.consume_topic('movement_with_collisions.*',
                          lambda m: check_movement(m, alex))
