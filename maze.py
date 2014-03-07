# Depth-first maze generation from
# http://www.mazeworks.com/mazegen/mazetut/index.htm

from random import choice as random_choice
from sys import argv, stdout

def make_maze(width, height):
    walls = _all_walls(width, height)
    stack = []
    current_cell = (0, 0)
    cells_visited = 1
    while cells_visited < width*height:
        intact_neighbours = filter(lambda(x): _is_intact(x, walls),
                                   _get_neighbours(current_cell, width, height))
        if len(intact_neighbours) > 0:
            next_cell = random_choice(intact_neighbours)
            walls.remove(_wall_between(current_cell, next_cell))
            stack.append(current_cell)
            current_cell = next_cell
            cells_visited += 1
        else:
            current_cell = stack.pop()
    return walls

def _is_valid_cell(cell, width, height):
    return cell[0]>=0 and cell[1]>=0 and cell[0]<width and cell[1]<height

def _get_neighbours(cell, width, height):
    return filter(lambda(x): _is_valid_cell(x, width, height),
                  set([_above(cell), _below(cell), _left(cell), _right(cell)]))

def _is_intact(cell, walls):
    return _walls_of(cell).issubset(walls)

def _above(cell):
    return (cell[0], cell[1] - 1)
def _left(cell):
    return (cell[0] - 1, cell[1])
def _below(cell):
    return (cell[0], cell[1] + 1)
def _right(cell):
    return (cell[0] + 1, cell[1])

def _top_wall(cell):
    return (cell[0], cell[1], cell[0]+1, cell[1])
def _bottom_wall(cell):
    return (cell[0], cell[1]+1, cell[0]+1, cell[1]+1)
def _left_wall(cell):
    return (cell[0], cell[1], cell[0], cell[1]+1)
def _right_wall(cell):
    return (cell[0]+1, cell[1], cell[0]+1, cell[1]+1)

def _walls_of(cell):
    return set([_top_wall(cell), _bottom_wall(cell),
                _left_wall(cell), _right_wall(cell)])

def _wall_between(cell_1, cell_2):
    common_walls = _walls_of(cell_1).intersection(_walls_of(cell_2))
    return common_walls.pop()

def _all_walls(width, height):
    walls = set()
    for x in range(0, width ):
        for y in range(0, height):
            walls.update(_walls_of((x,y)))
    return walls

def _print_maze(width, height, walls):
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

if __name__ == "__main__":
    width, height = int(argv[1]), int(argv[2])
    walls = make_maze(width, height)
    _print_maze(width, height, walls)
