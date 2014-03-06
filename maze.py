# Depth-first maze generation from
# http://www.mazeworks.com/mazegen/mazetut/index.htm

from random import choice as random_choice
from sys import stdout

def make_maze(width, height):
    walls = all_walls(width, height)
    stack = []
    number_of_cells = width*height
    current_cell = (0, 0)
    cells_visited = 1
    while cells_visited < number_of_cells:
        neighbours = get_neighbours(current_cell, width, height)
        intact_neighbours = []
        for neighbour in neighbours:
            if is_intact(neighbour, walls):
                intact_neighbours.append(neighbour)
        if len(intact_neighbours) > 0:
            next_cell = random_choice(intact_neighbours)
            wall = wall_between(current_cell, next_cell)
            walls.remove(wall)
            stack.append(current_cell)
            current_cell = next_cell
            cells_visited += 1
        else:
            current_cell = stack.pop()
    print_maze(width, height, walls)

def is_valid_cell(cell, width, height):
    x, y = cell[0], cell[1]
    return x>=0 and y>=0 and x<width and y<height

def get_neighbours(cell, width, height):
    x, y = cell[0], cell[1]
    candidates = [(x-1, y), (x, y-1), (x+1, y), (x, y+1)]
    neighbours = []
    for cell in candidates:
        if is_valid_cell(cell, width, height):
            neighbours.append(cell)
    return neighbours

def is_intact(cell, walls):
    x, y = cell[0], cell[1]
    return (x,y,x+1,y) in walls \
       and (x,y,x,y+1) in walls \
       and (x,y+1,x+1,y+1) in walls \
       and (x+1,y,x+1,y+1) in walls

def wall_between(cell_1, cell_2):
    x1, y1 = cell_1[0], cell_1[1]
    x2, y2 = cell_2[0], cell_2[1]
    if x1 > x2 or y1 > y2:
        return wall_between(cell_2, cell_1)
    if x1 == x2:
        return (x2,y2,x2+1,y2)
    else:
        return (x2,y2,x2,y2+1)

def all_walls(width, height):
    walls = []
    for x in range(0, width+1):
        for y in range(0, height+1):
            if x < width:
                walls.append((x,y,x+1,y))
            if y < height:
                walls.append((x,y,x,y+1))
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

make_maze(10, 8)
