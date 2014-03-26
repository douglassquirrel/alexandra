#! /usr/bin/python

from alexandra import Alexandra

alex = Alexandra(subscribe_world=False)
world = {'tick': 0, 'movements': {}, 'entities': {}}
movement_queue = alex.subscribe('decision_movement.*')

def publish_world(tick, alex):
    world['tick'] = tick
    world['movements'] = {}
    for m in movement_queue.fetch_all():
        entity, index, position = m['entity'], m['index'], m['to']
        name = '%s_%d' % (entity, index)
        world['entities'][name] = {'entity': entity, 'position': position}
        world['movements'][name] = m
    alex.publish('world', world)

alex.each_tick(publish_world)
