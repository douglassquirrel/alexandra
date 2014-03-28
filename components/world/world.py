#! /usr/bin/python

from alexandra import Alexandra

alex = Alexandra(subscribe_world=False)
world = {'tick': 0, 'movements': {}, 'entities': {}}
movement_queue = alex.subscribe('decision_movement.*')

def publish_world(tick, alex):
    world['tick'] = tick
    world['movements'] = {}
    all_movements = movement_queue.fetch_all()
    tick_movements = filter(lambda(m): m['tick'] == tick - 1, all_movements)
    if len(tick_movements) < len(all_movements):
        print 'Dropping movement(s) on tick %d' % tick
    for m in tick_movements:
        entity, index, position = m['entity'], m['index'], m['to']
        name = '%s_%d' % (entity, index)
        world['entities'][name] = {'entity': entity, 'position': position}
        world['movements'][name] = m
    alex.publish('world', world)

alex.consume('tick', publish_world)
