# Depth-first maze generation from
# http://www.mazeworks.com/mazegen/mazetut/index.htm

from random import choice as random_choice
from sys import stdout

def make_maze(width, height):
    walls = all_walls(width, height)
    stack = []
    current_cell = (0, 0)
    cells_visited = 1
    while cells_visited < width*height:
        intact_neighbours = filter(lambda(x): is_intact(x, walls),
                                   get_neighbours(current_cell, width, height))
        if len(intact_neighbours) > 0:
            next_cell = random_choice(intact_neighbours)
            walls.remove(wall_between(current_cell, next_cell))
            stack.append(current_cell)
            current_cell = next_cell
            cells_visited += 1
        else:
            current_cell = stack.pop()
    return walls

def is_valid_cell(cell, width, height):
    return cell[0]>=0 and cell[1]>=0 and cell[0]<width and cell[1]<height

def get_neighbours(cell, width, height):
    return filter(lambda(x): is_valid_cell(x, width, height),
                  set([above(cell), below(cell), left(cell), right(cell)]))

def is_intact(cell, walls):
    return walls_of(cell).issubset(walls)

def above(cell):
    return (cell[0], cell[1] - 1)
def left(cell):
    return (cell[0] - 1, cell[1])
def below(cell):
    return (cell[0], cell[1] + 1)
def right(cell):
    return (cell[0] + 1, cell[1])

def top_wall(cell):
    return (cell[0], cell[1], cell[0]+1, cell[1])
def bottom_wall(cell):
    return (cell[0], cell[1]+1, cell[0]+1, cell[1]+1)
def left_wall(cell):
    return (cell[0], cell[1], cell[0], cell[1]+1)
def right_wall(cell):
    return (cell[0]+1, cell[1], cell[0]+1, cell[1]+1)

def walls_of(cell):
    return set([top_wall(cell), bottom_wall(cell),
                left_wall(cell), right_wall(cell)])

def wall_between(cell_1, cell_2):
    common_walls = walls_of(cell_1).intersection(walls_of(cell_2))
    return common_walls.pop()

def all_walls(width, height):
    walls = set()
    for x in range(0, width ):
        for y in range(0, height):
            walls.update(walls_of((x,y)))
    return walls

def print_maze(width, height, walls):
    for y in range(0, height+1):
        for x in range(0, width+1):
            if (x,y-1,x,y) in walls:
                stdout.write('|')
            else:
                stdout.write(' ')
            if (x,y,x+1,y) in walls:
                stdout.write('_')
            else:
                stdout.write(' ')
        stdout.write('\n')
