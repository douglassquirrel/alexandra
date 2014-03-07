from json import dumps, load, loads
from pubsub import create_channel, publish, subscribe, unsubscribe, \
                   get_message, get_message_block
from maze import make_maze
from time import sleep
from sys import exit
from urllib2 import build_opener, HTTPHandler, Request, URLError, urlopen

IMAGE_FILE = 'wall.png'

def init():
    channel = create_channel()
    config = init_config(channel)
    publish_image(config['library_url'], IMAGE_FILE)
    world_queue = subscribe(channel, 'world')

    return channel, world_queue, config

def init_config(channel):
    queue = subscribe(channel, 'library_url')
    sleep(1)
    library_url = get_message(channel, queue)
    if library_url is None:
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
            'cell_width': 80,
            'library_url': library_url}

def draw_maze(walls, cell_width):
    for index, wall in enumerate(walls):
        position = (wall[0] * cell_width, wall[1] * cell_width)
        if wall[1] == wall[3]:
            rotation = 0
        else:
            rotation = -90
        send_movement(position, rotation, index, channel)

def publish_image(library_url, image_file):
    image_data = open(image_file).read()
    opener = build_opener(HTTPHandler)
    request = Request(library_url + '/wall/' + image_file, image_data)
    request.add_header('Content-Type', 'image/png')
    request.get_method = lambda: 'PUT'
    opener.open(request)

def main_loop(channel, world_queue):
    while True:
        world = loads(get_message_block(channel, world_queue))
        pass

def send_movement(position, rotation, index, channel):
    name = 'wall_%d' % (index,)
    movement = {'entity': name, 'from': position, 'to': position,
                'from_rotation': rotation, 'to_rotation': rotation}
    publish(channel, 'movement.' + name, dumps(movement))

channel, world_queue, config = init()
walls = make_maze(config['field_width']/config['cell_width'],
                  config['field_height']/config['cell_width'])
draw_maze(walls, config['cell_width'])
main_loop(channel, world_queue)
