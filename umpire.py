from json import dumps, load, loads
from pubsub import create_channel, publish, subscribe, unsubscribe, get_message
from time import sleep
from sys import exit
from urllib2 import URLError, urlopen

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self, vector):
        return Vector(self.x + vector.x, self.y + vector.y)

    def in_rect(self, rect):
        return rect.top_left._above_and_left_of(self) \
           and self._above_and_left_of(rect.bottom_right)

    def to_pair(self):
        return [self.x, self.y]

    def _above_and_left_of(self, vector):
        return self.x <= vector.x and self.y <= vector.y

class Rect:
    def __init__(self, top_left, bottom_right):
        self.top_left = top_left
        self.bottom_right = bottom_right

    def in_rect(self, rect):
        return self.top_left.in_rect(rect) and self.bottom_right.in_rect(rect)

    def move(self, v):
        return Rect(self.top_left.add(v), self.bottom_right.add(v))

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
            'width': 50,
            'height': 50,
            'library_url': library_url,
            'tick': config['tick_seconds']}

def main_loop(channel, movement_queue, field_rect, width, height, tick):
    while True:
        movement = get_movement(channel, movement_queue)
        if movement is not None:
            filter_movement(movement, field_rect, width, height)
        sleep(tick)

def filter_movement(movement, field_rect, width, height):
    entity = movement['entity']
    from_position, to_position = movement['from'], movement['to']
    from_rotation = movement['from_rotation']
    to_rotation = movement['to_rotation']

    if entity == 'player' and not is_legal(to_position[0], to_position[1],
                                           field_rect, width, height):
        new_position = from_position
    else:
        new_position = to_position

    approved_movement = {'entity': entity,
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
main_loop(channel, movement_queue, config['field_rect'],
          config['width'], config['height'], config['tick'])
