from alexandra import Alexandra
from json import dumps
from time import sleep

IMAGE_FILE = 'player_image.png'
WIDTH = 50
HEIGHT = 50
DELTAS = {'left': (-5, 0), 'right': (5, 0), 'up': (0, -5), 'down': (0, 5)}

def init(alex):
    alex.enter_in_library(open(IMAGE_FILE).read(),
                          '/player/player.png', 'image/png')
    alex.enter_in_library(dumps({'width': WIDTH, 'height': HEIGHT}),
                          '/player/player.json', 'application/json')
    position = (alex.config['player_start_x'], alex.config['player_start_y'])
    send_movement(position, position, alex)
    commands_queue = alex.subscribe('commands.player')

    return commands_queue, position

def main_loop(commands_queue, position, alex):
    while True:
        command = commands_queue.next()
        if command is not None and 'player_0' in alex.world:
            position = alex.world['player_0']['position']
            do(command, position, alex)
        sleep(alex.config['tick_seconds']/5.0)

def do(command, position, alex):
    delta = DELTAS.get(command)
    if delta is None:
        return position
    new_position = (position[0] + delta[0], position[1] + delta[1])
    send_movement(position, new_position, alex)

def send_movement(from_position, to_position, alex):
    movement = {'entity': 'player', 'index': 0,
                'from': from_position, 'to': to_position}
    alex.publish('movement.player', movement)

alex = Alexandra(subscribe_world=True)
commands_queue, position = init(alex)
main_loop(commands_queue, position, alex)
