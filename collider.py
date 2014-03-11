from json import dumps, load, loads
from pubsub import create_channel, publish, subscribe, unsubscribe, \
                   get_all_messages, get_message, get_message_block
from time import sleep
from sys import exit
from urllib2 import URLError, urlopen
from vector import Vector, Rect

def init():
    channel = create_channel()
    config = init_config(channel)
    world_queue = subscribe(channel, 'world')
    movement_queue = subscribe(channel, 'movement.*')

    return channel, world_queue, movement_queue, config

def init_config(channel):
    queue = subscribe(channel, 'library_url')
    sleep(1)
    library_url = get_message(channel, queue)
    if not library_url:
        print "No library url published, cannot fetch config"
        exit(1)
    unsubscribe(channel, queue, 'library_url')

    config_url = library_url + '/config.json'
    try:
        config_file = urlopen(config_url)
    except URLError:
        print "No config file at %s" % (config_url,)
        exit(1)
    config = load(config_file)

    return {'library_url': library_url,
            'tick': config['tick_seconds']}

def main_loop(channel, world_queue, movement_queue, library_url, tick):
    world = loads(get_message_block(channel, world_queue))
    del world['tick']
    while True:
        new_world = get_message(channel, world_queue)
        if new_world is not None:
            world = loads(new_world)
            del world['tick']

        movements = get_all_messages(channel, movement_queue)
        for m in movements:
            movement = loads(m)
            movement['collisions'] = collisions(movement, world, library_url)
            publish(channel, 'movement_with_collisions.' + movement['entity'],
                    dumps(movement))
        sleep(tick/5.0)

def collisions(movement, world, library_url):
    moving_entity = movement['entity']
    moving_rect = get_rect_for(moving_entity, movement['to'], library_url, {})

    collisions = []
    dimensions = {}
    for entity_data in world.values():
        entity, position = entity_data['entity'], entity_data['position']
        if entity == moving_entity:
            continue
        rect = get_rect_for(entity, position, library_url, dimensions)
        if rect.intersects(moving_rect):
            collisions.append(entity_data)
    return collisions

def get_rect_for(entity, position, library_url, dimensions):
    width, height = get_dimensions(entity, library_url, dimensions)
    top_left = Vector.frompair(position)
    bottom_right = top_left.add(Vector(width, height))
    return Rect(top_left, bottom_right)

def get_dimensions(entity, library_url, dimensions):
    if entity not in dimensions:
        url = '%s/%s/%s.json' % (library_url, entity, entity)
        data = load(urlopen(url))
        dimensions[entity] = (data['width'], data['height'])
    return dimensions[entity]

channel, world_queue, movement_queue, config = init()
main_loop(channel, world_queue, movement_queue,
          config['library_url'], config['tick'])
