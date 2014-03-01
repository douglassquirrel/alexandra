from json import dumps, loads
from pika import BlockingConnection, ConnectionParameters
from time import sleep

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

FIELD_RECT = Rect(Vector(0, 0), Vector(400, 400))
START = Vector(30, 30)
WIDTH = 50
HEIGHT = 50
TICK = 0.02
deltas = {'left': Vector(-5, 0), 'right': Vector(5, 0),
          'up': Vector(0, -5), 'down': Vector(0, 5)}

def init():
    connection = BlockingConnection(ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='position')
    channel.queue_declare(queue='input')

    rect = Rect(START, START.add(Vector(WIDTH, HEIGHT)))
    send_position(rect.top_left, channel)

    return channel, rect

def main_loop(channel, rect):
    while True:
        command = get_input(channel)
        if command:
            rect = do(command, rect)
        sleep(TICK)

def do(command, rect):
    delta = deltas.get(command)
    if not delta:
        return rect
    new_rect = rect.move(delta)
    if new_rect.in_rect(FIELD_RECT):
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

channel, rect = init()
main_loop(channel, rect)
