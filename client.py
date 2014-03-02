from json import dumps, load, loads
from pika import BlockingConnection, ConnectionParameters
from pygame import display, draw, event, init, key, quit, Rect
from pygame.locals import KEYDOWN, K_DOWN, K_LEFT, K_RIGHT, K_UP, QUIT
from sys import exit
from time import sleep
from urllib2 import URLError, urlopen

BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

def init_channel():
    connection = BlockingConnection(ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='position')
    channel.queue_declare(queue='input')
    return channel

def init_config(channel):
    channel.queue_declare(queue='library_url')
    sleep(1)
    library_url = channel.basic_get(0, 'library_url', no_ack=True)[2]
    if not library_url:
        print "No library url published, cannot fetch config - exiting client"
        exit(1)

    config_url = library_url + '/config.json'
    try:
        config_file = urlopen(config_url)
    except URLError:
        print "No config file at %s - exiting player" % (config_url,)
        exit(1)
    config = load(config_file)
    return {'field_width': config['field_width'],
            'field_height': config['field_height'],
            'tick': config['tick_seconds']}

def init_window(config):
    init()
    field_size = (config['field_width'], config['field_height'])
    window = display.set_mode(field_size, 0, 32)
    display.set_caption('Alexandra')
    return window

def get_position_update(channel):
    message = channel.basic_get(0, 'position', no_ack=True)[2]
    if message:
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

def do_position_update(window, new_position):
    x, y = new_position
    window.fill(BLACK)
    draw.rect(window, YELLOW, Rect(x, y, 50, 50))
    display.update()

def main_loop(window, channel, config):
    while True:
        new_position = get_position_update(channel)
        if new_position:
            do_position_update(window, new_position)
        input_list = get_input()
        for input in input_list:
            send_input(input, channel)
        check_quit()
        sleep(config['tick'])

channel = init_channel()
config = init_config(channel)
main_loop(init_window(config), channel, config)
