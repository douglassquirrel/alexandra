#! /usr/bin/python

from alexandra import Alexandra
from sys import argv

def publish_world(tick, alex, movement_queue, world):
    world['tick'] = tick
    movements = alex.pubsub.get_all_messages(movement_queue)
    tick_movements = filter(lambda(m): m['tick'] == tick - 1, movements)
    for m in tick_movements:
        entity, index, position = m['entity'], m['index'], m['to']
        name = '%s_%d' % (entity, index)
        world['entities'][name] = {'entity': entity, 'index': index,
                                   'position': position}
        world['movements'][name] = m
    alex.pubsub.publish('world', world)

alex = Alexandra(argv[1], argv[2])
movement_queue = alex.pubsub.subscribe('decision_movement.*')
world_monitor = alex.pubsub.make_topic_monitor('world')
initial_world = {'tick': 0, 'movements': {}, 'entities': {}}

tick_queue = alex.pubsub.subscribe('tick')
alex.pubsub.publish('world', initial_world)
alex.pubsub.consume_queue(tick_queue,
                          lambda t: publish_world(t, alex,
                                                  movement_queue,
                                                  world_monitor.latest()))
