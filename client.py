from json import dumps, load, loads
from pubsub import create_channel, publish, subscribe, unsubscribe, get_message
from pygame import display, draw, event, init, key, quit, Rect
from pygame.image import load as imageload
from pygame.locals import KEYDOWN, K_DOWN, K_LEFT, K_RIGHT, K_UP, QUIT
from StringIO import StringIO
from sys import exit
from time import sleep
from urllib2 import URLError, urlopen

BLACK = (0, 0, 0)

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
    return {'field_width': config['field_width'],
            'field_height': config['field_height'],
            'library_url': library_url,
            'tick': config['tick_seconds']}

def init_window(field_width, field_height):
    init()
    window = display.set_mode((field_width, field_height), 0)
    display.set_caption('Alexandra')
    return window

def get_world_update(channel, world_queue):
    message = get_message(channel, world_queue)
    if message is not None:
        return loads(message)
    else:
        return None

def check_quit():
    for e in event.get():
        if e.type == QUIT:
            quit()
            exit()

input_keys = {K_DOWN: 'down', K_LEFT: 'left', K_RIGHT: 'right', K_UP: 'up'}
def get_command():
    keyState = key.get_pressed()
    for k in input_keys.keys():
        if keyState[k]:
            return input_keys[k]
    return None

def send_command(command, channel):
    publish(channel, 'commands.player', dumps(command))

def do_world_update(window, world, library_url):
    new_position = world['player']
    image_url = library_url + '/player/player_image.png'
    image_data = StringIO(urlopen(image_url).read())
    image = imageload(image_data)
    window.fill(BLACK)
    window.blit(image, new_position)
    display.flip()

def main_loop(window, channel, world_queue, library_url, tick):
    while True:
        world = get_world_update(channel, world_queue)
        if world is not None:
            do_world_update(window, world, library_url)
        command = get_command()
        if command is not None:
            send_command(command, channel)
        check_quit()
        sleep(tick)

channel = create_channel()
config = init_config(channel)
world_queue = subscribe(channel, 'world')
window = init_window(config['field_width'], config['field_height'])
main_loop(window, channel, world_queue,
          config['library_url'], config['tick'])
