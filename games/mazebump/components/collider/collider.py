#! /usr/bin/env python

from alexandra import Alexandra
from json import loads
from sys import argv
from vector import Vector, Rect

def add_collisions(movement, world, alex):
    if world is None:
        return
    movement['collisions'] = collisions(movement, world['entities'])
    alex.pubsub.publish('movement_with_collisions.' + movement['entity'],
                        movement)

def collisions(movement, entities_dict):
    entities = entities_dict.values()
    detector = make_collision_detector(movement, alex)
    return filter(None, [detector(e) for e in entities])

def make_collision_detector(movement, alex):
    moving_entity = movement['entity']
    moving_entity_data = alex.pubsub.get_current_message('%s/%s.json' % (moving_entity, moving_entity))
    if moving_entity_data is None:
        return None
    moving_rect = get_rect_for(moving_entity_data, movement['to'], alex)
    return lambda(e): get_collision(e, moving_entity, moving_rect, alex)

def get_collision(entity_data, moving_entity, moving_rect, alex):
    entity, position = entity_data['entity'], entity_data['position']
    entity_data = alex.pubsub.get_current_message('%s/%s.json' % (entity, entity))
    if entity_data is None:
        return None
    rect = get_rect_for(entity_data, position, alex)
    if entity != moving_entity and rect.intersects(moving_rect):
        return entity_data
    else:
        return None

def get_rect_for(entity_data, position, alex):
    width, height = entity_data['width'], entity_data['height']
    top_left = Vector.frompair(position)
    bottom_right = top_left.add(Vector(width, height))
    return Rect(top_left, bottom_right)

alex = Alexandra(argv[1])
world_monitor = alex.pubsub.make_topic_monitor('world')
alex.pubsub.consume_topic('movement.*',
                  lambda m: add_collisions(m, world_monitor.latest(), alex))
