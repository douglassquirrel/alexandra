#! /usr/bin/python

from alexandra import Alexandra
from json import dumps

def box_collisions(movement):
    return filter(lambda c: c['entity'] == 'box', movement['collisions'])

def check_movement(movement, alex):
    map(lambda c: do_collision_movement(movement, c, alex),
        box_collisions(movement))

def do_collision_movement(movement, collision, alex):
    index = collision['index']
    from_position = collision['position']
    collider_from = movement['from']
    collider_to = movement['to']
    delta = (collider_to[0] - collider_from[0],
             collider_to[1] - collider_from[1])
    to_position = (from_position[0] + delta[0],
                   from_position[1] + delta[1])         
    box_movement = {'tick': movement['tick'],
                    'entity': 'box', 'index': index,
                    'from': from_position, 'to': to_position}
    alex.publish('movement.box', box_movement)

alex = Alexandra()
alex.consume('movement_with_collisions.*', check_movement)
