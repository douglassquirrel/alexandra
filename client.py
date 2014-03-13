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

BLACK = (0, 0, 0)
def do_world_update(window, alex):
    window.fill(BLACK)
    do_player_update(window, alex)
    do_wall_update(window, alex)
    display.flip()

def do_player_update(window, alex):
    if 'player_0' not in alex.world['entities']:
        return
    image = load(StringIO(alex.get_library_file('/player/player.png')))
    new_position = alex.world['entities']['player_0']['position']
    window.blit(image, new_position)

def do_wall_update(window, alex):
    if 'wall_horizontal_0' not in alex.world['entities'] and \
       'wall_vertical_0' not in alex.world['entities']:
        return

    h_image_path = '/wall_horizontal/wall_horizontal.png'
    v_image_path = '/wall_vertical/wall_vertical.png'
    h_image = load(StringIO(alex.get_library_file(h_image_path)))
    v_image = load(StringIO(alex.get_library_file(v_image_path)))

    entities = alex.world['entities']
    for wall_name in filter(lambda(x): x.startswith('wall'), entities.keys()):
        if entities[wall_name]['entity'] == 'wall_horizontal':
            image = h_image
        else:
            image = v_image
        position = entities[wall_name]['position']
        window.blit(image, position)

def main_loop(window, alex):
    alex.each_tick(lambda(x): update(window, x))

def update(window, alex):
    do_world_update(window, alex)
    command = get_command()
    if command is not None:
        alex.publish('commands.player', command)
    check_quit()

alex = Alexandra()
window = init_window(alex.config['field_width'], alex.config['field_height'])
main_loop(window, alex)
