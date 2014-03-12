from alexandra import Alexandra
from time import sleep

def main_loop(alex):
    movement_queue = alex.subscribe('decision.movement.*')
    world = {'tick': 0}
    while True:
        world['tick'] += 1
        for movement in movement_queue.fetch_all():
            entity = movement['entity']
            index = movement['index']
            position = movement['to']
            name = '%s_%d' % (entity, index)
            world[name] = {'entity': entity, 'position': position}
        alex.publish('world', world)
        sleep(alex.config['tick_seconds'])

main_loop(Alexandra())
