from alexandra import Alexandra
from time import sleep

def main_loop(alex, movement_queue):
    while True:
        movement = movement_queue.next()
        if movement is not None:
            filter_movement(alex, movement)
        sleep(alex.config['tick_seconds']/5.0)

def filter_movement(alex, movement):
    entity = movement['entity']
    from_position, to_position = movement['from'], movement['to']

    if entity != 'player' or len(movement['collisions']) == 0:
        new_position = to_position
    else:
        new_position = from_position

    approved_movement = {'entity': entity,
                         'index': movement['index'],
                         'from': from_position, 'to': new_position}
    alex.publish('decision.movement.' + entity, approved_movement)

alex = Alexandra()
movement_queue = alex.subscribe('movement_with_collisions.*')
main_loop(alex, movement_queue)
