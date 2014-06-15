#! /usr/bin/env python

from alexandra import Alexandra
from sys import argv

def check_movement(movement, alex):
    return movement['to'][0] >= 0 \
       and movement['to'][1] >= 0 \
       and movement['to'][0] < alex.config['field_width'] - 50\
       and movement['to'][1] < alex.config['field_height'] - 50\
       and len(movement['collisions']) == 0

def check_timing(world, movement):
    entity = movement['entity']
    tick = movement['tick']

    if entity.startswith('player') or entity.startswith('wall'):
        return True

    movements = world['movements'].values()
    is_player_last_tick = lambda m: m['tick'] == tick - 1 and \
                                    m['entity'].startswith('player')
    return len(filter(is_player_last_tick, movements)) > 0

def filter_movement(movement, world, alex):
    entity = movement['entity']
    from_position, to_position = movement['from'], movement['to']

    if check_timing(world, movement) is False:
        return

    if check_movement(movement, alex) is True:
        new_position = to_position
    else:
        new_position = from_position

    approved_movement = {'tick': movement['tick'],
                         'entity': entity,
                         'index': movement['index'],
                         'from': from_position, 'to': new_position}
    alex.pubsub.publish('decision_movement.' + entity, approved_movement)

alex = Alexandra(argv[1])
world_monitor = alex.pubsub.make_topic_monitor('world')
alex.pubsub.consume_topic('movement_with_collisions.*',
                          lambda m: filter_movement(m, world_monitor.latest(),
                                                    alex))
