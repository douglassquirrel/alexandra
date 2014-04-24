#! /usr/bin/python

from alexandra import Alexandra

def publish_world(tick, alex, movements, world):
    world['tick'] = tick
    tick_movements = filter(lambda(m): m['tick'] == tick - 1, movements)
    for m in tick_movements:
        entity, index, position = m['entity'], m['index'], m['to']
        name = '%s_%d' % (entity, index)
        world['entities'][name] = {'entity': entity, 'position': position}
        world['movements'][name] = m
    alex.publish('world', world)

alex = Alexandra()
movement_queue = alex.subscribe('decision_movement.*')
world_monitor = alex.topic_monitor('world')
initial_world = {'tick': 0, 'movements': {}, 'entities': {}}

alex.consume('tick',
             lambda t, a: publish_world(t, a,
                                        movement_queue.fetch_all(),
                                        world_monitor.latest()),
             initial=lambda: alex.publish('world', initial_world))
