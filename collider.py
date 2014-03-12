from alexandra import Alexandra
from json import load
from time import sleep
from vector import Vector, Rect

def main_loop(alex, movement_queue):
    while True:
        movement = movement_queue.next()
        if movement is not None:
            movement['collisions'] = collisions(movement, alex.world.copy())
            alex.publish('movement_with_collisions.' + movement['entity'],
                         movement)
        sleep(alex.config['tick_seconds']/5.0)

def collisions(movement, world):
    del world['tick']
    moving_entity = movement['entity']
    moving_rect = get_rect_for(moving_entity, movement['to'], alex, {})

    collisions = []
    dimensions = {}
    for entity_data in world.values():
        entity, position = entity_data['entity'], entity_data['position']
        if entity == moving_entity:
            continue
        rect = get_rect_for(entity, position, alex, dimensions)
        if rect.intersects(moving_rect):
            collisions.append(entity_data)
    return collisions

def get_rect_for(entity, position, alex, dimensions):
    width, height = get_dimensions(entity, alex, dimensions)
    top_left = Vector.frompair(position)
    bottom_right = top_left.add(Vector(width, height))
    return Rect(top_left, bottom_right)

def get_dimensions(entity, library_url, dimensions):
    if entity not in dimensions:
        data = load(alex.get_library_file('/%s/%s.json' % (entity, entity)))
        dimensions[entity] = (data['width'], data['height'])
    return dimensions[entity]

alex = Alexandra(subscribe_world=True)
movement_queue = alex.subscribe('movement.*')
main_loop(alex, movement_queue)
