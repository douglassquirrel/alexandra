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
    while True:
        world = loads(get_message_block(channel, world_queue))
        del world['tick']
        movements = get_all_messages(channel, movement_queue)
        for movement in movements:
            check(loads(movement), world, library_url)

def check(movement, world, library_url):
    moving_entity = movement['entity']
    moving_rect = get_rect_for(moving_entity, movement['to'], library_url)

    for entity_data in world.values():
        entity, position = entity_data['entity'], entity_data['position']
        if entity == moving_entity:
            continue
        rect = get_rect_for(entity, position, library_url)
        if rect.intersects(moving_rect):
            print 'Collision: %s hits %s' % (movement, entity_data)

def get_rect_for(entity, position, library_url):
    url = '%s/%s/%s.json' % (library_url, entity, entity)
    data = load(urlopen(url))
    top_left = Vector.frompair(position)
    bottom_right = top_left.add(Vector(data['width'], data['height']))
    return Rect(top_left, bottom_right)

channel, world_queue, movement_queue, config = init()
main_loop(channel, world_queue, movement_queue,
          config['library_url'], config['tick'])
