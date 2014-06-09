#! /usr/bin/python

from alexandra import Alexandra, request_game
from docstore import connect as docstore_connect
from json import loads
from pygame import display, event, init, key, quit, Surface, surfarray
from pygame.locals import KEYDOWN, K_DOWN, K_LEFT, K_RIGHT, K_UP, QUIT
from StringIO import StringIO
from sys import argv, exit
from time import time as now
from uuid import uuid4

def init_window(field_width, field_height):
    init()
    window = display.set_mode((field_width, field_height), 0)
    display.set_caption('Alexandra')
    return window

def update(window, world, alex):
    alex.pubsub.publish('heartbeat', now())
    do_world_update(window, world, alex)
    command = get_command()
    if command is not None:
        alex.pubsub.publish('commands.player', command)
    check_quit()

def check_quit():
    if len([e for e in event.get() if e.type == QUIT]) > 0:
        quit()
        exit()

command_dict = {K_DOWN: 'down', K_LEFT: 'left', K_RIGHT: 'right', K_UP: 'up'}
known_keys = set(command_dict.keys())
def get_command():
    key_states = enumerate(key.get_pressed())
    pressed_keys = set([x for (x,y) in key_states if y != 0])
    known_pressed_keys = pressed_keys.intersection(known_keys)
    if len(known_pressed_keys) > 0:
        selected_key = sorted(list(known_pressed_keys))[0]
        return command_dict[selected_key]
    else:
        return None

BLACK = (0, 0, 0)
def do_world_update(window, world, alex):
    window.fill(BLACK)
    updater = lambda(e): do_entity_update(e, window, alex)
    map(updater, world['entities'].values())
    display.flip()

def do_entity_update(entity_data, window, alex):
    entity, position = entity_data['entity'], entity_data['position']
    entity_topic = '%s/%s.json' % (entity, entity)
    entity_data = alex.pubsub.get_current_message(entity_topic)
    width, height = entity_data['width'], entity_data['height']
    colour = list(entity_data['colour'])
    draw_rectangle(width, height, colour, position, window)

def draw_rectangle(width, height, colour, position, window):
    rectangle = Surface((width, height))
    pixels = surfarray.pixels3d(rectangle)
    pixels[:][:] = colour
    del pixels
    rectangle.unlock()
    window.blit(rectangle, position)

docstore_url, game_name = argv[1], argv[2]
game_id = str(uuid4())
print "Starting client for game %s with id %s" % (game_name, game_id)

pubsub_url = docstore_connect(docstore_url).get('/services/pubsub')
if request_game(game_name, game_id, pubsub_url) is False:
    print "Could not start game"
    exit(1)

alex = Alexandra(docstore_url, game_id)
window = init_window(alex.config['field_width'], alex.config['field_height'])
alex.pubsub.consume_topic('world', lambda w: update(window, w, alex))
