from json import dumps, load, loads
from pika import BlockingConnection, ConnectionParameters
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
    channel = init_channel()
    config = init_config(channel)
    rect = Rect(config['start'],
                config['start'].add(Vector(config['width'], config['height'])))
    send_position(rect.top_left, channel)

    return channel, rect, config

def init_config(channel):
    channel.queue_declare(queue='library_url')
    sleep(1)
    library_url = channel.basic_get(0, 'library_url', no_ack=True)[2]
    if not library_url:
        print "No library url published, cannot fetch config - exiting player"
        exit(1)

    config_url = library_url + '/config.json'
    try:
        config_file = urlopen(config_url)
    except URLError:
        print "No config file at %s - exiting player" % (config_url,)
        exit(1)
    config = load(config_file)

    return {'field_rect': Rect(Vector(0, 0),
                               Vector(config['field_width'],
                                      config['field_height'])),
            'start': Vector(config['player_start_x'], config['player_start_y']),
            'width': 50,
            'height': 50,
            'tick': config['tick_seconds'],
            'deltas': {'left': Vector(-5, 0), 'right': Vector(5, 0),
                       'up': Vector(0, -5), 'down': Vector(0, 5)}}

def init_channel():
    connection = BlockingConnection(ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='position')
    channel.queue_declare(queue='input')
    return channel

def main_loop(channel, rect, config):
    while True:
        command = get_input(channel)
        if command:
            rect = do(command, rect)
        sleep(config['tick'])

def do(command, rect):
    delta = config['deltas'].get(command)
    if not delta:
        return rect
    new_rect = rect.move(delta)
    if new_rect.in_rect(config['field_rect']):
        send_position(new_rect.top_left, channel)
        return new_rect
    else:
        return rect

def send_position(position, channel):
    pair = position.to_pair()
    channel.basic_publish(exchange='',
                          routing_key='position',
                          body=dumps(pair))

def get_input(channel):
    message = channel.basic_get(0, 'input', no_ack=True)[2]
    if message:
        return loads(message)
    else:
        return None

channel, rect, config = init()
main_loop(channel, rect, config)
