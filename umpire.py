from json import dumps, load, loads
from pubsub import create_channel, publish, subscribe, unsubscribe, get_message
from time import sleep
from sys import exit
from urllib2 import URLError, urlopen

def init():
    channel = create_channel()
    config = init_config(channel)
    movement_queue = subscribe(channel, 'movement_with_collisions.*')

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

    return {'library_url': library_url,
            'tick': config['tick_seconds']}

def main_loop(channel, movement_queue, library_url, tick):
    while True:
        message = get_message(channel, movement_queue)
        if message is not None:
            filter_movement(loads(message), library_url)
        sleep(tick/5.0)

def filter_movement(movement, library_url):
    entity = movement['entity']
    from_position, to_position = movement['from'], movement['to']

    if entity != 'player' or len(movement['collisions']) == 0:
        new_position = to_position
    else:
        new_position = from_position

    approved_movement = {'entity': entity,
                         'index': movement['index'],
                         'from': from_position, 'to': new_position}
    publish(channel, 'decision.movement.' + entity,
            dumps(approved_movement))

channel, movement_queue, config = init()
main_loop(channel, movement_queue, config['library_url'], config['tick'])
