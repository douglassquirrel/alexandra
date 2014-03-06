from json import dumps, load, loads
from pubsub import create_channel, publish, subscribe, unsubscribe, \
                   get_message, get_message_block
from time import sleep
from sys import exit
from urllib2 import build_opener, HTTPHandler, Request, URLError, urlopen

IMAGE_FILE = 'player_image.png'

def init():
    channel = create_channel()
    config = init_config(channel)
    publish_image(config['library_url'])
    position = (config['start_x'], config['start_y'])
    send_movement(position, position, channel)
    commands_queue = subscribe(channel, 'commands.player')
    world_queue = subscribe(channel, 'world')

    return channel, commands_queue, world_queue, position, config

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

    return {'start_x': config['player_start_x'],
            'start_y': config['player_start_y'],
            'width': 50,
            'height': 50,
            'library_url': library_url,
            'deltas': {'left': (-5, 0), 'right': (5, 0),
                       'up': (0, -5), 'down': (0, 5)}}

def publish_image(library_url):
    image_data = open(IMAGE_FILE).read()
    opener = build_opener(HTTPHandler)
    request = Request(library_url + '/player/player_image.png', image_data)
    request.add_header('Content-Type', 'image/png')
    request.get_method = lambda: 'PUT'
    opener.open(request)

def main_loop(channel, commands_queue, world_queue, position, deltas):
    while True:
        world = loads(get_message_block(channel, world_queue))
        if 'player' not in world:
            continue
        position = world['player']
        command = get_input(channel, commands_queue)
        if command is not None:
            do(command, position, deltas)

def do(command, position, deltas):
    delta = deltas.get(command)
    if delta is None:
        return position
    new_position = (position[0] + delta[0], position[1] + delta[1])
    send_movement(position, new_position, channel)

def send_movement(from_position, to_position, channel):
    movement = {'entity': 'player', 'from': from_position, 'to': to_position}
    publish(channel, 'movement.player', dumps(movement))

def get_input(channel, commands_queue):
    message = get_message(channel, commands_queue)
    if message is not None:
        return loads(message)
    else:
        return None

channel, commands_queue, world_queue, position, config = init()
main_loop(channel, commands_queue, world_queue,
          position, config['deltas'])
