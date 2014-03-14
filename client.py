from alexandra import Alexandra
from json import dumps
from pygame import display, event, init, key, quit
from pygame.image import load
from pygame.locals import KEYDOWN, K_DOWN, K_LEFT, K_RIGHT, K_UP, QUIT
from StringIO import StringIO
from sys import exit

def init_window(field_width, field_height):
    init()
    window = display.set_mode((field_width, field_height), 0)
    display.set_caption('Alexandra')
    return window

def update(window, alex):
    do_world_update(window, alex)
    command = get_command()
    if command is not None:
        alex.publish('commands.player', command)
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
def do_world_update(window, alex):
    window.fill(BLACK)
    updater = lambda(e): do_entity_update(e, window, alex)
    map(updater, alex.world['entities'].values())
    display.flip()

def do_entity_update(entity_data, window, alex):
    entity, position = entity_data['entity'], entity_data['position']
    image_path = '/%s/%s.png' % (entity, entity)
    image = load(StringIO(alex.get_library_file(image_path)))
    window.blit(image, position)

alex = Alexandra()
window = init_window(alex.config['field_width'], alex.config['field_height'])
alex.on_each_tick(lambda(x): update(window, x))
alex.wait()
