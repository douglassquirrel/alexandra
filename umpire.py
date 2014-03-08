from json import dumps, load, loads
from pubsub import create_channel, publish, subscribe, unsubscribe, get_message
from time import sleep
from sys import exit
from urllib2 import URLError, urlopen
from vector import Vector, Rect

def init():
    channel = create_channel()
    config = init_config(channel)
    movement_queue = subscribe(channel, 'movement.*')

    return channel, movement_queue, config

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

    return {'field_rect': Rect(Vector(0, 0),
                               Vector(config['field_width'],
                                      config['field_height'])),
            'library_url': library_url,
            'tick': config['tick_seconds']}

def main_loop(channel, movement_queue, field_rect, library_url, tick):
    while True:
        movement = get_movement(channel, movement_queue)
        if movement is not None:
            filter_movement(movement, field_rect, library_url)
        sleep(tick)

def filter_movement(movement, field_rect, library_url):
    entity = movement['entity']
    entity_data_url = '%s/%s/%s.json' % (library_url, entity, entity)
    entity_data = load(urlopen(entity_data_url))
    width, height = entity_data['width'], entity_data['height']

    from_position, to_position = movement['from'], movement['to']
    from_rotation = movement['from_rotation']
    to_rotation = movement['to_rotation']

    if is_legal(to_position[0], to_position[1], field_rect, width, height):
        new_position = to_position
    else:
        new_position = from_position

    approved_movement = {'entity': entity,
                         'index': movement['index'],
                         'from': from_position, 'to': new_position,
                         'from_rotation': from_rotation,
                         'to_rotation': to_rotation}
    publish(channel, 'decision.movement.' + entity,
            dumps(approved_movement))

def is_legal(new_x, new_y, field_rect, width, height):
    top_left = Vector(new_x, new_y)
    bottom_right = top_left.add(Vector(width, height))
    new_rect = Rect(top_left, bottom_right)
    return new_rect.in_rect(field_rect)

def get_movement(channel, movement_queue):
    message = get_message(channel, movement_queue)
    if message:
        return loads(message)
    else:
        return None

channel, movement_queue, config = init()
main_loop(channel, movement_queue, config['field_rect'], config['library_url'],
          config['tick'])
