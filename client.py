from json import dumps, load, loads
from pubsub import create_channel, publish, subscribe, unsubscribe, \
                   get_message, get_message_block
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
            'library_url': library_url}

def init_window(field_width, field_height):
    init()
    window = display.set_mode((field_width, field_height), 0)
    display.set_caption('Alexandra')
    return window

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
    window.fill(BLACK)
    do_player_update(window, world, library_url)
    do_wall_update(window, world, library_url)
    display.flip()

def do_player_update(window, world, library_url):
    if 'player_0' not in world:
        return
    image = get_image(library_url + '/player/player.png')
    new_position = world['player_0']['position']
    window.blit(image, new_position)

def do_wall_update(window, world, library_url):
    if 'wall_horizontal_0' not in world and \
       'wall_vertical_0' not in world:
        return

    h_image = get_image(library_url + '/wall_horizontal/wall_horizontal.png')
    v_image = get_image(library_url + '/wall_vertical/wall_vertical.png')

    for wall_name in filter(lambda(x): x.startswith('wall'), world.keys()):
        if world[wall_name]['entity'] == 'wall_horizontal':
            image = h_image
        else:
            image = v_image
        position = world[wall_name]['position']
        window.blit(image, position)

def get_image(url):
    data = StringIO(urlopen(url).read())
    return imageload(data)

def main_loop(window, channel, world_queue, library_url):
    while True:
        world = loads(get_message_block(channel, world_queue))
        do_world_update(window, world, library_url)
        command = get_command()
        if command is not None:
            send_command(command, channel)
        check_quit()

channel = create_channel()
config = init_config(channel)
world_queue = subscribe(channel, 'world')
window = init_window(config['field_width'], config['field_height'])
main_loop(window, channel, world_queue, config['library_url'])
