#! /usr/bin/python

from alexandra import Alexandra

def check_movement(movement, alex):
    return movement['to'][0] >= 0 \
       and movement['to'][1] >= 0 \
       and movement['to'][0] < alex.config['field_width'] - 50\
       and movement['to'][1] < alex.config['field_height'] - 50\
       and (movement['entity'].startswith('wall') \
                or len(movement['collisions']) == 0)

def filter_movement(movement, alex):
    entity = movement['entity']
    from_position, to_position = movement['from'], movement['to']

    if check_movement(movement, alex) is True:
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
