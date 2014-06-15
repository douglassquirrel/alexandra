#! /usr/bin/env python

from alexandra import Alexandra
from sys import argv

def is_trigger(movement):
    entity = movement['entity']
    return entity.startswith('player') or entity.startswith('wall')

def ok_movement(movements):
    return len(filter(is_trigger, movements)) > 0

def player_trigger(tick, movements):
    two_ticks_ago = filter(lambda m: m['tick'] == tick-2, movements)
    return len(filter(lambda m: m['entity'].startswith('player'),
                      two_ticks_ago)) > 0

def publish_world(tick, alex, movement_queue, world):
    world['tick'] = tick
    queue_movements = alex.pubsub.get_all_messages(movement_queue)
    if not player_trigger(tick, world['movements'].values()) \
            and not ok_movement(queue_movements):
        if tick % 10 == 0:
            alex.pubsub.publish('world', world)
        return

    last_tick_movements = filter(lambda(m): m['tick'] == tick - 1,
                                 queue_movements)
    for m in last_tick_movements:
        entity, index, position = m['entity'], m['index'], m['to']
        name = '%s_%d' % (entity, index)
        world['entities'][name] = {'entity': entity, 'index': index,
                                   'position': position}
        world['movements'][name] = m
    alex.pubsub.publish('world', world)

alex = Alexandra(argv[1])
movement_queue = alex.pubsub.subscribe('decision_movement.*')
world_monitor = alex.pubsub.make_topic_monitor('world')
initial_world = {'tick': 0, 'movements': {}, 'entities': {}}

tick_queue = alex.pubsub.subscribe('tick')
alex.pubsub.publish('world', initial_world)
alex.pubsub.consume_queue(tick_queue,
                          lambda t: publish_world(t, alex,
                                                  movement_queue,
                                                  world_monitor.latest()))
