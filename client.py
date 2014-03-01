from json import dumps, loads
from pika import BlockingConnection, ConnectionParameters
from pygame import display, draw, event, init, key, quit, Rect
from pygame.locals import KEYDOWN, K_DOWN, K_LEFT, K_RIGHT, K_UP, QUIT
from sys import exit
from time import sleep

BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
TICK = 0.02

def init_window():
    init()
    window = display.set_mode((400, 400), 0, 32)
    display.set_caption('Alexandra')
    return window

def init_channel():
    connection = BlockingConnection(ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='position')
    channel.queue_declare(queue='input')
    return channel

def get_position_update(channel):
    message = channel.basic_get(0, 'position', no_ack=True)[2]
    if message:
        print "Received %s" % (message,)
        return loads(message)[0:2]
    else:
        return None

def check_quit():
    for e in event.get():
        if e.type == QUIT:
            quit()
            exit()

commands = {K_DOWN: 'down', K_LEFT: 'left', K_RIGHT: 'right', K_UP: 'up'}
def get_input():
    input = []
    keyState = key.get_pressed()
    for command in commands.keys():
        if keyState[command]:
            input.append(commands[command])
    return input

def send_input(input, channel):
    channel.basic_publish(exchange='',
                          routing_key='input',
                          body=dumps(input))
    print "Sent %s" % (input,)

def do_position_update(window, new_position):
    x, y = new_position
    window.fill(BLACK)
    draw.rect(window, YELLOW, Rect(x, y, 50, 50))
    display.update()

def main_loop(window, channel):
    while True:
        new_position = get_position_update(channel)
        if new_position:
            do_position_update(window, new_position)
        input_list = get_input()
        for input in input_list:
            send_input(input, channel)
        check_quit()
        sleep(TICK)

main_loop(init_window(), init_channel())
