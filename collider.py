from alexandra import Alexandra
from json import load
from vector import Vector, Rect

def add_collisions(movement, alex):
    movement['collisions'] = collisions(movement, alex.world.copy())
    alex.publish('movement_with_collisions.' + movement['entity'],
                 movement)

def collisions(movement, world):
    del world['tick']

    dimensions = {}
    entities = world.values()
    detector = make_collision_detector(world, movement, alex, dimensions)
    return filter(lambda(x): x is not None, map(detector, entities))

def make_collision_detector(world, movement, alex, dimensions):
    moving_entity = movement['entity']
    moving_rect = get_rect_for(moving_entity, movement['to'], alex, {})
    return lambda(e): get_collision(e, moving_entity, moving_rect, alex,
                                    dimensions)

def get_collision(entity_data, moving_entity, moving_rect, alex, dimensions):
    entity, position = entity_data['entity'], entity_data['position']
    rect = get_rect_for(entity, position, alex, dimensions)
    if entity != moving_entity and rect.intersects(moving_rect):
        return entity_data
    else:
        return None

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
alex.monitor(movement_queue, add_collisions)
