from json import dumps, load, loads
from pubsub import create_channel, publish, subscribe, unsubscribe, \
                   get_message, get_message_block
from maze import make_maze
from time import sleep
from sys import exit
from urllib2 import build_opener, HTTPHandler, Request, URLError, urlopen

H_IMAGE_FILE = 'wall_horizontal.png'
H_WIDTH = 80
H_HEIGHT = 3
V_IMAGE_FILE = 'wall_vertical.png'
V_WIDTH = 3
V_HEIGHT = 80

def init():
    channel = create_channel()
    config = init_config(channel)
    publish_info(config['library_url'])
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
            orientation = 'horizontal'
        else:
            orientation = 'vertical'
        send_movement(position, orientation, index, channel)

def publish_info(library_url):
    publish_to_url(open(H_IMAGE_FILE).read(),
                   library_url + '/wall_horizontal/' + H_IMAGE_FILE,
                   'image/png')
    publish_to_url(open(V_IMAGE_FILE).read(),
                   library_url + '/wall_vertical/' + V_IMAGE_FILE,
                   'image/png')
    publish_to_url(dumps({'width': H_WIDTH, 'height': H_HEIGHT}),
                   library_url + '/wall_horizontal/wall_horizontal.json',
                   'application/json')
    publish_to_url(dumps({'width': V_WIDTH, 'height': V_HEIGHT}),
                   library_url + '/wall_vertical/wall_vertical.json',
                   'application/json')

def publish_to_url(data, url, content_type):
    opener = build_opener(HTTPHandler)
    request = Request(url, data)
    request.add_header('Content-Type', content_type)
    request.get_method = lambda: 'PUT'
    opener.open(request)

def main_loop(channel, world_queue):
    while True:
        world = loads(get_message_block(channel, world_queue))
        pass

def send_movement(position, orientation, index, channel):
    entity = 'wall_%s' % orientation
    name = '%s_%d' % (entity, index,)
    movement = {'entity': entity, 'index': index,
                'from': position, 'to': position}
    publish(channel, 'movement.' + name, dumps(movement))

channel, world_queue, config = init()
walls = make_maze(config['field_width']/config['cell_width'],
                  config['field_height']/config['cell_width'])
draw_maze(walls, config['cell_width'])
main_loop(channel, world_queue)
