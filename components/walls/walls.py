#! /usr/bin/python

from alexandra import Alexandra
from json import dumps
from maze import make_maze

H_WIDTH = 80
H_HEIGHT = 3
V_WIDTH = 3
V_HEIGHT = 80
COLOUR = [0, 50, 200]
CELL_WIDTH = 80

def init(alex):
    alex.enter_in_library(dumps({'width': H_WIDTH, 'height': H_HEIGHT,
                                 'colour': COLOUR}),
                          '/wall_horizontal/wall_horizontal.json',
                          'application/json')
    alex.enter_in_library(dumps({'width': V_WIDTH, 'height': V_HEIGHT,
                                 'colour': COLOUR}),
                          '/wall_vertical/wall_vertical.json',
                          'application/json')

def draw_maze(walls, alex):
    map(lambda(x): draw_wall(x[0], x[1], alex), enumerate(walls))

def draw_wall(index, wall, alex):
    position = (wall[0] * CELL_WIDTH, wall[1] * CELL_WIDTH)
    send_movement(position, orientation(wall), index, alex)

def orientation(wall):
    if wall[1] == wall[3]:
        return 'horizontal'
    else:
        return 'vertical'

def draw_if_absent(walls, alex):
    walls_in_world = filter(lambda(e): e.startswith('wall_'),
                            alex.world['entities'].keys())
    if len(walls_in_world) == 0:
        draw_maze(walls, alex)

def send_movement(position, orientation, index, alex):
    entity = 'wall_%s' % orientation
    name = '%s_%d' % (entity, index,)
    movement = {'entity': entity, 'index': index,
                'from': position, 'to': position}
    alex.publish('movement.' + name, movement)

alex = Alexandra()
init(alex)
walls = make_maze(alex.config['field_width']/CELL_WIDTH,
                  alex.config['field_height']/CELL_WIDTH)
alex.on_each_tick(lambda(x): draw_if_absent(walls, x))
alex.wait()
