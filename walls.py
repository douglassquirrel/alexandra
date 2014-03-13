from alexandra import Alexandra
from json import dumps
from maze import make_maze

H_IMAGE_FILE = 'wall_horizontal.png'
H_WIDTH = 80
H_HEIGHT = 3
V_IMAGE_FILE = 'wall_vertical.png'
V_WIDTH = 3
V_HEIGHT = 80
CELL_WIDTH = 80

def init(alex):
    alex.enter_in_library(open(H_IMAGE_FILE).read(),
                          '/wall_horizontal/' + H_IMAGE_FILE,
                          'image/png')
    alex.enter_in_library(open(V_IMAGE_FILE).read(),
                          '/wall_vertical/' + V_IMAGE_FILE,
                          'image/png')
    alex.enter_in_library(dumps({'width': H_WIDTH, 'height': H_HEIGHT}),
                          '/wall_horizontal/wall_horizontal.json',
                          'application/json')
    alex.enter_in_library(dumps({'width': V_WIDTH, 'height': V_HEIGHT}),
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

def main_loop(alex):
    alex.each_tick(lambda(x): None)

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
draw_maze(walls, alex)
main_loop(alex)
