#! /usr/bin/env python

from alexandra import Alexandra
from json import dumps
from maze import make_maze
from sys import argv

H_WIDTH = 80
H_HEIGHT = 3
V_WIDTH = 3
V_HEIGHT = 80
COLOUR = [0, 50, 200]
CELL_WIDTH = 80

def init(alex):
    alex.pubsub.publish('wall_horizontal/wall_horizontal.json',
                        {'width': H_WIDTH, 'height': H_HEIGHT,
                         'colour': COLOUR})
    alex.pubsub.publish('wall_vertical/wall_vertical.json',
                        {'width': V_WIDTH, 'height': V_HEIGHT,
                         'colour': COLOUR})

def draw_wall(index, wall, tick, alex):
    position = (wall[0] * CELL_WIDTH, wall[1] * CELL_WIDTH)
    send_movement(position, orientation(wall), index, tick, alex)

def orientation(wall):
    if wall[1] == wall[3]:
        return 'horizontal'
    else:
        return 'vertical'

def draw(walls, world, alex):
    number_of_walls = len(walls)
    walls_in_world = filter(lambda(e): e.startswith('wall_'),
                            world['entities'].keys())
    if len(walls_in_world) >= number_of_walls:
        return
    in_world = sorted(map(lambda(w): int(w.partition('al_')[2]),
                          walls_in_world))
    indexes = [i for i in range(number_of_walls) if i not in in_world][0:10]
    for index in indexes:
        draw_wall(index, walls[index], world['tick'], alex)

def send_movement(position, orientation, index, tick, alex):
    entity = 'wall_%s' % orientation
    name = '%s_%d' % (entity, index,)
    movement = {'tick': tick,
                'entity': entity, 'index': index,
                'from': position, 'to': position}
    alex.pubsub.publish('movement.' + name, movement)

alex = Alexandra(argv[1])
init(alex)
walls = list(make_maze(alex.config['field_width']/CELL_WIDTH,
                       alex.config['field_height']/CELL_WIDTH))
alex.pubsub.consume_topic('world', lambda w: draw(walls, w, alex))
