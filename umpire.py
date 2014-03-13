from alexandra import Alexandra
from time import sleep

def filter_movement(movement, alex):
    entity = movement['entity']
    from_position, to_position = movement['from'], movement['to']

    if entity != 'player' or len(movement['collisions']) == 0:
        new_position = to_position
    else:
        new_position = from_position

    approved_movement = {'entity': entity,
                         'index': movement['index'],
                         'from': from_position, 'to': new_position}
    alex.publish('decision_movement.' + entity, approved_movement)

alex = Alexandra()
movement_queue = alex.subscribe('movement_with_collisions.*')
alex.monitor(movement_queue, filter_movement)
